import pytest

from cantok import (
    ConditionToken,
    CounterToken,
    SimpleToken,
    TimeoutToken,
)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_timeout_token_plus_temp_simple_token():
    token = TimeoutToken(1) + SimpleToken()

    assert isinstance(token, TimeoutToken)
    assert len(token._tokens) == 0
    assert token._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_quasitemp_timeout_token_plus_temp_simple_token():
    timeout_token = TimeoutToken(1)
    token = timeout_token + SimpleToken()

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0] is timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_timeout_token_plus_not_temp_simple_token():
    simple_token = SimpleToken()
    token = TimeoutToken(1) + simple_token

    assert isinstance(token, TimeoutToken)
    assert token is not simple_token
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], SimpleToken)
    assert token._tokens[0] is simple_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_timeout_token_plus_temp_simple_token_reverse():
    token = SimpleToken() + TimeoutToken(1)

    assert isinstance(token, TimeoutToken)
    assert len(token._tokens) == 0
    assert token._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_quasitemp_timeout_token_plus_temp_simple_token_reverse():
    timeout_token = TimeoutToken(1)
    token = SimpleToken() + timeout_token

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0] is timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_timeout_token_plus_not_temp_simple_token_reverse():
    simple_token = SimpleToken()
    token = simple_token + TimeoutToken(1)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert token is not simple_token
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], SimpleToken)
    assert token._tokens[0] is simple_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag(addictional_kwargs):
    token = TimeoutToken(2, **addictional_kwargs) + TimeoutToken(1, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag(left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(2, **left_addictional_kwargs) + TimeoutToken(1, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_same_monotonic_flag(timeout_for_equal_or_bigger_token, addictional_kwargs):
    token = TimeoutToken(1, **addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(1, **left_addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == timeout_for_equal_or_bigger_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag(addictional_kwargs):
    left_timeout_token = TimeoutToken(2, **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token is not left_timeout_token
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[0] is left_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(2, **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[0] is left_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_same_monotonic_flag(addictional_kwargs):
    left_timeout_token = TimeoutToken(1, **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(1, **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert token._tokens[0] is left_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_same_monotonic_flag(addictional_kwargs):
    right_timeout_token = TimeoutToken(1, **addictional_kwargs)
    token = TimeoutToken(2, **addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(1, **right_addictional_kwargs)
    token = TimeoutToken(2, **left_addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert token._tokens[0] is right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_same_monotonic_flag(addictional_kwargs):
    right_timeout_token = TimeoutToken(2, **addictional_kwargs)
    token = TimeoutToken(1, **addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert token._tokens[0]._timeout == 2
    assert token._tokens[0] is right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_not_same_monotonic_flag(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(2, **right_addictional_kwargs)
    token = TimeoutToken(1, **left_addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[0] is right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right(addictional_kwargs):
    token = TimeoutToken(2, **addictional_kwargs) + TimeoutToken(1, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], ConditionToken)
    assert len(token._tokens[0]._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right(left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(2, **left_addictional_kwargs) + TimeoutToken(1, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert isinstance(token._tokens[0]._tokens[0], ConditionToken)
    assert len(token._tokens[0]._tokens[0]._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right(timeout_for_equal_or_bigger_token, addictional_kwargs):
    token = TimeoutToken(1, **addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(1, **left_addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == timeout_for_equal_or_bigger_token
    assert isinstance(token._tokens[0]._tokens[0], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right(addictional_kwargs):
    left_timeout_token = TimeoutToken(2, **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token is not left_timeout_token
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(2, **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert token._tokens[0] is not left_timeout_token
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2
    assert token._tokens[1] is left_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right(addictional_kwargs):
    left_timeout_token = TimeoutToken(1, **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(1, **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert token._tokens[0] is not left_timeout_token
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1
    assert token._tokens[1] is left_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right(addictional_kwargs):
    right_timeout_token = TimeoutToken(1, ConditionToken(lambda: True), **addictional_kwargs)
    token = TimeoutToken(2, **addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert token is right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(1, ConditionToken(lambda: True), **right_addictional_kwargs)
    token = TimeoutToken(2, **left_addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1
    assert token._tokens[0] is right_timeout_token
    assert isinstance(token._tokens[0]._tokens[0], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right(addictional_kwargs):
    right_timeout_token = TimeoutToken(2, ConditionToken(lambda: True), **addictional_kwargs)
    token = TimeoutToken(1, **addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert token._tokens[0]._timeout == 2
    assert token._tokens[0] is right_timeout_token
    assert isinstance(token._tokens[0]._tokens[0], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(2, ConditionToken(lambda: True), **right_addictional_kwargs)
    token = TimeoutToken(1, **left_addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[0]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 2
    assert token._tokens[0] is right_timeout_token
    assert isinstance(token._tokens[0]._tokens[0], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(addictional_kwargs):
    token = TimeoutToken(2, CounterToken(5), **addictional_kwargs) + TimeoutToken(1, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert isinstance(token._tokens[1], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs) + TimeoutToken(1, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[1]._tokens) == 1
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(timeout_for_equal_or_bigger_token, addictional_kwargs):
    token = TimeoutToken(1, CounterToken(5), **addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert {type(token._tokens[0]), type(token._tokens[1])} == {CounterToken, ConditionToken}


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(addictional_kwargs):
    left_timeout_token = TimeoutToken(2, CounterToken(5), **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token is not left_timeout_token
    assert token._tokens[1] is left_timeout_token
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2
    assert isinstance(token._tokens[1]._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token is not left_timeout_token
    assert token._tokens[1] is left_timeout_token
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2
    assert isinstance(token._tokens[1]._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(addictional_kwargs):
    left_timeout_token = TimeoutToken(1, CounterToken(5), **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, ConditionToken(lambda: True), **addictional_kwargs)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1
    assert isinstance(token._tokens[1]._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, ConditionToken(lambda: True), **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], ConditionToken)
    assert token._tokens[0] is not left_timeout_token
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1
    assert token._tokens[1] is left_timeout_token
    assert isinstance(token._tokens[1]._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(addictional_kwargs):
    right_timeout_token = TimeoutToken(1, ConditionToken(lambda: True), **addictional_kwargs)
    token = TimeoutToken(2, CounterToken(5), **addictional_kwargs) + right_timeout_token

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token._tokens[1]._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert token._tokens[1] is right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(1, ConditionToken(lambda: True), **right_addictional_kwargs)
    token = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token._tokens[1]._timeout == 1
    assert token._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert token._tokens[1] is right_timeout_token
    assert token is not right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(addictional_kwargs):
    right_timeout_token = TimeoutToken(2, ConditionToken(lambda: True), **addictional_kwargs)
    token = TimeoutToken(1, CounterToken(5), **addictional_kwargs) + right_timeout_token

    TimeoutToken(1, CounterToken(5), TimeoutToken(2, ConditionToken(lambda: True)))

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert token._timeout == 1
    assert token._tokens[1]._timeout == 2
    assert token._tokens[1] is right_timeout_token
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert isinstance(token._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_condition_token_at_right_and_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(2, ConditionToken(lambda: True), **right_addictional_kwargs)
    token = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs) + right_timeout_token

    TimeoutToken(1, CounterToken(5), TimeoutToken(2, ConditionToken(lambda: True)))

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert isinstance(token._tokens[1]._tokens[0], ConditionToken)
    assert token._timeout == 1
    assert token._tokens[1]._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 1
    assert len(token._tokens[1]._tokens[0]._tokens) == 0
    assert token._tokens[1] is right_timeout_token
    assert token is not right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag_with_temp_counter_token_at_left(addictional_kwargs):
    token = TimeoutToken(2, CounterToken(5), **addictional_kwargs) + TimeoutToken(1, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag_with_temp_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs) + TimeoutToken(1, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_counter_token_at_left(timeout_for_equal_or_bigger_token, addictional_kwargs):
    token = TimeoutToken(1, CounterToken(5), **addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert token._timeout == 1
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert isinstance(token._tokens[0], CounterToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
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
def test_less_or_equal_temp_not_monotonic_timeout_token_plus_bigger_or_equal_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_counter_token_at_left(timeout_for_equal_or_bigger_token, left_addictional_kwargs, right_addictional_kwargs):
    token = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs) + TimeoutToken(timeout_for_equal_or_bigger_token, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert token._tokens[1]._timeout == timeout_for_equal_or_bigger_token
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_same_monotonic_flag_with_temp_counter_token_at_left(addictional_kwargs):
    left_timeout_token = TimeoutToken(2, CounterToken(5), **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert token is not left_timeout_token
    assert token._tokens[0] is left_timeout_token
    assert token._timeout == 1
    assert token._tokens[0]._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[0]._tokens[0]._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_timeout_token_plus_less_temp_timeout_token_with_not_same_monotonic_flag_with_temp_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(1, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert token is not left_timeout_token
    assert token._tokens[0] is left_timeout_token
    assert token._timeout == 1
    assert token._tokens[0]._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[0]._tokens[0]._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_counter_token_at_left(addictional_kwargs):
    left_timeout_token = TimeoutToken(1, CounterToken(5), **addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, **addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert token is left_timeout_token
    assert token._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_not_monotonic_timeout_token_plus_bigger_temp_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    left_timeout_token = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs)
    token = left_timeout_token + TimeoutToken(2, **right_addictional_kwargs)

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], TimeoutToken)
    assert isinstance(token._tokens[0]._tokens[0], CounterToken)
    assert token._timeout == 2
    assert token._tokens[0]._timeout == 1
    assert token._tokens[0] is left_timeout_token
    assert token is not left_timeout_token
    assert token._timeout == 2
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 1
    assert len(token._tokens[0]._tokens[0]._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_same_monotonic_flag_with_temp_counter_token_at_left(addictional_kwargs):
    right_timeout_token = TimeoutToken(1, **addictional_kwargs)
    token = TimeoutToken(2, CounterToken(5), **addictional_kwargs) + right_timeout_token

    assert isinstance(token, SimpleToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert token._tokens[1] is right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_bigger_temp_timeout_token_plus_less_timeout_token_with_not_same_monotonic_flag_with_temp_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(1, **right_addictional_kwargs)
    token = TimeoutToken(2, CounterToken(5), **left_addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1
    assert token._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert token._tokens[1] is right_timeout_token
    assert token is not right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    'addictional_kwargs',
    [
        {'monotonic': False},
        {},
        {'monotonic': True},
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_same_monotonic_flag_with_temp_counter_token_at_left(addictional_kwargs):
    right_timeout_token = TimeoutToken(2, **addictional_kwargs)
    token = TimeoutToken(1, CounterToken(5), **addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert token._tokens[1]._timeout == 2
    assert token._tokens[1] is right_timeout_token
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
@pytest.mark.parametrize(
    ('left_addictional_kwargs', 'right_addictional_kwargs'),
    [
        ({'monotonic': False}, {'monotonic': True}),
        ({}, {'monotonic': True}),
        ({'monotonic': True}, {'monotonic': False}),
        ({'monotonic': True}, {}),
    ],
)
def test_less_temp_not_monotonic_timeout_token_plus_bigger_not_monotonic_timeout_token_with_not_same_monotonic_flag_with_temp_counter_token_at_left(left_addictional_kwargs, right_addictional_kwargs):
    right_timeout_token = TimeoutToken(2, **right_addictional_kwargs)
    token = TimeoutToken(1, CounterToken(5), **left_addictional_kwargs) + right_timeout_token

    assert isinstance(token, TimeoutToken)
    assert isinstance(token._tokens[0], CounterToken)
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._timeout == 1
    assert token._tokens[1]._timeout == 2
    assert len(token._tokens) == 2
    assert len(token._tokens[0]._tokens) == 0
    assert len(token._tokens[1]._tokens) == 0
    assert token._tokens[1] is right_timeout_token
    assert token is not right_timeout_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_temp_negative_timeout_token_plus_temp_timeout_token():
    token = TimeoutToken(1, cancelled=True) + TimeoutToken(1)

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_temp_timeout_token_plus_temp_negative_timeout_token():
    token = TimeoutToken(1) + TimeoutToken(1, cancelled=True)

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_temp_negative_timeout_token_plus_temp_timeout_token():
    first = TimeoutToken(1, cancelled=True)
    token = first + TimeoutToken(1)

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_temp_timeout_token_plus_temp_negative_timeout_token():
    first = TimeoutToken(1)
    token = first + TimeoutToken(1, cancelled=True)

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_temp_negative_timeout_token_plus_timeout_token():
    first = TimeoutToken(1, cancelled=True)
    second = TimeoutToken(1)
    token = first + second

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_temp_timeout_token_plus_negative_timeout_token():
    first = TimeoutToken(1)
    second = TimeoutToken(1, cancelled=True)
    token = first + second

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_temp_negative_timeout_token_plus_timeout_token():
    second = TimeoutToken(1)
    token = TimeoutToken(1, cancelled=True) + second

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_temp_timeout_token_plus_negative_timeout_token():
    second = TimeoutToken(1, cancelled=True)
    token = TimeoutToken(1) + second

    assert isinstance(token, SimpleToken)
    assert not token
    assert not token._tokens
