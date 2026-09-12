from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.domain import Verdict


ProfileName = Literal["compatible", "changed", "corrected"]


class HandoffRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profiles: list[ProfileName] = Field(min_length=1)
    fixture_id: str = Field(min_length=1)


class VariantRecord(BaseModel):
    gene: Literal["FLT3"] = "FLT3"
    type: Literal["ITD"] = "ITD"
    position: int
    length_bp: int = Field(gt=0)
    sequence: str = Field(min_length=1)
    test_vaf: float = Field(ge=0, le=1)


class RunRecord(BaseModel):
    run_id: str
    profile: ProfileName
    status: Literal["completed", "failed"]
    sandbox_id: str | None
    caller: str = "getITD"
    caller_version: str
    config_sha256: str
    fixture_sha256: str
    exact_recovery: bool | None
    detected_position: int | None = None
    detected_length_bp: int | None = None
    detected_sequence: str | None = None
    error: str | None = None

    @model_validator(mode="after")
    def validate_outcome(self) -> "RunRecord":
        if self.status == "completed" and (self.exact_recovery is None or self.error is not None):
            raise ValueError("Completed runs require an exact-recovery result and no error")
        if self.status == "failed" and (self.exact_recovery is not None or not self.error):
            raise ValueError("Failed runs require an error and no exact-recovery result")
        return self


class HandoffResponse(BaseModel):
    case_id: str
    fixture_id: str
    synthetic: bool
    variant: VariantRecord
    runs: list[RunRecord]
    verdict: Verdict
    verdict_source: Literal["neo4j"] = "neo4j"
    limitations: list[str]
