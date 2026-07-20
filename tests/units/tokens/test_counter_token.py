from threading import Thread

import pytest

from cantok import CounterCancellationError, CounterToken, DefaultToken, SimpleToken
from cantok.tokens.abstract.abstract_token import CancelCause, CancellationReport


def test_counter_token_is_deprecated():
    """
    Ensure CounterToken construction emits the public deprecation warning.

    The test checks the warning category and stable message prefix only; counter
    behavior is covered by dedicated tests.
    """
    with pytest.warns(DeprecationWarning, match='CounterToken is deprecated'):
        CounterToken(1)


@pytest.mark.parametrize(
    'iterations',
    [
        0,
        1,
        5,
        15,
    ],
)
def test_counter(iterations):
    """
    Stop a direct polling loop after exactly the configured number of iterations.

    The zero-count boundary cancels before the loop body runs.
    """
    token = CounterToken(iterations)
    counter = 0

    while not token.cancelled:
        counter += 1

    assert counter == iterations


def test_double_str():
    """
    Ensure rendering the same one-attempt counter token twice is stable.

    The test compares the two string results directly instead of pinning the exact
    text, and this repeated rendering must not consume the counter.
    """
    token = CounterToken(1)

    assert str(token) == str(token)  # noqa: PLR0124


def test_counter_less_than_zero():
    """
    Reject negative initial counters at construction.

    CounterToken only accepts non-negative iteration limits, with zero as the
    valid lower boundary.
    """
    with pytest.raises(ValueError, match=r'.'):
        CounterToken(-1)


@pytest.mark.parametrize(
    'iterations',
    [
        10_000,
        50_000,
        1_000,
    ],
)
@pytest.mark.parametrize(
    'number_of_threads',
    [
        1,
        2,
        5,
    ],
)
def test_race_condition_for_counter(iterations, number_of_threads):
    """Ensure concurrent direct polls consume exactly the configured counter."""
    results = []
    token = CounterToken(iterations)

    def decrementer(_number):
        counter = 0
        while not token.cancelled:
            counter += 1
        results.append(counter)

    threads = [Thread(target=decrementer, args=(iterations / number_of_threads, )) for _ in range(number_of_threads)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    result = sum(results)
    assert result == iterations


@pytest.mark.parametrize(
    ('kwargs', 'expected_result'),
    [
        ({}, 5),
        ({'direct': True}, 5),
        ({'direct': False}, 4),
    ],
)
def test_direct_default_counter(kwargs, expected_result):
    """
    Verify indirect parent polling honors the CounterToken `direct` option.

    Polling through SimpleToken must not consume default/direct=True counters, must
    consume direct=False counters, and direct polling the nested token still
    decrements afterward.
    """
    nested_token = CounterToken(5, **kwargs)
    token = SimpleToken(nested_token)

    assert not token.cancelled
    assert nested_token.counter == expected_result

    assert not nested_token.cancelled
    assert nested_token.counter == expected_result - 1


def test_check_superpower_raised():
    """
    Check raises CounterCancellationError after a standalone five-attempt CounterToken exhausts.

    Repeated checks keep reporting the exhausted token with the original attempt limit in the message.
    """
    token = CounterToken(5)

    while not token.cancelled:
        pass

    with pytest.raises(CounterCancellationError):
        token.check()

    with pytest.raises(CounterCancellationError) as exc_info:
        token.check()
    assert str(exc_info.value) == 'After 5 attempts, the counter was reset to zero.'
    assert exc_info.value.token is token


def test_check_superpower_raised_nested():
    """
    Parent check preserves a nested five-attempt CounterToken cancellation attribution.

    The nested counter is `direct=False`, so parent polling can exhaust it; repeated
    parent checks then raise with the nested counter's exception type, message, and
    token attribution.
    """
    nested_token = CounterToken(5, direct=False)
    token = SimpleToken(nested_token)

    while not token.cancelled:
        pass

    with pytest.raises(CounterCancellationError):
        token.check()

    with pytest.raises(CounterCancellationError) as exc_info:
        token.check()
    assert str(exc_info.value) == 'After 5 attempts, the counter was reset to zero.'
    assert exc_info.value.token is nested_token
    assert exc_info.value.token.exception is type(exc_info.value)


def test_get_report_cancelled():
    """Verify that ordinary polling reports an exhausted standalone CounterToken as its own superpower cancellation."""
    token = CounterToken(5)

    while not token.cancelled:
        pass

    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.SUPERPOWER
    assert report.from_token is token


@pytest.mark.parametrize(
    ('counter', 'counter_nested', 'from_token_is_nested'),
    [
        (1, 0, True),
        (0, 1, False),
        (0, 0, False),
    ],
)
def test_get_report_cancelled_nested(counter, counter_nested, from_token_is_nested):
    """
    Report the first counter superpower in parent-first nested order.

    When both counters are already exhausted the parent owns the report, but if
    the parent starts at one and only reaches zero during this lookup, the
    already-exhausted nested counter remains the reported source. The report is
    always a CancellationReport with SUPERPOWER cause.
    """
    nested_token = CounterToken(counter_nested)
    token = CounterToken(counter, nested_token)

    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.SUPERPOWER
    if from_token_is_nested:
        assert report.from_token is nested_token
    else:
        assert report.from_token is token


@pytest.mark.parametrize(
    ('poll', 'expected_exception_type'),
    [
        (lambda token: token.check(), CounterCancellationError),
        (lambda token: token.check(exception=None), CounterCancellationError),
        (lambda token: token.check(exception=RuntimeError), RuntimeError),
        (lambda token: token.check(exception=RuntimeError('custom message')), RuntimeError),
        (lambda token: token.is_cancelled(), None),
        (lambda token: token.cancelled, None),
        (lambda token: token.keep_on(), None),
    ],
)
@pytest.mark.parametrize(
    ('initial_counter', 'final_counter'),
    [
        (50, 49),
        (5, 4),
        (1, 0),
        (0, 0),
    ],
)
def test_direct_status_operations_poll_counter_once(
    poll,
    expected_exception_type,
    initial_counter,
    final_counter,
):
    """
    Poll the counter once for each tested direct status operation.

    `check()` covers omitted, `None`, class, and instance exception forms
    alongside `is_cancelled()`, `cancelled`, and `keep_on()`. Positive counters
    decrement once and zero remains zero. At zero, `check()` raises the exact
    expected class while the other operations do not raise.
    """
    token = CounterToken(initial_counter)
    poll_calls = []
    original_get_report = token._get_report

    def record_poll_and_get_report(*args, **kwargs):
        poll_calls.append(None)
        return original_get_report(*args, **kwargs)

    token._get_report = record_poll_and_get_report

    if initial_counter == 0 and expected_exception_type is not None:
        with pytest.raises(expected_exception_type) as exc_info:
            poll(token)

        assert type(exc_info.value) is expected_exception_type
    else:
        poll(token)

    assert poll_calls == [None]
    assert token.counter == final_counter


def test_check_is_decrementing_counter_when_nested_token_is_cancelled():
    """
    Check still consumes a two-attempt parent counter while nested cancellation is reported.

    The check that reaches zero keeps raising from the nested token; the next check
    raises from the parent counter superpower.
    """
    nested_token = SimpleToken(cancelled=True)
    token = CounterToken(2, nested_token)

    with pytest.raises(Exception, match=r'.') as exc_info:
        token.check()
    assert exc_info.value.token is nested_token
    assert type(exc_info.value) is nested_token.exception
    assert type(exc_info.value) is not token.exception

    assert token.counter == 1

    with pytest.raises(Exception, match=r'.') as exc_info:
        token.check()
    assert exc_info.value.token is nested_token
    assert type(exc_info.value) is nested_token.exception
    assert type(exc_info.value) is not token.exception

    assert token.counter == 0

    with pytest.raises(Exception, match=r'.') as exc_info:
        token.check()
    assert exc_info.value.token is token
    assert type(exc_info.value) is token.exception
    assert type(exc_info.value) is not nested_token.exception


def test_decrement_counter_after_zero():
    """Direct polling an already exhausted CounterToken leaves its counter at zero."""
    token = CounterToken(0)

    token.is_cancelled()

    assert token.counter == 0


def test_counter_token_plus_simple_token():
    """
    Check that CounterToken + SimpleToken preserves operands in order.

    The composed token is a fresh SimpleToken wrapper containing the original
    counter token first and the original simple token second.
    """
    simple_token = SimpleToken()
    counter_token = CounterToken(1)
    token = counter_token + simple_token

    assert isinstance(token, SimpleToken)
    assert token is not simple_token
    assert len(token._tokens) == 2
    assert isinstance(token._tokens[0], CounterToken)
    assert token._tokens[0] is counter_token
    assert token._tokens[1] is simple_token


def test_simple_token_plus_counter_token():
    """
    Adding a counter token on the right creates an ordered simple composite.

    The composite preserves the original simple token and counter token identities
    in left-to-right order.
    """
    simple_token = SimpleToken()
    counter_token = CounterToken(1)
    token = simple_token + counter_token

    assert isinstance(token, SimpleToken)
    assert token is not simple_token
    assert len(token._tokens) == 2
    assert isinstance(token._tokens[1], CounterToken)
    assert token._tokens[1] is counter_token
    assert token._tokens[0] is simple_token


def test_zero_counter_token_report_is_about_superpower():
    """
    Report an initially exhausted counter token as cancelled by its own superpower.

    Both direct and indirect report checks should classify a zero-count token as superpower-cancelled despite indirect polling rollback behavior.
    """
    for report in CounterToken(0)._get_report(True), CounterToken(0)._get_report(False):
        assert report.cause == CancelCause.SUPERPOWER


def test_repr_for_counter_token():
    """
    `CounterToken` repr reflects counter, options, state, and nesting.

    The same contract is checked with `doc`: `None` keeps the old repr, valid
    text is appended last, escaped text is represented safely, and
    `DefaultToken` remains neutral when nested.
    """
    assert repr(CounterToken(0)) == 'CounterToken(0)'
    assert repr(CounterToken(1)) == 'CounterToken(1)'
    assert repr(CounterToken(10000)) == 'CounterToken(10000)'

    assert repr(CounterToken(10000, CounterToken(10000))) == 'CounterToken(10000, CounterToken(10000))'
    assert repr(CounterToken(10000, CounterToken(10000), CounterToken(10000))) == 'CounterToken(10000, CounterToken(10000), CounterToken(10000))'
    assert repr(CounterToken(10000, CounterToken(10000), doc=None)) == 'CounterToken(10000, CounterToken(10000))'
    assert repr(CounterToken(10000, CounterToken(10000, doc='nested'), doc='parent')) == "CounterToken(10000, CounterToken(10000, doc='nested'), doc='parent')"
    assert repr(CounterToken(10000, DefaultToken(doc='neutral'), doc='parent')) == "CounterToken(10000, doc='parent')"

    assert repr(CounterToken(10000, direct=True)) == 'CounterToken(10000)'
    assert repr(CounterToken(10000, direct=False)) == 'CounterToken(10000, direct=False)'

    assert repr(CounterToken(10000, cancelled=False)) == 'CounterToken(10000)'
    assert repr(CounterToken(10000, cancelled=True)) == 'CounterToken(10000, cancelled=True)'

    assert repr(CounterToken(10000, direct=False, cancelled=True)) == 'CounterToken(10000, cancelled=True, direct=False)'
    assert repr(CounterToken(10000, CounterToken(10000), direct=False, cancelled=True)) == 'CounterToken(10000, CounterToken(10000), cancelled=True, direct=False)'
    assert repr(CounterToken(10000, CounterToken(10000), direct=False, cancelled=True, doc=None)) == 'CounterToken(10000, CounterToken(10000), cancelled=True, direct=False)'
    assert repr(CounterToken(10000, doc='d')) == "CounterToken(10000, doc='d')"
    assert repr(CounterToken(0, doc='d')) == "CounterToken(0, doc='d')"
    assert repr(CounterToken(10000, cancelled=True, doc='d')) == "CounterToken(10000, cancelled=True, doc='d')"
    assert repr(CounterToken(10000, direct=False, doc='d')) == "CounterToken(10000, direct=False, doc='d')"
    assert repr(CounterToken(10000, direct=False, cancelled=True, doc='d')) == "CounterToken(10000, cancelled=True, direct=False, doc='d')"
    assert repr(CounterToken(10000, doc="escaped ' doc")) == 'CounterToken(10000, doc="escaped \' doc")'
