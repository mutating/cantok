import time
from time import perf_counter, sleep

import pytest

from cantok import (
    ConditionToken,
    CounterToken,
    DefaultToken,
    SimpleToken,
    TimeoutCancellationError,
    TimeOutToken,
    TimeoutToken,
)
from cantok.tokens.abstract.abstract_token import CancelCause, CancellationReport


def test_timeout_token_deprecated_alias_points_to_timeout_token():
    """
    `TimeOutToken` remains a direct alias of `TimeoutToken`.

    The test keeps alias behavior separate from repeated constructor checks, so
    `doc` coverage does not need duplicate cases for both names.
    """
    assert TimeOutToken is TimeoutToken


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'monotonic': True},
        {'monotonic': False},
    ],
)
@pytest.mark.parametrize(
    'zero_timeout',
    [
        0,
        0.0,
    ],
)
def test_zero_timeout(zero_timeout, options):
    """
    Verify that a zero timeout is accepted and immediately expired.

    Checks integer and float zero across clock modes, with repeated status queries
    remaining cancelled and keep_on() remaining false.
    """
    token = TimeoutToken(zero_timeout, **options)

    assert token.cancelled == True
    assert token.cancelled == True
    assert token.is_cancelled() == True
    assert token.is_cancelled() == True
    assert token.keep_on() == False
    assert token.keep_on() == False


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'monotonic': True},
        {'monotonic': False},
    ],
)
@pytest.mark.parametrize(
    'timeout',
    [
        -1,
        -0.5,
    ],
)
def test_less_than_zero_timeout(options, timeout):
    """
    Reject negative timeout values during construction.

    Pins the exact ValueError for integer and float negatives across all monotonic option forms.
    """
    with pytest.raises(ValueError, match=r'You cannot specify a timeout less than zero\.'):
        TimeoutToken(timeout, **options)


def test_raise_without_first_argument():
    """Omitting the required timeout duration is rejected by the timeout-token constructor."""
    with pytest.raises(TypeError):
        TimeoutToken()


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'monotonic': True},
        {'monotonic': False},
    ],
)
def test_timeout_expired(options):
    """A positive timeout flips every status API after its deadline."""
    timeout = 0.1
    token = TimeoutToken(timeout, **options)

    assert token.cancelled == False
    assert token.cancelled == False
    assert token.is_cancelled() == False
    assert token.is_cancelled() == False
    assert token.keep_on() == True
    assert token.keep_on() == True

    sleep(timeout * 2)

    assert token.cancelled == True
    assert token.cancelled == True
    assert token.is_cancelled() == True
    assert token.is_cancelled() == True
    assert token.keep_on() == False
    assert token.keep_on() == False


@pytest.mark.parametrize(
    ('monotonic', 'clock_name', 'expired_time'),
    [
        (False, 'perf_counter', 1.1),
        (True, 'monotonic_ns', 1_100_000_000),
    ],
)
def test_timeout_token_clock_can_be_patched_through_time_module(monkeypatch, monotonic, clock_name, expired_time):
    """
    `TimeoutToken` reads its clock through the standard `time` module.

    Patching the public clock function before construction must control both
    the deadline calculation and later cancellation checks without reaching
    into `cantok.tokens.timeout_token` internals.
    """
    current_time = 0.0

    monkeypatch.setattr(time, clock_name, lambda: current_time)

    token = TimeoutToken(1, monotonic=monotonic)

    assert token.cancelled == False

    current_time = expired_time

    assert token.cancelled == True


def test_text_representaion_of_extra_kwargs():
    """Confirm timeout extra kwargs render only non-default clock options."""
    assert TimeoutToken(5, monotonic=False)._text_representation_of_extra_kwargs() == ''
    assert TimeoutToken(5, monotonic=True)._text_representation_of_extra_kwargs() == 'monotonic=True'
    assert TimeoutToken(5)._text_representation_of_extra_kwargs() == ''


def test_repr_of_timeout_token():
    """
    `TimeoutToken` repr reflects timeout values, state, and monotonic options.

    The same option cases also check that a valid `doc` is appended after the
    existing option text without changing the old repr. Extra assertions cover
    state, nesting, escaping, and neutral `DefaultToken` filtering.
    """
    assert repr(TimeoutToken(1)) == 'TimeoutToken(1)'
    assert repr(TimeoutToken(0)) == 'TimeoutToken(0)'
    assert repr(TimeoutToken(0.5)) == 'TimeoutToken(0.5)'
    assert repr(TimeoutToken(1.25, monotonic=False)) == 'TimeoutToken(1.25)'
    assert repr(TimeoutToken(0.5, monotonic=True)) == 'TimeoutToken(0.5, monotonic=True)'
    assert repr(TimeoutToken(1, cancelled=False, monotonic=True)) == 'TimeoutToken(1, monotonic=True)'
    assert repr(TimeoutToken(1, cancelled=True)) == 'TimeoutToken(1, cancelled=True)'
    assert repr(TimeoutToken(1, doc='d')) == "TimeoutToken(1, doc='d')"
    assert repr(TimeoutToken(1, monotonic=True)) == 'TimeoutToken(1, monotonic=True)'
    assert repr(TimeoutToken(1, monotonic=True, doc='d')) == "TimeoutToken(1, monotonic=True, doc='d')"
    assert repr(TimeoutToken(1, monotonic=False)) == 'TimeoutToken(1)'
    assert repr(TimeoutToken(1, monotonic=False, doc='d')) == "TimeoutToken(1, doc='d')"
    assert repr(TimeoutToken(1, monotonic=True, cancelled=True, doc=None)) == 'TimeoutToken(1, cancelled=True, monotonic=True)'
    assert repr(TimeoutToken(0, doc='d')) == "TimeoutToken(0, doc='d')"
    assert repr(TimeoutToken(1, cancelled=True, doc='d')) == "TimeoutToken(1, cancelled=True, doc='d')"
    assert repr(TimeoutToken(1, monotonic=True, cancelled=True, doc='d')) == "TimeoutToken(1, cancelled=True, monotonic=True, doc='d')"
    assert repr(TimeoutToken(1, doc="escaped ' doc")) == 'TimeoutToken(1, doc="escaped \' doc")'
    assert repr(TimeoutToken(1, TimeoutToken(2), doc=None)) == 'TimeoutToken(1, TimeoutToken(2))'
    assert repr(TimeoutToken(1, TimeoutToken(2, doc='nested'), doc='parent')) == "TimeoutToken(1, TimeoutToken(2, doc='nested'), doc='parent')"
    assert repr(TimeoutToken(1, DefaultToken(doc='neutral'), doc='parent')) == "TimeoutToken(1, doc='parent')"


def test_check_superpower_raised():
    """
    Expired direct timeout checks raise the timeout-specific cancellation error.

    The raised error preserves the timeout message and points back to the checked token.
    """
    token = TimeoutToken(0.125)

    while not token.cancelled:
        pass

    with pytest.raises(TimeoutCancellationError):
        token.check()

    with pytest.raises(TimeoutCancellationError) as exc_info:
        token.check()
    assert str(exc_info.value) == 'The timeout of 0.125 seconds has expired.'
    assert exc_info.value.token is token


@pytest.mark.parametrize(
    'timeout',
    [
        0.125,
        0,
    ],
)
def test_check_superpower_raised_nested(timeout):
    """
    Raise the nested timeout token's cancellation error through its parent.

    The parent must report the expired nested token as the cancellation source.
    """
    nested_token = TimeoutToken(timeout)
    token = SimpleToken(nested_token)

    while not token.cancelled:
        pass

    with pytest.raises(TimeoutCancellationError):
        token.check()

    with pytest.raises(TimeoutCancellationError) as exc_info:
        token.check()
    assert str(exc_info.value) == f'The timeout of {timeout} seconds has expired.'
    assert exc_info.value.token is nested_token
    assert exc_info.value.token.exception is type(exc_info.value)


def test_get_report_cancelled():
    """Report an expired standalone timeout as its own superpower cancellation."""
    token = TimeoutToken(0)

    while not token.cancelled:
        pass

    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.SUPERPOWER
    assert report.from_token is token


@pytest.mark.parametrize(
    ('timeout', 'timeout_nested', 'from_token_is_nested'),
    [
        (0, 0, False),
        (1, 0, True),
        (0, 1, False),
    ],
)
def test_get_report_cancelled_nested(timeout, timeout_nested, from_token_is_nested):
    """
    Report which timeout token causes nested cancellation across priority cases.

    The report is checked for three cases: both parent and nested timeout expired,
    only the nested timeout expired, and only the parent timeout expired. The nested
    token is reported only while the parent timeout is still active; otherwise the
    parent reports its own timeout superpower.
    """
    nested_token = TimeoutToken(timeout_nested)
    token = TimeoutToken(timeout, nested_token)

    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.SUPERPOWER
    if from_token_is_nested:
        assert report.from_token is nested_token
    else:
        assert report.from_token is token


def test_timeout_wait():
    """
    Wait until the timeout token cancels itself.

    The synchronous wait should not return before the token's own timeout has elapsed.
    """
    sleep_duration = 1
    token = TimeoutToken(sleep_duration)

    start_time = perf_counter()
    token.wait()
    finish_time = perf_counter()

    assert sleep_duration <= finish_time - start_time


def test_timeout_token_plus_simple_token():
    """
    Ensure TimeoutToken plus SimpleToken creates a new ordered composition.

    The resulting SimpleToken preserves both original operands by identity, with
    the TimeoutToken first and the SimpleToken second.
    """
    simple_token = SimpleToken()
    timeout_token = TimeoutToken(1)
    token = timeout_token + simple_token

    assert isinstance(token, SimpleToken)
    assert token is not simple_token
    assert len(token._tokens) == 2
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0] is timeout_token
    assert token._tokens[1] is simple_token


def test_simple_token_plus_timeout_token():
    """
    Ensure SimpleToken plus TimeoutToken creates a new ordered container.

    The result preserves the original SimpleToken and TimeoutToken by identity in
    left-to-right order.
    """
    simple_token = SimpleToken()
    timeout_token = TimeoutToken(1)
    token = simple_token + timeout_token

    assert isinstance(token, SimpleToken)
    assert token is not simple_token
    assert len(token._tokens) == 2
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1] is timeout_token
    assert token._tokens[0] is simple_token


def test_timeout_is_more_important_than_cache():
    """
    Ensure an expired timeout overrides a cached nested cancellation report.

    The parent report is read through direct and indirect calls while a nested
    cancelled token is the cancellation cause. After the parent timeout expires,
    both calls must ignore the cached nested report and return the parent timeout's
    own superpower report.
    """
    sleep_time = 0.001
    inner_token = SimpleToken(cancelled=True)
    token = TimeoutToken(sleep_time, inner_token)

    for report in token._get_report(True), token._get_report(False):
        assert report is not None
        assert isinstance(report, CancellationReport)
        assert report.from_token is inner_token
        assert report.cause == CancelCause.CANCELLED

    sleep(sleep_time * 15)

    for report in token._get_report(True), token._get_report(False):
        assert report is not None
        assert isinstance(report, CancellationReport)
        assert report.from_token is token
        assert report.cause == CancelCause.SUPERPOWER


def test_zero_timeout_token_report_is_about_superpower():
    """
    Ensure an expired zero-timeout token reports cancellation by superpower.

    Both direct and indirect report checks should classify the immediate timeout
    as the token's own automatic cancellation cause.
    """
    for report in TimeoutToken(0)._get_report(True), TimeoutToken(0)._get_report(False):
        assert report.cause == CancelCause.SUPERPOWER


@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_same_monotonic_flag(addictional_kwargs):
    """
    Preserve larger-left and smaller-right timeout operands with the same monotonic setting.

    The resulting SimpleToken keeps both original plain TimeoutTokens in order, with
    no nested tokens added to either operand.
    """
    left = TimeoutToken(2, **addictional_kwargs)
    right = TimeoutToken(1, **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1
    assert token._tokens[0] is left
    assert token._tokens[1] is right


@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag(left_addictional_kwargs, right_addictional_kwargs):
    """
    Combine a bigger left timeout with a smaller right timeout without merging.

    Different monotonic flags keep the operands as two separate timeout tokens in
    the resulting sum, with no nested tokens added to either operand.
    """
    left = TimeoutToken(2, **left_addictional_kwargs)
    right = TimeoutToken(1, **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1
    assert token._tokens[0] is left
    assert token._tokens[1] is right


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_same_monotonic_flag(timeout_for_equal_or_bigger_token, addictional_kwargs):
    """
    Preserve two same-clock timeout operands without optimizing the sum.

    Cover a left timeout of 1 combined with a right timeout of 1 or 2, using
    matching monotonic flags on both operands. With no nested tokens involved, the
    sum must remain a SimpleToken containing the original left and right
    TimeoutToken objects in order, with no merging or reordering.
    """
    left = TimeoutToken(1, **addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token
    assert token._tokens[0] is left
    assert token._tokens[1] is right


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_not_same_monotonic_flag(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    """
    Preserve two plain timeout operands with incompatible clock modes.

    Left timeout is 1 and right timeout is 1 or 2; the effective monotonic flags
    differ, neither operand has nested tokens, and addition must not merge,
    replace, reorder, or otherwise collapse the original operands.
    """
    left = TimeoutToken(1, **left_addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token
    assert token._tokens[0] is left
    assert token._tokens[1] is right


@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_same_monotonic_flag_with_nested_condition_token_at_right(addictional_kwargs):
    """
    Preserve original timeout operands when the right side has a nested condition.

    A larger left TimeoutToken plus a smaller right TimeoutToken with the same
    monotonic flag should produce a SimpleToken containing those same two timeout
    objects in order. The left timeout stays unnested, and the right timeout keeps
    exactly its nested ConditionToken.
    """
    left = TimeoutToken(2, **addictional_kwargs)
    right = TimeoutToken(1, ConditionToken(lambda: False), **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)


@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag_with_nested_condition_token_at_right(left_addictional_kwargs, right_addictional_kwargs):
    """
    Preserve original incompatible timeout operands when only the right side has a condition.

    A larger left TimeoutToken plus a smaller right TimeoutToken with different
    monotonic flags should produce a SimpleToken containing those same two timeout
    objects in order. The left timeout stays unnested, and the right timeout keeps
    exactly its nested ConditionToken.
    """
    left = TimeoutToken(2, **left_addictional_kwargs)
    right = TimeoutToken(1, ConditionToken(lambda: False), **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_same_monotonic_flag_with_nested_condition_token_at_right(timeout_for_equal_or_bigger_token, addictional_kwargs):
    """
    Composing same-clock timeout tokens keeps the right nested condition attached.

    The left timeout is 1, the right timeout is 1 or 2, and both timeout tokens use
    the same monotonic flag. Only the right timeout embeds a ConditionToken, so the
    sum should preserve the original left and right timeout operands without
    flattening or moving that nested condition.
    """
    left = TimeoutToken(1, **addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: False), **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_nested_condition_token_at_right(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    """
    Preserve original incompatible timeout operands when the right timeout may be equal or larger.

    The left TimeoutToken has timeout 1, the right TimeoutToken has timeout 1 or 2,
    and their effective monotonic flags differ. The sum should be a SimpleToken
    containing those same timeout objects in order, with the left timeout unnested
    and the right timeout keeping exactly its nested ConditionToken.
    """
    left = TimeoutToken(1, **left_addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: False), **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)


@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_same_monotonic_flag_with_nested_condition_token_at_right_and_counter_token_at_left(addictional_kwargs):
    """
    Verify adding a larger left timeout to a smaller right timeout preserves both operands.

    Both timeout tokens use the same monotonic flag configuration, while the left
    timeout keeps its nested CounterToken and the right timeout keeps its nested
    ConditionToken in the resulting composite structure.
    """
    left = TimeoutToken(2, CounterToken(5), **addictional_kwargs)
    right = TimeoutToken(1, ConditionToken(lambda: False), **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1


@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag_with_nested_condition_token_at_right_and_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    """
    Preserve larger-left and smaller-right timeout operands with different monotonic settings.

    The resulting SimpleToken keeps the left CounterToken and right ConditionToken
    under their original TimeoutToken owners.
    """
    left = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs)
    right = TimeoutToken(1, ConditionToken(lambda: False), **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_same_monotonic_flag_with_nested_condition_token_at_right_and_counter_token_at_left(timeout_for_equal_or_bigger_token, addictional_kwargs):
    """
    Preserve original same-clock timeout operands and their own nested tokens.

    The left TimeoutToken has timeout 1 and owns a CounterToken, while the right
    TimeoutToken has timeout 1 or 2 and owns a ConditionToken. With matching
    monotonic flags, the sum should be a SimpleToken containing those same timeout
    objects in order, without moving, flattening, or copying either nested token.
    """
    left = TimeoutToken(1, CounterToken(5), **addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: False), **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_nested_condition_token_at_right_and_counter_token_at_left(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    """
    Preserve two mismatched-monotonic timeout operands and their own nested tokens.

    Checks that adding a left TimeoutToken with timeout 1 to a right TimeoutToken
    with timeout 1 or 2, using different monotonic flags, creates a SimpleToken
    wrapper over the original operands. The CounterToken nested in the left timeout
    and the ConditionToken nested in the right timeout must remain under those
    owners without merging, reordering, flattening, or copying.
    """
    left = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: False), **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token


@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_same_monotonic_flag_with_nested_counter_token_at_left(addictional_kwargs):
    """
    Preserve a left CounterToken under larger-left/smaller-right timeout addition.

    With matching monotonic settings, the resulting SimpleToken keeps the original
    TimeoutTokens in order, leaves the CounterToken under the left timeout, and
    leaves the right timeout unnested.
    """
    left = TimeoutToken(2, CounterToken(5), **addictional_kwargs)
    right = TimeoutToken(1, **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1


@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag_with_nested_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    """
    Preserve a left CounterToken when unequal timeout operands use different monotonic settings.

    The resulting SimpleToken keeps the original larger-left and smaller-right
    TimeoutTokens in order, with the CounterToken still nested only under the left
    timeout.
    """
    left = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs)
    right = TimeoutToken(1, **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 2
    assert token._tokens[1]._timeout == 1


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_same_monotonic_flag_with_nested_counter_token_at_left(timeout_for_equal_or_bigger_token, addictional_kwargs):
    """
    Preserve both timeout operands when only the left timeout nests a counter.

    Left is TimeoutToken(1) with CounterToken nested inside it, while right is
    TimeoutToken(1 or 2) without nested tokens. Both operands use the same monotonic
    flag configuration. The sum should stay a SimpleToken containing the original
    left and right timeout tokens in order, preserving the left-only CounterToken
    and the right token's empty nested-token list.
    """
    left = TimeoutToken(1, CounterToken(5), **addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, **addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token


@pytest.mark.parametrize(
    'timeout_for_equal_or_bigger_token',
    [
        1,
        2,
    ],
)
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_or_equal_not_monotonic_timeout_token_plus_bigger_or_equal_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_nested_counter_token_at_left(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    """
    Compose different-clock timeout siblings without merging nested left state.

    Left uses timeout 1 and owns the only nested CounterToken, while the right
    timeout is 1 or 2 and has no nested tokens. Different effective monotonic flags
    must keep both TimeoutToken operands as ordered SimpleToken children, preserving
    their identities, timeout values, and the counter nested only inside the left
    timeout.
    """
    left = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs)
    right = TimeoutToken(timeout_for_equal_or_bigger_token, **right_addictional_kwargs)
    token = left + right

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[1]._tokens) == 0
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0] is left
    assert token._tokens[1] is right
    assert token._tokens[0]._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token
