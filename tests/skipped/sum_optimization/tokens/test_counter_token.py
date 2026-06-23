import pytest

from cantok import CounterToken, SimpleToken


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_counter_token_plus_temp_simple_token():
    token = CounterToken(0) + SimpleToken()

    assert isinstance(token, CounterToken)
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_quasitemp_counter_token_plus_temp_simple_token():
    counter_token = CounterToken(1)
    token = counter_token + SimpleToken()

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], CounterToken)
    assert token._tokens[0] is counter_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_counter_token_plus_not_temp_simple_token():
    simple_token = SimpleToken()
    token = CounterToken(1) + simple_token

    assert isinstance(token, CounterToken)
    assert token is not simple_token
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], SimpleToken)
    assert token._tokens[0] is simple_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_counter_token_plus_temp_simple_token_reverse():
    token = SimpleToken() + CounterToken(1)

    assert isinstance(token, CounterToken)
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_not_quasitemp_counter_token_plus_temp_simple_token_reverse():
    counter_token = CounterToken(1)
    token = SimpleToken() + counter_token

    assert isinstance(token, SimpleToken)
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], CounterToken)
    assert token._tokens[0] is counter_token


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_quasitemp_counter_token_plus_not_temp_simple_token_reverse():
    simple_token = SimpleToken()
    token = simple_token + CounterToken(1)

    assert isinstance(token, CounterToken)
    assert token is not simple_token
    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], SimpleToken)
    assert token._tokens[0] is simple_token
