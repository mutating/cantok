import io
import sys
from contextlib import redirect_stdout

import pytest

from cantok import ConditionToken, CounterToken, SimpleToken, TimeoutToken


@pytest.mark.parametrize(
    ('create_value', 'expected_string'),
    [
        (lambda: SimpleToken(cancelled=True).wait(), ''),
        (lambda: TimeoutToken(0.0001).wait(), ''),
        (lambda: ConditionToken(lambda: True).wait(), ''),
        (lambda: CounterToken(0).wait(), ''),
        (lambda: 1, '1\n'),
        (lambda: 'kek', f'{"kek"!r}\n'),
    ],
)
@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_displayhook_printing_coroutine_wrappers_and_other_objects(create_value, expected_string):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        sys.displayhook(create_value())

    output = buffer.getvalue()

    assert output == expected_string
