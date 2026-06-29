import sys

import pytest
from full_match import match

from cantok import DefaultToken, ImpossibleCancelError, SimpleToken


def test_dafault_token_is_not_cancelled_by_default():
    token = DefaultToken()

    assert bool(token)
    assert token.cancelled == False
    assert token.is_cancelled() == False
    assert token.keep_on() == True

    token.check()


def test_you_can_set_cancelled_attribute_as_false():
    token = DefaultToken()

    token.cancelled = False

    assert bool(token)
    assert token.cancelled == False
    assert token.is_cancelled() == False
    assert token.keep_on() == True

    token.check()


def test_you_cant_set_true_as_cancelled_attribute():
    token = DefaultToken()

    with pytest.raises(ImpossibleCancelError, match=match('You cannot cancel a default token.')):
        token.cancelled = True

    assert token.cancelled == False


def test_you_cannot_cancel_default_token_by_standard_way():
    token = DefaultToken()

    with pytest.raises(ImpossibleCancelError, match=match('You cannot cancel a default token.')):
        token.cancel()

    assert token.cancelled == False


def test_str_for_default_token():
    assert str(DefaultToken()) == '<DefaultToken (not cancelled)>'


def test_str_with_doc_is_unchanged_for_default_token():
    """
    `doc` must not affect `str(DefaultToken())`.

    The exact `str()` text is covered by `test_str_for_default_token`, so this
    test only compares equivalent default tokens with and without `doc`.
    """
    assert str(DefaultToken(doc='visible-doc')) == str(DefaultToken())


def test_repr_for_default_token():
    """
    `DefaultToken` repr follows the shared `doc` contract.

    Omitted and explicit `None` keep the old repr; valid and escaped text is
    emitted as the final `doc` keyword.
    """
    assert repr(DefaultToken()) == repr(DefaultToken(doc=None)) == 'DefaultToken()'
    assert repr(DefaultToken(doc='d')) == "DefaultToken(doc='d')"
    assert repr(DefaultToken(doc="escaped ' doc")) == 'DefaultToken(doc="escaped \' doc")'


@pytest.mark.skipif(sys.version_info >= (3, 10), reason='Format of this exception messages was changed.')
def test_you_cannot_neste_another_token_to_default_one_old_pythons():
    with pytest.raises(TypeError, match=match('__init__() takes 1 positional argument but 2 were given')):
        DefaultToken(SimpleToken())


@pytest.mark.skipif(sys.version_info < (3, 10), reason='Format of this exception messages was changed.')
def test_you_cannot_neste_another_token_to_default_one_new_pythons():
    with pytest.raises(TypeError, match=match('DefaultToken.__init__() takes 1 positional argument but 2 were given')):
        DefaultToken(SimpleToken())


def test_default_plus_default():
    empty_sum = DefaultToken() + DefaultToken()

    assert isinstance(empty_sum, SimpleToken)
    assert len(empty_sum._tokens) == 0


def test_default_plus_default_plus_default():
    empty_sum = DefaultToken() + DefaultToken() + DefaultToken()

    assert isinstance(empty_sum, SimpleToken)
    assert len(empty_sum._tokens) == 1
    assert isinstance(empty_sum._tokens[0], SimpleToken)
    assert len(empty_sum._tokens[0]._tokens) == 0


def test_default_plus_default_plus_default_preserves_intermediate_simple_token():
    inner_sum = DefaultToken() + DefaultToken()
    total = inner_sum + DefaultToken()

    assert isinstance(total, SimpleToken)
    assert len(total._tokens) == 1
    assert total._tokens[0] is inner_sum

    inner_sum.cancel()

    assert not total


def test_default_token_plus_inline_simple_token():
    total = DefaultToken() + SimpleToken()

    assert isinstance(total, SimpleToken)
    assert len(total._tokens) == 1
    assert isinstance(total._tokens[0], SimpleToken)


def test_default_token_plus_bound_simple_token():
    simple_token = SimpleToken()
    total = DefaultToken() + simple_token

    assert isinstance(total, SimpleToken)
    assert len(total._tokens) == 1
    assert total is not simple_token
    assert total._tokens[0] is simple_token
