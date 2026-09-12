from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

from Bio.Seq import Seq


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fastq_record(name: str, sequence: str) -> str:
    return f"@{name}\n{sequence}\n+\n{'I' * len(sequence)}\n"


def substitute_base(sequence: str, position: int) -> str:
    alternatives = {"A": "C", "C": "G", "G": "T", "T": "A"}
    return sequence[:position] + alternatives[sequence[position]] + sequence[position + 1 :]


def generate_fixture(
    reference_path: Path,
    output_dir: Path,
    *,
    insertion_after_zero_based: int = 92,
    itd_sequence: str = "TTGATTTCAGAGAATATGAAT",
    fragment_count: int = 200,
    variant_fraction: float = 0.6,
    read_length: int = 251,
    seed: int = 20260912,
) -> dict:
    reference = "".join(reference_path.read_text(encoding="utf-8").split()).upper()
    if not 0 < variant_fraction < 1:
        raise ValueError("variant_fraction must be between 0 and 1")
    if read_length > len(reference):
        raise ValueError("read_length cannot exceed the reference length")
    expected_tandem = reference[
        insertion_after_zero_based - len(itd_sequence) : insertion_after_zero_based
    ]
    if expected_tandem != itd_sequence:
        raise ValueError("ITD sequence is not the tandem immediately before insertion")

    mutant = (
        reference[:insertion_after_zero_based]
        + itd_sequence
        + reference[insertion_after_zero_based:]
    )
    variant_count = round(fragment_count * variant_fraction)
    labels = [True] * variant_count + [False] * (fragment_count - variant_count)
    random.Random(seed).shuffle(labels)

    output_dir.mkdir(parents=True, exist_ok=True)
    r1_path = output_dir / "FLT3-ITD-DEMO-001_R1.fastq"
    r2_path = output_dir / "FLT3-ITD-DEMO-001_R2.fastq"
    with r1_path.open("w", encoding="ascii", newline="\n") as r1, r2_path.open(
        "w", encoding="ascii", newline="\n"
    ) as r2:
        variant_seen = 0
        noise_positions = (140, 145, 150, 155)
        for index, is_variant in enumerate(labels, start=1):
            template = mutant if is_variant else reference
            if is_variant:
                # Model deterministic sequencing diversity outside the ITD and
                # primers so getITD's unique-read support filter is exercised.
                template = substitute_base(
                    template, noise_positions[variant_seen % len(noise_positions)]
                )
                variant_seen += 1
            pair_name = f"ITDCARRY:{index:06d}:{'VAR' if is_variant else 'WT'}"
            r1.write(fastq_record(f"{pair_name}/1", template[:read_length]))
            r2_sequence = str(Seq(template[-read_length:]).reverse_complement())
            r2.write(fastq_record(f"{pair_name}/2", r2_sequence))

    manifest = {
        "fixture_id": "FLT3-ITD-DEMO-001",
        "fixture_class": "deterministic_synthetic_amplicon_reads",
        "synthetic": True,
        "clinical_use": False,
        "reference_source": "getITD v1.5.17 bundled FLT3 amplicon reference",
        "reference_path": str(reference_path.as_posix()),
        "reference_sha256": sha256(reference_path),
        "coordinate_system": "getITD one-based amplicon start",
        "itd_position": insertion_after_zero_based - len(itd_sequence) + 1,
        "itd_sequence": itd_sequence,
        "itd_length_bp": len(itd_sequence),
        "read_length_bp": read_length,
        "paired_end": True,
        "random_seed": seed,
        "fragment_count": fragment_count,
        "intended_variant_fragment_fraction": variant_count / fragment_count,
        "observed_variant_fragment_fraction": sum(labels) / len(labels),
        "deterministic_noise": {
            "type": "single_base_substitution",
            "mutant_template_positions_zero_based": list(noise_positions),
            "purpose": "Model unique sequencing reads outside the ITD and primer regions"
        },
        "r1_sha256": sha256(r1_path),
        "r2_sha256": sha256(r2_path),
        "generator": "pipeline/generate_reads.py",
        "limitations": [
            "Synthetic computational challenge only",
            "No biological or clinical conclusion",
            "Intended fragment fraction is not a validated clinical VAF",
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fragments", type=int, default=200)
    parser.add_argument("--variant-fraction", type=float, default=0.6)
    parser.add_argument("--seed", type=int, default=20260912)
    args = parser.parse_args()
    manifest = generate_fixture(
        args.reference,
        args.output,
        fragment_count=args.fragments,
        variant_fraction=args.variant_fraction,
        seed=args.seed,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
