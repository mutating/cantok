from functools import partial

import pytest

from cantok import (
    ConditionToken,
    CounterToken,
    SimpleToken,
    TimeoutToken,
)

ALL_TOKEN_CLASSES = [SimpleToken, ConditionToken, TimeoutToken, CounterToken]
ALL_SUPERPOWER_TOKEN_CLASSES = [ConditionToken, TimeoutToken, CounterToken]
ALL_ARGUMENTS_FOR_TOKEN_CLASSES = [tuple(), (lambda: False, ), (15, ), (15, )]
ALL_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS = [(lambda: True, ), (0, ), (0, )]
ALL_NOT_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS = [(lambda: False, ), (15, ), (15, )]
ALL_TOKENS_FABRICS = [partial(token_class, *arguments) for token_class, arguments in zip(ALL_TOKEN_CLASSES, ALL_ARGUMENTS_FOR_TOKEN_CLASSES)]
ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER = [partial(token_class, *arguments) for token_class, arguments in zip(ALL_SUPERPOWER_TOKEN_CLASSES, ALL_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS)]
ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER = [partial(token_class, *arguments) for token_class, arguments in zip(ALL_SUPERPOWER_TOKEN_CLASSES, ALL_NOT_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS)]


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('first_token_class', 'first_arguments'),
    [
        (TimeoutToken, [15]),
        (ConditionToken, [lambda: False]),
        (CounterToken, [15]),
    ],
)
@pytest.mark.parametrize(
    ('second_token_class', 'second_arguments'),
    [
        (TimeoutToken, [15]),
        (ConditionToken, [lambda: False]),
        (CounterToken, [15]),
    ],
)
def test_add_temp_tokens(first_token_class, second_token_class, first_arguments, second_arguments):
    tokens_sum = first_token_class(*first_arguments) + second_token_class(*second_arguments)

    if not (first_token_class is TimeoutToken and second_token_class is TimeoutToken):
        assert isinstance(tokens_sum, first_token_class)
        assert len(tokens_sum._tokens) == 1
        assert isinstance(tokens_sum._tokens[0], second_token_class)
        assert len(tokens_sum._tokens[0]._tokens) == 0
    else:
        assert isinstance(tokens_sum, TimeoutToken)
        assert len(tokens_sum._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('first_token_class', 'first_arguments'),
    [
        (TimeoutToken, [15]),
        (ConditionToken, [lambda: False]),
        (CounterToken, [15]),
    ],
)
@pytest.mark.parametrize(
    ('second_token_class', 'second_arguments'),
    [
        (TimeoutToken, [15]),
        (ConditionToken, [lambda: False]),
        (CounterToken, [15]),
    ],
)
def test_add_not_temp_token_and_temp_token(first_token_class, second_token_class, first_arguments, second_arguments):
    first_token = first_token_class(*first_arguments)
    tokens_sum = first_token + second_token_class(*second_arguments)

    if first_token_class is TimeoutToken and second_token_class is TimeoutToken:
        assert tokens_sum is first_token
        assert not tokens_sum._tokens
    else:
        assert isinstance(tokens_sum, second_token_class)
        assert len(tokens_sum._tokens) == 1
        assert isinstance(tokens_sum._tokens[0], first_token_class)
        assert len(tokens_sum._tokens[0]._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('first_token_class', 'first_arguments'),
    [
        (TimeoutToken, [15]),
        (ConditionToken, [lambda: False]),
        (CounterToken, [15]),
    ],
)
@pytest.mark.parametrize(
    ('second_token_class', 'second_arguments'),
    [
        (TimeoutToken, [15]),
        (ConditionToken, [lambda: False]),
        (CounterToken, [15]),
    ],
)
def test_add_temp_token_and_not_temp_token(first_token_class, second_token_class, first_arguments, second_arguments):
    second_token = second_token_class(*second_arguments)
    tokens_sum = first_token_class(*first_arguments) + second_token

    if first_token_class is TimeoutToken and second_token_class is TimeoutToken:
        assert isinstance(tokens_sum, TimeoutToken)
        assert len(tokens_sum._tokens) == 0
    else:
        assert isinstance(tokens_sum, first_token_class)
        assert len(tokens_sum._tokens) == 1
        assert isinstance(tokens_sum._tokens[0], second_token_class)
        assert len(tokens_sum._tokens[0]._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER,
)
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER,
)
@pytest.mark.parametrize(
    'third_token_fabric',
    ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER,
)
def test_add_three_tokens_except_simple_token(first_token_fabric, second_token_fabric, third_token_fabric):
    first_token = first_token_fabric()
    second_token = second_token_fabric()
    third_token = third_token_fabric()

    tokens_sum = first_token + second_token + third_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 3
    assert tokens_sum._tokens[0] is first_token
    assert tokens_sum._tokens[1] is second_token
    assert tokens_sum._tokens[2] is third_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER,
)
def test_add_another_token_and_temp_simple_token(first_token_fabric):
    first_token = first_token_fabric()

    tokens_sum = first_token + SimpleToken()

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 1
    assert tokens_sum._tokens[0] is first_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER,
)
def test_add_temp_simple_token_and_another_token(second_token_fabric):
    second_token = second_token_fabric()

    tokens_sum = SimpleToken() + second_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 1
    assert tokens_sum._tokens[0] is second_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_any_token_plus_temp_cancelled_simple_token_gives_cancelled_simple_token(token_fabric):
    token = token_fabric() + SimpleToken(cancelled=True)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 0
    assert not token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_any_token_plus_cancelled_simple_token_gives_cancelled_simple_token(token_fabric):
    simple_token = SimpleToken(cancelled=True)
    token = token_fabric() + simple_token

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 0
    assert not token
