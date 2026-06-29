from functools import partial

import pytest

from cantok import ConditionCancellationError, ConditionToken, DefaultToken, SimpleToken
from cantok.tokens.abstract.abstract_token import CancelCause, CancellationReport


def test_condition_counter():
    loop_size = 5
    def condition():
        for _number in range(loop_size):
            yield False
        while True:
            yield True

    token = ConditionToken(partial(next, iter(condition())))

    counter = 0
    while not token.cancelled:
        counter += 1

    assert counter == loop_size


def test_condition_false():
    assert ConditionToken(lambda: False).cancelled == False
    assert ConditionToken(lambda: False).is_cancelled() == False
    assert ConditionToken(lambda: False).keep_on() == True


def test_condition_true():
    assert ConditionToken(lambda: True).cancelled == True
    assert ConditionToken(lambda: True).is_cancelled() == True
    assert ConditionToken(lambda: True).keep_on() == False


@pytest.mark.parametrize(('arguments', 'expected_cancelled_status'), [
    ([SimpleToken(), SimpleToken().cancel()], True),
    ([SimpleToken(), ConditionToken(lambda: True)], True),
    ([ConditionToken(lambda: False), ConditionToken(lambda: True)], True),
    ([SimpleToken()], False),
    ([ConditionToken(lambda: False)], False),
    ([SimpleToken().cancel()], True),
    ([ConditionToken(lambda: False).cancel()], True),
    ([ConditionToken(lambda: True).cancel()], True),
    ([SimpleToken(), SimpleToken()], False),
    ([SimpleToken(), SimpleToken(), SimpleToken()], False),
    ([SimpleToken(), SimpleToken(), SimpleToken(), SimpleToken()], False),
    ([ConditionToken(lambda: False), ConditionToken(lambda: False)], False),
    ([ConditionToken(lambda: False), ConditionToken(lambda: False), ConditionToken(lambda: False)], False),
])
def test_just_created_condition_token_with_arguments(arguments, expected_cancelled_status):
    assert ConditionToken(lambda: False, *arguments).cancelled == expected_cancelled_status
    assert ConditionToken(lambda: False, *arguments).is_cancelled() == expected_cancelled_status
    assert ConditionToken(lambda: False, *arguments).keep_on() == (not expected_cancelled_status)


def test_raise_without_first_argument():
    with pytest.raises(TypeError):
        ConditionToken()


def test_suppress_exception_false():
    def condition():
        raise ValueError('error')

    token = ConditionToken(condition, suppress_exceptions=False)

    with pytest.raises(ValueError, match=r'.'):
        _ = token.cancelled


def test_suppress_exception_true():
    def condition():
        raise ValueError

    token = ConditionToken(condition, suppress_exceptions=True)

    assert token.cancelled == False


def test_suppress_exception_default_true():
    def condition():
        raise ValueError

    token = ConditionToken(condition)

    assert token.cancelled == False


def test_condition_function_returning_not_bool_value():
    assert ConditionToken(lambda: 'kek', suppress_exceptions=True).cancelled == False
    assert ConditionToken(lambda: 'kek').cancelled == False

    with pytest.raises(TypeError):
        _ = ConditionToken(lambda: 'kek', suppress_exceptions=False).cancelled


@pytest.mark.parametrize(
    'default',
    [True, False],
)
def test_default_if_exception(default):
    def condition():
        raise ValueError

    token = ConditionToken(condition, suppress_exceptions=True, default=default)

    assert token.cancelled == default


@pytest.mark.parametrize(
    'default',
    [True, False],
)
def test_default_if_not_bool(default):
    def condition():
        return 'kek'

    token = ConditionToken(condition, suppress_exceptions=True, default=default)

    assert token.cancelled == default


def test_check_superpower_raised():
    token = ConditionToken(lambda: True)

    with pytest.raises(ConditionCancellationError):
        token.check()

    with pytest.raises(ConditionCancellationError) as exc_info:
        token.check()
    assert str(exc_info.value) == 'The cancellation condition was satisfied.'
    assert exc_info.value.token is token


def test_check_superpower_raised_nested():
    nested_token = ConditionToken(lambda: True)
    token = SimpleToken(nested_token)

    with pytest.raises(ConditionCancellationError):
        token.check()

    with pytest.raises(ConditionCancellationError) as exc_info:
        token.check()
    assert str(exc_info.value) == 'The cancellation condition was satisfied.'
    assert exc_info.value.token is nested_token
    assert exc_info.value.token.exception is type(exc_info.value)


def test_get_report_cancelled():
    token = ConditionToken(lambda: True)

    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.SUPERPOWER
    assert report.from_token is token


@pytest.mark.parametrize(
    ('cancelled', 'cancelled_nested', 'from_token_is_nested'),
    [
        (True, False, False),
        (False, True, True),
        (True, True, False),
    ],
)
def test_get_report_cancelled_nested(cancelled, cancelled_nested, from_token_is_nested):
    nested_token = ConditionToken(lambda: cancelled_nested)
    token = ConditionToken(lambda: cancelled, nested_token)

    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.SUPERPOWER
    if from_token_is_nested:
        assert report.from_token is nested_token
    else:
        assert report.from_token is token


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'suppress_exceptions': True},
        {'suppress_exceptions': False},
    ],
)
def test_order_of_callbacks(options):
    lst = []
    token = ConditionToken(lambda: lst.append(2) is not None, before=lambda: lst.append(1), after=lambda: lst.append(3), **options)

    token.check()

    assert lst == [1, 2, 3]


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'suppress_exceptions': True},
    ],
)
def test_raise_suppressed_exception_in_before_callback(options):
    lst = []

    def before_callback():
        lst.append(1)
        raise ValueError

    token = ConditionToken(lambda: lst.append(2) is not None, before=before_callback, after=lambda: lst.append(3), **options)

    token.check()

    assert lst == [1, 2, 3]


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'suppress_exceptions': True},
    ],
)
def test_raise_suppressed_exception_in_after_callback(options):
    lst = []

    def after_callback():
        lst.append(3)
        raise ValueError

    token = ConditionToken(lambda: lst.append(2) is not None, before=lambda: lst.append(1), after=after_callback, **options)

    token.check()

    assert lst == [1, 2, 3]


def test_raise_not_suppressed_exception_in_before_callback():
    lst = []

    token = ConditionToken(lambda: lst.append(2) is not None, before=lambda: 1 / 0, suppress_exceptions=False)

    with pytest.raises(ZeroDivisionError):
        token.check()

    assert not lst


def test_raise_not_suppressed_exception_in_after_callback():
    lst = []

    token = ConditionToken(lambda: lst.append(2) is not None, before=lambda: lst.append(1), after=lambda: 1 / 0, suppress_exceptions=False)

    with pytest.raises(ZeroDivisionError):
        token.check()

    assert lst == [1, 2]


@pytest.mark.parametrize(
    'options',
    [
        {},
        {'caching': True},
        {'caching': False},
    ],
)
def test_cached_condition_cancelling(options):
    counter = 0

    def condition():
        nonlocal counter
        counter +=1
        return counter == 3

    token = ConditionToken(condition, **options)

    token.wait()

    if options.get('caching', True):
        assert counter == 3
        assert token.cancelled == True
        assert counter == 3
        with pytest.raises(ConditionCancellationError):
            token.check()
        assert counter == 3
        assert token.cancelled == True
        assert counter == 3
    else:
        assert counter == 3
        assert token.cancelled == False
        assert counter == 4
        token.check()
        assert counter == 5
        assert token.cancelled == False
        assert counter == 6


def test_condition_token_plus_simple_token():
    simple_token = SimpleToken()
    condition_token = ConditionToken(lambda: False)
    token = condition_token + simple_token

    assert isinstance(token, SimpleToken)
    assert token is not simple_token
    assert len(token._tokens) == 2
    assert isinstance(token._tokens[0], ConditionToken)
    assert token._tokens[0] is condition_token
    assert token._tokens[1] is simple_token


def test_simple_token_plus_condition_token():
    simple_token = SimpleToken()
    condition_token = ConditionToken(lambda: False)
    token = simple_token + condition_token

    assert isinstance(token, SimpleToken)
    assert token is not simple_token
    assert len(token._tokens) == 2
    assert isinstance(token._tokens[1], ConditionToken)
    assert token._tokens[1] is condition_token
    assert token._tokens[0] is simple_token


def test_condition_function_is_more_important_than_cache():
    flag = False
    inner_token = SimpleToken(cancelled=True)
    token = ConditionToken(lambda: flag, inner_token)

    for report in token._get_report(True), token._get_report(False):
        assert report is not None
        assert isinstance(report, CancellationReport)
        assert report.from_token is inner_token
        assert report.cause == CancelCause.CANCELLED

    flag = True

    for report in token._get_report(True), token._get_report(False):
        assert report is not None
        assert isinstance(report, CancellationReport)
        assert report.from_token is token
        assert report.cause == CancelCause.SUPERPOWER


def test_zero_condition_token_report_is_about_superpower():
    for report in ConditionToken(lambda: True)._get_report(True), ConditionToken(lambda: True)._get_report(False):
        assert report.cause == CancelCause.SUPERPOWER


def test_creating_condition_token_with_no_suppress_exceptions_is_not_calling_condition():
    calls = []

    ConditionToken(lambda: calls.append(True) is None, suppress_exceptions=False)

    assert not calls


def test_repr_of_condition_token():
    """
    `ConditionToken` repr reflects function text, options, state, and nesting.

    The same contract is checked with `doc`: `None` keeps the old repr, valid
    text is appended last, escaped text is represented safely, and
    `DefaultToken` remains neutral when nested.
    """
    def function(): return False

    assert repr(ConditionToken(lambda: False)) == 'ConditionToken(λ)'
    assert repr(ConditionToken(lambda: False, ConditionToken(lambda: False))) == 'ConditionToken(λ, ConditionToken(λ))'
    assert repr(ConditionToken(lambda: False, ConditionToken(lambda: False), doc=None)) == 'ConditionToken(λ, ConditionToken(λ))'
    assert repr(ConditionToken(lambda: False, ConditionToken(lambda: False, doc='nested'), doc='parent')) == "ConditionToken(λ, ConditionToken(λ, doc='nested'), doc='parent')"
    assert repr(ConditionToken(lambda: False, DefaultToken(doc='neutral'), doc='parent')) == "ConditionToken(λ, doc='parent')"
    assert repr(ConditionToken(lambda: False, suppress_exceptions=True)) == 'ConditionToken(λ)'
    assert repr(ConditionToken(lambda: False, suppress_exceptions=False)) == 'ConditionToken(λ, suppress_exceptions=False)'
    assert repr(ConditionToken(lambda: False, default=False)) == 'ConditionToken(λ)'
    assert repr(ConditionToken(lambda: False, default=True)) == 'ConditionToken(λ, default=True)'
    assert repr(ConditionToken(lambda: False, suppress_exceptions=False, default=True)) == 'ConditionToken(λ, suppress_exceptions=False, default=True)'
    assert repr(ConditionToken(lambda: False, suppress_exceptions=False, default=True, cancelled=True)) == 'ConditionToken(λ, cancelled=True, suppress_exceptions=False, default=True)'
    assert repr(ConditionToken(lambda: False, suppress_exceptions=False, default=True, cancelled=True, doc=None)) == 'ConditionToken(λ, cancelled=True, suppress_exceptions=False, default=True)'
    assert repr(ConditionToken(lambda: False, doc='d')) == "ConditionToken(λ, doc='d')"
    assert repr(ConditionToken(lambda: True, doc='d')) == "ConditionToken(λ, doc='d')"
    assert repr(ConditionToken(lambda: False, cancelled=True, doc='d')) == "ConditionToken(λ, cancelled=True, doc='d')"
    assert repr(ConditionToken(lambda: True, suppress_exceptions=False, default=True, doc='d')) == "ConditionToken(λ, suppress_exceptions=False, default=True, doc='d')"
    assert repr(ConditionToken(lambda: False, doc="escaped ' doc")) == 'ConditionToken(λ, doc="escaped \' doc")'

    assert repr(ConditionToken(function)) == 'ConditionToken(function)'
    assert repr(ConditionToken(function, ConditionToken(function))) == 'ConditionToken(function, ConditionToken(function))'
    assert repr(ConditionToken(function, suppress_exceptions=True)) == 'ConditionToken(function)'
    assert repr(ConditionToken(function, suppress_exceptions=False)) == 'ConditionToken(function, suppress_exceptions=False)'
    assert repr(ConditionToken(function, default=False)) == 'ConditionToken(function)'
    assert repr(ConditionToken(function, default=True)) == 'ConditionToken(function, default=True)'
    assert repr(ConditionToken(function, suppress_exceptions=False, default=True)) == 'ConditionToken(function, suppress_exceptions=False, default=True)'

    assert repr(ConditionToken(function, suppress_exceptions=False, default=True, cancelled=True)) == 'ConditionToken(function, cancelled=True, suppress_exceptions=False, default=True)'
    assert repr(ConditionToken(function, suppress_exceptions=False, default=True, cancelled=True, doc='d')) == "ConditionToken(function, cancelled=True, suppress_exceptions=False, default=True, doc='d')"


def test_repr_for_class_based_function():
    class SomeChecker:
        def __call__(self) -> bool:
            return True

        def __str__(self) -> str:
            return 'str_string'

        def __repr__(self) -> str:
            return 'repr_string'

    assert repr(ConditionToken(SomeChecker())) == 'ConditionToken(repr_string)'
