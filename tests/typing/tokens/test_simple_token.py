from sys import version_info
from typing import Optional

if version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

import pytest
from full_match import match

from cantok import SimpleToken


@pytest.mark.mypy_testing
def test_simple_token_accepts_doc_keyword_and_exposes_optional_string_doc():
    """
    `SimpleToken` accepts keyword-only `doc` in the typed public API.

    Positive cases cover omitted `doc`, `None`, a valid string, cancellation
    state, nested tokens, and the exposed `Optional[str]` attribute type.
    """
    SimpleToken()
    assert_type(SimpleToken(doc=None).doc, Optional[str])
    SimpleToken(cancelled=True, doc='d')
    SimpleToken(SimpleToken(), doc='d')


@pytest.mark.mypy_testing
def test_simple_token_rejects_invalid_doc_types():
    """
    `SimpleToken` rejects non-`None`, non-string `doc` values statically and at runtime.

    Each invalid value has a mypy expected-error marker and is wrapped in
    `pytest.raises` because the same line is executed as a runtime test.
    """
    expected_message = match('The token description must be a string.')

    with pytest.raises(TypeError, match=expected_message):
        SimpleToken(doc=1)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        SimpleToken(doc=True)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        SimpleToken(doc=[])  # E: [arg-type]


@pytest.mark.mypy_testing
def test_simple_token_nested_positional_arguments_must_be_tokens():
    """
    `SimpleToken` treats a positional string as an invalid nested-token argument in the static type contract.

    The constructor call is intentionally not wrapped in `pytest.raises`
    because runtime token validation for `*tokens` is outside this check.
    """
    SimpleToken('d')  # E: [arg-type]
