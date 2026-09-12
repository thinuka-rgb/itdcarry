from collections.abc import Iterable

from backend.domain import ITD, RunStatus, Verdict


def normalize_sequence(sequence: str) -> str:
    """Apply the only universally safe normalization to a DNA sequence."""
    return "".join(sequence.upper().split())


def exact_recovery(expected: ITD, detected: ITD | None) -> bool:
    if detected is None:
        return False
    return (
        expected.position == detected.position
        and expected.length_bp == detected.length_bp
        and normalize_sequence(expected.sequence)
        == normalize_sequence(detected.sequence)
    )


def any_exact_recovery(expected: ITD, detected: Iterable[ITD]) -> bool:
    return any(exact_recovery(expected, call) for call in detected)


def local_verdict(status: RunStatus, recovered: bool | None) -> Verdict:
    """Reference semantics for tests; production verdict comes from Neo4j."""
    if status is RunStatus.FAILED or recovered is None:
        return Verdict.NO_CONCLUSION
    if recovered:
        return Verdict.COMPUTATIONALLY_OBSERVABLE
    return Verdict.NOT_TECHNICALLY_COMPARABLE

