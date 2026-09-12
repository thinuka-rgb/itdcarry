from pathlib import Path

import pytest

from pipeline.parse_getitd import GetITDParseError, parse_high_confidence_itds


FIXTURE = Path(__file__).parent / "fixtures" / "getitd_hc.tsv"


def test_parse_realistic_high_confidence_output():
    calls = parse_high_confidence_itds(FIXTURE)
    assert len(calls) == 1
    call = calls[0]
    assert call.marker.position == 72
    assert call.marker.length_bp == 21
    assert call.marker.sequence == "TTGATTTCAGAGAATATGAAT"
    assert call.vaf_percent == pytest.approx(69.023)
    assert call.total_supporting_reads == 1377
    assert call.unique_supporting_reads == 44


def test_missing_output_means_no_calls_after_successful_execution(tmp_path):
    assert parse_high_confidence_itds(tmp_path / "not-created.tsv") == []


def test_malformed_output_fails_closed(tmp_path):
    malformed = tmp_path / "bad.tsv"
    malformed.write_text("sample\tlength\nexample\t21\n", encoding="utf-8")
    with pytest.raises(GetITDParseError):
        parse_high_confidence_itds(malformed)

