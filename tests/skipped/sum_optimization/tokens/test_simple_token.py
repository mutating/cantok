import pytest

from cantok import ConditionToken, SimpleToken, TimeoutToken


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_2_temp_simple_tokens():
    token = SimpleToken() + SimpleToken()

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_5_temp_simple_tokens():
    token = SimpleToken() + SimpleToken() + SimpleToken() + SimpleToken() + SimpleToken()

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_1_temp_and_1_not_temp_simple_tokens():
    second_token = SimpleToken()
    result = SimpleToken() + second_token

    assert isinstance(result, SimpleToken)
    assert len(result._tokens) == 1
    assert result._tokens[0] is second_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_1_not_temp_and_1_temp_simple_tokens():
    first_token = SimpleToken()
    result = first_token + SimpleToken()

    assert isinstance(result, SimpleToken)
    assert len(result._tokens) == 1
    assert result._tokens[0] is first_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_2_not_temp_simple_tokens_and_one_temp():
    first_token = SimpleToken()
    second_token = SimpleToken()
    result = first_token + second_token + SimpleToken()

    assert isinstance(result, SimpleToken)
    assert len(result._tokens) == 2
    assert result._tokens[0] is first_token
    assert result._tokens[1] is second_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_3_not_temp_simple_tokens():
    first_token = SimpleToken()
    second_token = SimpleToken()
    third_token = SimpleToken()
    result = first_token + second_token + third_token

    assert isinstance(result, SimpleToken)
    assert len(result._tokens) == 3
    assert result._tokens[0] is first_token
    assert result._tokens[1] is second_token
    assert result._tokens[2] is third_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_2_temp_timeout_tokens_throw_temp_simple_tokens():
    token = SimpleToken(TimeoutToken(1)) + SimpleToken(TimeoutToken(2))

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2

    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_2_temp_timeout_tokens_throw_right_temp_simple_token():
    token = TimeoutToken(1) + SimpleToken(TimeoutToken(2))

    assert isinstance(token, TimeoutToken)
    assert len(token._tokens) == 1
    assert len(token._tokens[0]._tokens) == 0
    assert token._timeout == 1
    assert token._tokens[0]._timeout == 2


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_2_temp_timeout_tokens_throw_left_temp_simple_token():
    token = SimpleToken(TimeoutToken(1)) + TimeoutToken(2)

    assert isinstance(token, TimeoutToken)
    assert len(token._tokens) == 1
    assert token._timeout == 2

    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_2_not_temp_timeout_tokens_throw_temp_simple_tokens():
    first_timeout_token = TimeoutToken(1)
    second_timeout_token = TimeoutToken(2)
    token = SimpleToken(first_timeout_token) + SimpleToken(second_timeout_token)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2

    assert token._tokens[0] is first_timeout_token
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert token._tokens[1] is second_timeout_token
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_first_temp_and_second_not_temp_timeout_tokens_throw_temp_simple_tokens():
    second_timeout_token = TimeoutToken(2)
    token = SimpleToken(TimeoutToken(1)) + SimpleToken(second_timeout_token)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2

    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert token._tokens[1] is second_timeout_token
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_first_not_temp_and_second_temp_timeout_tokens_throw_temp_simple_tokens():
    first_timeout_token = TimeoutToken(1)
    token = SimpleToken(first_timeout_token) + SimpleToken(TimeoutToken(2))

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2

    assert token._tokens[0] is first_timeout_token
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 2


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_temp_timeout_token_and_temp_condition_token_throw_temp_simple_tokens():
    token = SimpleToken(TimeoutToken(1)) + SimpleToken(ConditionToken(lambda: False))

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert token

    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert isinstance(token._tokens[1], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_temp_condition_token_and_temp_timeout_token_throw_temp_simple_tokens():
    token = SimpleToken(ConditionToken(lambda: False)) + SimpleToken(TimeoutToken(1))

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert token

    assert isinstance(token._tokens[0], ConditionToken)

    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_not_temp_timeout_token_and_temp_condition_token_throw_temp_simple_tokens():
    timeout_token = TimeoutToken(1)
    token = SimpleToken(timeout_token) + SimpleToken(ConditionToken(lambda: False))

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert token

    assert token._tokens[0] is timeout_token
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert isinstance(token._tokens[1], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_temp_timeout_token_and_not_temp_condition_token_throw_temp_simple_tokens():
    condition_token = ConditionToken(lambda: False)
    token = SimpleToken(TimeoutToken(1)) + SimpleToken(condition_token)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert token

    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert isinstance(token._tokens[1], ConditionToken)
    assert token._tokens[1] is condition_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_not_temp_condition_token_and_temp_timeout_token_throw_temp_simple_tokens():
    condition_token = ConditionToken(lambda: False)
    token = SimpleToken(condition_token) + SimpleToken(TimeoutToken(1))

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert token

    assert isinstance(token._tokens[0], ConditionToken)
    assert token._tokens[0] is condition_token

    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_not_temp_timeout_token_and_not_temp_condition_token_throw_temp_simple_tokens():
    timeout_token = TimeoutToken(1)
    condition_token = ConditionToken(lambda: False)
    token = SimpleToken(timeout_token) + SimpleToken(condition_token)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert token

    assert token._tokens[0] is timeout_token
    assert isinstance(token._tokens[0], TimeoutToken)
    assert token._tokens[0]._timeout == 1

    assert token._tokens[1] is condition_token
    assert isinstance(token._tokens[1], ConditionToken)


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_sum_of_not_temp_condition_token_and_not_temp_timeout_token_throw_temp_simple_tokens():
    timeout_token = TimeoutToken(1)
    condition_token = ConditionToken(lambda: False)
    token = SimpleToken(condition_token) + SimpleToken(timeout_token)

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 2
    assert token

    assert token._tokens[0] is condition_token
    assert isinstance(token._tokens[0], ConditionToken)

    assert token._tokens[1] is timeout_token
    assert isinstance(token._tokens[1], TimeoutToken)
    assert token._tokens[1]._timeout == 1


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_temp_timeout_token_plus_temp_cancelled_simple_token():
    token = TimeoutToken(1) + SimpleToken(cancelled=True)

    assert isinstance(token, SimpleToken)
    assert not token
    assert len(token._tokens) == 0
