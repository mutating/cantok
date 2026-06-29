from sys import version_info
from typing import Optional

if version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

import pytest
from full_match import match

from cantok import CounterToken, SimpleToken


@pytest.mark.mypy_testing
def test_counter_token_accepts_doc_keyword_and_exposes_optional_string_doc():
    """
    `CounterToken` accepts `doc` alongside counter, nesting, and `direct`.

    Positive cases cover `None`, valid text, cancellation state, nested tokens,
    `direct=False`, and the exposed `Optional[str]` attribute type.
    """
    assert_type(CounterToken(1, doc=None).doc, Optional[str])
    CounterToken(1, cancelled=True, doc='d')
    CounterToken(1, SimpleToken(), direct=False, doc='d')


@pytest.mark.mypy_testing
def test_counter_token_rejects_invalid_doc_types():
    """
    `CounterToken` rejects non-`None`, non-string `doc` values statically and at runtime.

    Each invalid value has a mypy expected-error marker and is wrapped in
    `pytest.raises` because the same line is executed as a runtime test.
    """
    expected_message = match('The token description must be a string.')

    with pytest.raises(TypeError, match=expected_message):
        CounterToken(1, doc=1)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        CounterToken(1, doc=True)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        CounterToken(1, doc=[])  # E: [arg-type]


@pytest.mark.mypy_testing
def test_counter_token_nested_positional_arguments_must_be_tokens():
    """
    `CounterToken` treats a positional string after the counter as an invalid nested-token argument in the static type contract.

    The constructor call is intentionally not wrapped in `pytest.raises`
    because runtime token validation for `*tokens` is outside this check.
    """
    CounterToken(1, 'd')  # E: [arg-type]
