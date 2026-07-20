import sys
from typing import Optional

if sys.version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

import pytest
from full_match import match

from cantok import AbstractToken, SimpleToken


@pytest.mark.mypy_testing
def test_abstract_token_exposes_doc_and_check_type_contracts():
    """
    Expose the public type contracts of `doc` and `check()`.

    `doc` is `Optional[str]`. The keyword-only `exception` may be omitted or set
    to `None`, and accepts classes and instances throughout the `BaseException`
    hierarchy. Every `check()` call has inferred type `None`.
    """
    token: AbstractToken = SimpleToken(doc='d')

    assert_type(token.doc, Optional[str])
    assert_type(token.check(), None)
    assert_type(token.check(exception=None), None)
    assert_type(token.check(exception=RuntimeError), None)
    assert_type(token.check(exception=RuntimeError('custom message')), None)
    assert_type(token.check(exception=SystemExit), None)
    assert_type(token.check(exception=SystemExit('custom message')), None)


@pytest.mark.mypy_testing
def test_abstract_token_rejects_invalid_check_exception_types():
    """
    Reject non-exception values and classes statically and at runtime.

    At runtime, both invalid forms raise the documented `ValueError` with its
    exact message.
    """
    token: AbstractToken = SimpleToken()
    expected_message = match('Only an exception instance or an exception class can be passed.')

    with pytest.raises(ValueError, match=expected_message):
        token.check(exception=1)  # E: [arg-type]

    with pytest.raises(ValueError, match=expected_message):
        token.check(exception=object)  # E: [arg-type]


@pytest.mark.mypy_testing
def test_abstract_token_check_exception_is_keyword_only():
    """Reject positional exception overrides statically and at runtime."""
    token: AbstractToken = SimpleToken()

    with pytest.raises(TypeError):
        token.check(ValueError)  # E: [misc]
