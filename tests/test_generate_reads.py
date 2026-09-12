from pathlib import Path

from pipeline.generate_reads import generate_fixture


REFERENCE = Path("vendor/getitd/anno/amplicon.txt")


def test_fixture_is_deterministic(tmp_path):
    first = generate_fixture(REFERENCE, tmp_path / "first")
    second = generate_fixture(REFERENCE, tmp_path / "second")
    assert first["r1_sha256"] == second["r1_sha256"]
    assert first["r2_sha256"] == second["r2_sha256"]
    assert first["itd_position"] == 72
    assert first["itd_length_bp"] == 21
    assert first["synthetic"] is True


def test_fastq_pairs_have_valid_shape(tmp_path):
    manifest = generate_fixture(REFERENCE, tmp_path, fragment_count=20)
    for suffix in ("R1", "R2"):
        lines = (tmp_path / f"FLT3-ITD-DEMO-001_{suffix}.fastq").read_text().splitlines()
        assert len(lines) == 20 * 4
        for index in range(0, len(lines), 4):
            assert lines[index].startswith("@ITDCARRY:")
            assert lines[index + 2] == "+"
            assert len(lines[index + 1]) == manifest["read_length_bp"]
            assert len(lines[index + 3]) == manifest["read_length_bp"]

