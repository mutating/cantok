import pytest

from cantok import ConditionToken, SimpleToken


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_condition_token_plus_temp_simple_token():
    token = ConditionToken(lambda: False) + SimpleToken()

    assert isinstance(token, ConditionToken)
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_quasitemp_condition_token_plus_temp_simple_token():
    condition_token = ConditionToken(lambda: False)
    token = condition_token + SimpleToken()

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], ConditionToken)
    assert token._tokens[0] is condition_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_condition_token_plus_not_temp_simple_token():
    simple_token = SimpleToken()
    token = ConditionToken(lambda: False) + simple_token

    assert isinstance(token, ConditionToken)
    assert token is not simple_token
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], SimpleToken)
    assert token._tokens[0] is simple_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_condition_token_plus_temp_simple_token_reverse():
    token = SimpleToken() + ConditionToken(lambda: False)

    assert isinstance(token, ConditionToken)
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_quasitemp_condition_token_plus_temp_simple_token_reverse():
    condition_token = ConditionToken(lambda: False)
    token = SimpleToken() + condition_token

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], ConditionToken)
    assert token._tokens[0] is condition_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_condition_token_plus_not_temp_simple_token_reverse():
    simple_token = SimpleToken()
    token = simple_token + ConditionToken(lambda: False)

    assert isinstance(token, ConditionToken)
    assert token is not simple_token
    assert len(token._tokens) == 1
    assert token._tokens[0] is simple_token
