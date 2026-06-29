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
    with pytest.raises(ValueError, match=r'You cannot specify a timeout less than zero\.'):
        TimeoutToken(timeout, **options)


def test_raise_without_first_argument():
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
    sleep_duration = 1
    token = TimeoutToken(sleep_duration)

    start_time = perf_counter()
    token.wait()
    finish_time = perf_counter()

    assert sleep_duration <= finish_time - start_time


def test_timeout_token_plus_simple_token():
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
