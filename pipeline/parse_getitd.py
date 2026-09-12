from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from backend.domain import ITD


class GetITDParseError(RuntimeError):
    """Raised when a completed caller output cannot be interpreted safely."""


@dataclass(frozen=True)
class DetectedITD:
    marker: ITD
    sample: str
    vaf_percent: float
    total_supporting_reads: int
    unique_supporting_reads: int


def parse_high_confidence_itds(path: str | Path) -> list[DetectedITD]:
    """Parse getITD's final high-confidence TSV without relaxing exact fields."""
    source = Path(path)
    if not source.is_file():
        # getITD does not create an ITD TSV when it finds no ITDs. The caller
        # runner must establish successful completion before invoking this.
        return []

    try:
        with source.open("r", encoding="utf-8", newline="") as handle:
            rows = csv.DictReader(handle, delimiter="\t")
            required = {
                "sample",
                "start",
                "length",
                "seq",
                "vaf",
                "counts",
                "counts_unique_total",
            }
            if rows.fieldnames is None or not required.issubset(rows.fieldnames):
                missing = sorted(required.difference(rows.fieldnames or []))
                raise GetITDParseError(f"Missing getITD columns: {missing}")

            parsed: list[DetectedITD] = []
            for line_number, row in enumerate(rows, start=2):
                try:
                    parsed.append(
                        DetectedITD(
                            marker=ITD(
                                position=int(row["start"]),
                                length_bp=int(row["length"]),
                                sequence=row["seq"],
                            ),
                            sample=row["sample"],
                            vaf_percent=float(row["vaf"]),
                            total_supporting_reads=int(row["counts"]),
                            unique_supporting_reads=int(row["counts_unique_total"]),
                        )
                    )
                except (TypeError, ValueError) as exc:
                    raise GetITDParseError(
                        f"Invalid value in {source.name} at line {line_number}"
                    ) from exc
            return parsed
    except UnicodeDecodeError as exc:
        raise GetITDParseError(f"Output is not valid UTF-8: {source}") from exc

