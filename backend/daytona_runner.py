from __future__ import annotations

import hashlib
import json
import tempfile
import uuid
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from daytona import (
    CreateSandboxFromSnapshotParams,
    Daytona,
    DaytonaFileNotFoundError,
    FileUpload,
)

from backend.domain import ITD
from backend.exact_match import any_exact_recovery
from backend.schemas import RunRecord
from pipeline.parse_getitd import parse_high_confidence_itds


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "data" / "synthetic_case" / "generated"
MANIFEST_PATH = FIXTURE_DIR / "manifest.json"
PROFILES_DIR = ROOT / "pipeline" / "profiles"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _bundle(path: Path) -> None:
    members = [
        ROOT / "vendor" / "getitd" / "getitd.py",
        ROOT / "vendor" / "getitd" / "anno" / "amplicon.txt",
        ROOT / "vendor" / "getitd" / "anno" / "amplicon_kayser.tsv",
        FIXTURE_DIR / "FLT3-ITD-DEMO-001_R1.fastq",
        FIXTURE_DIR / "FLT3-ITD-DEMO-001_R2.fastq",
    ]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for member in members:
            archive.write(member, member.relative_to(ROOT).as_posix())


def run_profiles(profiles: list[str]) -> tuple[list[RunRecord], dict]:
    allowed = {"compatible", "changed", "corrected"}
    if not profiles or any(profile not in allowed for profile in profiles):
        raise ValueError("Unknown or empty profile list")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = ITD(
        manifest["itd_position"], manifest["itd_length_bp"], manifest["itd_sequence"]
    )
    r1 = FIXTURE_DIR / "FLT3-ITD-DEMO-001_R1.fastq"
    r2 = FIXTURE_DIR / "FLT3-ITD-DEMO-001_R2.fastq"
    if sha256(r1) != manifest["r1_sha256"] or sha256(r2) != manifest["r2_sha256"]:
        raise RuntimeError("Fixture hash mismatch")

    daytona = Daytona()
    sandbox = daytona.create(CreateSandboxFromSnapshotParams(language="python"), timeout=60)
    records: list[RunRecord] = []
    try:
        remote_root = f"{sandbox.get_work_dir()}/itdcarry"
        sandbox.fs.create_folder(remote_root, "755")
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle.zip"
            _bundle(bundle)
            sandbox.fs.upload_files([FileUpload(str(bundle), f"{remote_root}/bundle.zip")])
        setup = sandbox.process.exec(
            "python -c \"import zipfile; zipfile.ZipFile('bundle.zip').extractall('.')\" && "
            "python -m pip install -q numpy pandas biopython",
            cwd=remote_root,
            timeout=300,
        )
        if setup.exit_code != 0:
            raise RuntimeError(f"Daytona setup failed: {setup.result}")

        fixture_hash = hashlib.sha256(
            (manifest["r1_sha256"] + manifest["r2_sha256"]).encode()
        ).hexdigest()
        for profile in profiles:
            profile_path = PROFILES_DIR / f"{profile}.json"
            profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
            run_id = f"run-{uuid.uuid4().hex[:12]}"
            sample = f"itdcarry-{profile}"
            args = " ".join(profile_data["getitd_args"])
            command = (
                "python vendor/getitd/getitd.py "
                "-reference vendor/getitd/anno/amplicon.txt "
                f"-anno vendor/getitd/anno/amplicon_kayser.tsv {args} {sample} "
                "data/synthetic_case/generated/FLT3-ITD-DEMO-001_R1.fastq "
                "data/synthetic_case/generated/FLT3-ITD-DEMO-001_R2.fastq"
            )
            response = sandbox.process.exec(command, cwd=remote_root, timeout=180)
            artifact_dir = ROOT / "artifacts" / run_id
            artifact_dir.mkdir(parents=True)
            (artifact_dir / "stdout.log").write_text(response.result or "", encoding="utf-8")
            config_hash = hashlib.sha256(profile_path.read_bytes()).hexdigest()
            common = dict(
                run_id=run_id, profile=profile, sandbox_id=sandbox.id,
                caller_version="1.5.17", config_sha256=config_hash,
                fixture_sha256=fixture_hash,
            )
            if response.exit_code != 0:
                records.append(RunRecord(**common, status="failed", exact_recovery=None, error="Caller execution failed"))
                continue
            remote_tsv = (
                f"{remote_root}/{sample}_getitd/"
                "itds_collapsed-is-same_is-similar_is-close_is-same_trailing_hc.tsv"
            )
            try:
                raw = sandbox.fs.download_file(remote_tsv)
            except DaytonaFileNotFoundError:
                raw = None
            calls = []
            if raw:
                local_tsv = artifact_dir / "raw-caller-output.tsv"
                local_tsv.write_bytes(raw)
                calls = parse_high_confidence_itds(local_tsv)
            recovered = any_exact_recovery(expected, [call.marker for call in calls])
            detected = next((call.marker for call in calls if any_exact_recovery(expected, [call.marker])), None)
            records.append(
                RunRecord(
                    **common, status="completed", exact_recovery=recovered,
                    detected_position=detected.position if detected else None,
                    detected_length_bp=detected.length_bp if detected else None,
                    detected_sequence=detected.sequence if detected else None,
                    error=None,
                )
            )
            (artifact_dir / "execution.json").write_text(
                json.dumps({"sandbox_id": sandbox.id, "completed_at": datetime.now(UTC).isoformat()}, indent=2),
                encoding="utf-8",
            )
        return records, manifest
    finally:
        daytona.delete(sandbox, timeout=60, wait=True)
