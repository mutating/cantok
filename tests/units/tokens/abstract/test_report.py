from dataclasses import FrozenInstanceError
from sys import getsizeof, version_info

import pytest

from cantok import SimpleToken, TimeoutToken
from cantok.tokens.abstract.abstract_token import CancelCause, CancellationReport


def test_cant_change_cancellation_report():
    """Cancellation reports must reject post-construction field changes."""
    report = CancellationReport(
        cause=CancelCause.NOT_CANCELLED,
        from_token=SimpleToken(),
    )

    with pytest.raises(FrozenInstanceError):
        report.from_token = TimeoutToken(1)


@pytest.mark.skipif(version_info < (3, 8), reason='There is no support of __slots__ for dataclasses in old pythons.')
def test_size_of_report_is_not_so_big():
    """
    Protect the compact memory footprint of cancellation reports.

    Report objects are produced during cancellation checks, so a neutral report
    must stay within the expected size threshold.
    """
    report = CancellationReport(
        cause=CancelCause.NOT_CANCELLED,
        from_token=SimpleToken(),
    )

    assert getsizeof(report) <= 48
