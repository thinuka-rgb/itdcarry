import pytest
from pydantic import ValidationError

from backend.schemas import HandoffRequest


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

