import pytest

from backend.domain import ITD, RunStatus, Verdict
from backend.exact_match import any_exact_recovery, exact_recovery, local_verdict


EXPECTED = ITD(position=100, length_bp=6, sequence="ACGTAC")


@pytest.mark.parametrize(
    ("detected", "result"),
    [
        (ITD(100, 6, "ACGTAC"), True),
        (ITD(100, 6, "ac gtac"), True),
        (ITD(100, 6, "ACGTAA"), False),
        (ITD(101, 6, "ACGTAC"), False),
        (ITD(100, 9, "ACGTAC"), False),
        (None, False),
    ],
)
def test_exact_recovery(detected, result):
    assert exact_recovery(EXPECTED, detected) is result


def test_any_exact_recovery_accepts_one_exact_call():
    assert any_exact_recovery(
        EXPECTED,
        [ITD(100, 6, "AAAAAA"), ITD(100, 6, "ACGTAC")],
    )


def test_execution_failure_is_no_conclusion():
    assert local_verdict(RunStatus.FAILED, None) is Verdict.NO_CONCLUSION


def test_completed_miss_is_not_technically_comparable():
    assert (
        local_verdict(RunStatus.COMPLETED, False)
        is Verdict.NOT_TECHNICALLY_COMPARABLE
    )

