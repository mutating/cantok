import pytest

from cantok import DefaultToken, SimpleToken, TimeoutToken


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_default_plus_default_plus_default():
    empty_sum = DefaultToken() + DefaultToken() + DefaultToken()

    assert isinstance(empty_sum, SimpleToken)
    assert len(empty_sum._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_default_token_plus_temp_simple_token():
    empty_sum = DefaultToken() + SimpleToken()

    assert isinstance(empty_sum, SimpleToken)
    assert len(empty_sum._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_temp_default_token_plus_temp_timeout_token():
    token = DefaultToken() + TimeoutToken(1)

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 0


@pytest.mark.skip(reason='Token addition optimization is no longer supported because Python 3.14 changed reference-counting details.')
def test_temp_timeout_token_plus_temp_default_token():
    token = TimeoutToken(1) + DefaultToken()

    assert isinstance(token, TimeoutToken)
    assert token._timeout == 1
    assert len(token._tokens) == 0
