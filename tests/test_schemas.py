import pytest
from pydantic import ValidationError

from backend.schemas import HandoffRequest, RunRecord


def test_request_accepts_known_profiles():
    request = HandoffRequest(
        fixture_id="FLT3-ITD-DEMO-001",
        profiles=["compatible", "changed"],
    )
    assert request.profiles == ["compatible", "changed"]


def test_request_rejects_unknown_profile():
    with pytest.raises(ValidationError):
        HandoffRequest(fixture_id="FLT3-ITD-DEMO-001", profiles=["unknown"])


def test_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        HandoffRequest(
            fixture_id="FLT3-ITD-DEMO-001",
            profiles=["compatible"],
            filesystem_path="C:/secret",
        )


def test_run_record_rejects_inconsistent_completed_outcome():
    with pytest.raises(ValidationError):
        RunRecord(
            run_id="run-1",
            profile="compatible",
            status="completed",
            sandbox_id="sandbox-1",
            caller_version="1.5.17",
            config_sha256="a" * 64,
            fixture_sha256="b" * 64,
            exact_recovery=None,
        )


def test_run_record_accepts_failed_outcome():
    run = RunRecord(
        run_id="run-1",
        profile="compatible",
        status="failed",
        sandbox_id="sandbox-1",
        caller_version="1.5.17",
        config_sha256="a" * 64,
        fixture_sha256="b" * 64,
        exact_recovery=None,
        error="Caller execution failed",
    )
    assert run.status == "failed"
