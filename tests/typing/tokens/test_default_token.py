import sys
from typing import Optional

if sys.version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

import pytest
from full_match import match

from cantok import DefaultToken


@pytest.mark.mypy_testing
def test_default_token_accepts_doc_keyword_and_exposes_optional_string_doc():
    """
    `DefaultToken` accepts only keyword `doc` in the typed public API.

    Positive cases cover omitted `doc`, `None`, valid text, and the exposed
    `Optional[str]` attribute type.
    """
    DefaultToken()
    assert_type(DefaultToken(doc='d').doc, Optional[str])
    DefaultToken(doc=None)


@pytest.mark.mypy_testing
def test_default_token_rejects_invalid_doc_types():
    """
    `DefaultToken` rejects non-`None`, non-string `doc` values statically and at runtime.

    Each invalid value has a mypy expected-error marker and is wrapped in
    `pytest.raises` because the same line is executed as a runtime test.
    """
    expected_message = match('The token description must be a string.')

    with pytest.raises(TypeError, match=expected_message):
        DefaultToken(doc=1)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        DefaultToken(doc=True)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        DefaultToken(doc=[])  # E: [arg-type]


@pytest.mark.mypy_testing
def test_default_token_rejects_positional_doc_arguments():
    """
    `DefaultToken` rejects positional `doc`-like arguments.

    Unlike regular token nesting checks, these calls fail both statically and
    at runtime because `DefaultToken` does not accept positional arguments.
    """
    with pytest.raises(TypeError):
        DefaultToken('d')  # E: [misc]

    with pytest.raises(TypeError):
        DefaultToken(None)  # E: [misc]
