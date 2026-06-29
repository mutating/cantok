import sys
from typing import Optional

if sys.version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

import pytest
from full_match import match

from cantok import SimpleToken, TimeOutToken, TimeoutToken


@pytest.mark.mypy_testing
def test_timeout_token_accepts_doc_keyword_and_exposes_optional_string_doc():
    """
    `TimeoutToken` accepts `doc` alongside timeout, nesting, and `monotonic`.

    Positive cases cover `None`, valid text, cancellation state, nested tokens,
    `monotonic=True`, the deprecated `TimeOutToken` alias, and the exposed
    `Optional[str]` attribute type.
    """
    assert_type(TimeoutToken(1, doc=None).doc, Optional[str])
    TimeoutToken(1, cancelled=True, doc='d')
    TimeoutToken(1, SimpleToken(), monotonic=True, doc='d')
    assert_type(TimeOutToken(1, doc='d'), TimeoutToken)


@pytest.mark.mypy_testing
def test_timeout_token_rejects_invalid_doc_types():
    """
    `TimeoutToken` rejects non-`None`, non-string `doc` values statically and at runtime.

    Each invalid value has a mypy expected-error marker and is wrapped in
    `pytest.raises` because the same line is executed as a runtime test.
    """
    expected_message = match('The token description must be a string.')

    with pytest.raises(TypeError, match=expected_message):
        TimeoutToken(1, doc=1)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        TimeoutToken(1, doc=True)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        TimeoutToken(1, doc=[])  # E: [arg-type]


@pytest.mark.mypy_testing
def test_timeout_token_nested_positional_arguments_must_be_tokens():
    """
    `TimeoutToken` treats a positional string after the timeout as an invalid nested-token argument in the static type contract.

    The constructor call is intentionally not wrapped in `pytest.raises`
    because runtime token validation for `*tokens` is outside this check.
    """
    TimeoutToken(1, 'd')  # E: [arg-type]
