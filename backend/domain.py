from dataclasses import dataclass
from enum import StrEnum


class RunStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class Verdict(StrEnum):
    COMPUTATIONALLY_OBSERVABLE = "COMPUTATIONALLY_OBSERVABLE"
    NOT_TECHNICALLY_COMPARABLE = "NOT_TECHNICALLY_COMPARABLE"
    NO_CONCLUSION = "NO_CONCLUSION"


@dataclass(frozen=True)
class ITD:
    position: int
    length_bp: int
    sequence: str

