import sys

import pytest
from full_match import match

from cantok import DefaultToken, ImpossibleCancelError, SimpleToken


@pytest.mark.parametrize(
    'check',
    [
        lambda token: token.check(),
        lambda token: token.check(exception=None),
        lambda token: token.check(exception=UnicodeDecodeError),
        lambda token: token.check(exception=RuntimeError('unused')),
    ],
)
def test_default_token_is_not_cancelled_by_default(check):
    """`DefaultToken` starts active, and every supported `check()` call returns `None`."""
    token = DefaultToken()

    assert bool(token)
    assert token.cancelled == False
    assert token.is_cancelled() == False
    assert token.keep_on() == True

    assert check(token) is None


@pytest.mark.parametrize(
    'check',
    [
        lambda token: token.check(),
        lambda token: token.check(exception=None),
        lambda token: token.check(exception=UnicodeDecodeError),
        lambda token: token.check(exception=RuntimeError('unused')),
    ],
)
def test_you_can_set_cancelled_attribute_as_false(check):
    """
    Setting `DefaultToken.cancelled` to `False` is a no-op.

    All status APIs still report an active token, and every supported `check()`
    call returns `None`.
    """
    token = DefaultToken()

    token.cancelled = False

    assert bool(token)
    assert token.cancelled == False
    assert token.is_cancelled() == False
    assert token.keep_on() == True

    assert check(token) is None


@pytest.mark.parametrize(
    'check',
    [
        lambda token: token.check(),
        lambda token: token.check(exception=None),
        lambda token: token.check(exception=UnicodeDecodeError),
        lambda token: token.check(exception=RuntimeError('unused')),
    ],
)
def test_you_cant_set_true_as_cancelled_attribute(check):
    """
    Setting `DefaultToken.cancelled` to `True` raises `ImpossibleCancelError`.

    The token remains active, so every supported `check()` call returns `None`.
    """
    token = DefaultToken()

    with pytest.raises(ImpossibleCancelError, match=match('You cannot cancel a default token.')) as exc_info:
        token.cancelled = True

    assert type(exc_info.value) is ImpossibleCancelError
    assert token.cancelled == False
    assert check(token) is None


@pytest.mark.parametrize(
    'check',
    [
        lambda token: token.check(),
        lambda token: token.check(exception=None),
        lambda token: token.check(exception=UnicodeDecodeError),
        lambda token: token.check(exception=RuntimeError('unused')),
    ],
)
def test_you_cannot_cancel_default_token_by_standard_way(check):
    """
    `DefaultToken.cancel()` raises `ImpossibleCancelError`.

    The token remains active, and every supported `check()` call returns `None`.
    """
    token = DefaultToken()

    with pytest.raises(ImpossibleCancelError, match=match('You cannot cancel a default token.')) as exc_info:
        token.cancel()

    assert type(exc_info.value) is ImpossibleCancelError
    assert token.cancelled == False
    assert check(token) is None


def test_str_for_default_token():
    """
    `DefaultToken` stringifies as a regular, never-cancelled token.

    Unlike the shared string test, this pins only the not-cancelled spelling because
    a default token cannot transition to the cancelled state.
    """
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
    """
    DefaultToken rejects nested-token positional arguments with only the old TypeError text.

    This old-Python compatibility case pins the unqualified `__init__()` wording;
    the qualified new-Python wording is covered separately.
    """
    with pytest.raises(TypeError, match=match('__init__() takes 1 positional argument but 2 were given')):
        DefaultToken(SimpleToken())


@pytest.mark.skipif(sys.version_info < (3, 10), reason='Format of this exception messages was changed.')
def test_you_cannot_neste_another_token_to_default_one_new_pythons():
    """
    Guard the Python 3.10+ TypeError for passing a nested token to DefaultToken.

    DefaultToken only accepts keyword-only constructor arguments, so a positional nested token must be rejected with the newer qualified error message.
    """
    with pytest.raises(TypeError, match=match('DefaultToken.__init__() takes 1 positional argument but 2 were given')):
        DefaultToken(SimpleToken())


def test_default_plus_default():
    """Two neutral DefaultToken operands produce an empty SimpleToken sum."""
    empty_sum = DefaultToken() + DefaultToken()

    assert isinstance(empty_sum, SimpleToken)
    assert len(empty_sum._tokens) == 0


def test_default_plus_default_plus_default():
    """Preserve the left-associative empty intermediate token in an inline all-default sum."""
    empty_sum = DefaultToken() + DefaultToken() + DefaultToken()

    assert isinstance(empty_sum, SimpleToken)
    assert len(empty_sum._tokens) == 1
    assert isinstance(empty_sum._tokens[0], SimpleToken)
    assert len(empty_sum._tokens[0]._tokens) == 0


def test_default_plus_default_plus_default_preserves_intermediate_simple_token():
    """
    A default-only SimpleToken intermediate remains a live operand in later sums.

    Direct defaults are filtered from the first sum, but the bound intermediate must
    be preserved by identity in the second sum and propagate its later cancellation.
    """
    inner_sum = DefaultToken() + DefaultToken()
    total = inner_sum + DefaultToken()

    assert isinstance(total, SimpleToken)
    assert len(total._tokens) == 1
    assert total._tokens[0] is inner_sum

    inner_sum.cancel()

    assert not total


def test_default_token_plus_inline_simple_token():
    """
    DefaultToken is neutral when added to an inline SimpleToken.

    The resulting sum is a SimpleToken with exactly one nested operand, and that
    operand is the temporary non-default SimpleToken rather than the neutral default.
    """
    total = DefaultToken() + SimpleToken()

    assert isinstance(total, SimpleToken)
    assert len(total._tokens) == 1
    assert isinstance(total._tokens[0], SimpleToken)


def test_default_token_plus_bound_simple_token():
    """
    Treat a left-hand default token as neutral while preserving a bound simple token.

    The sum is a fresh wrapper whose sole live operand is the preexisting simple token.
    """
    simple_token = SimpleToken()
    total = DefaultToken() + simple_token

    assert isinstance(total, SimpleToken)
    assert len(total._tokens) == 1
    assert total is not simple_token
    assert total._tokens[0] is simple_token
