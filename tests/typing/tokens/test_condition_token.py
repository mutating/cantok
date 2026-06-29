import sys
from typing import Optional

if sys.version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

import pytest
from full_match import match

from cantok import ConditionToken, SimpleToken


@pytest.mark.mypy_testing
def test_condition_token_accepts_doc_keyword_and_exposes_optional_string_doc():
    """
    `ConditionToken` accepts `doc` alongside its existing keyword options.

    Positive cases cover `None`, valid text, cancellation state, nesting,
    callback options, caching, and the exposed `Optional[str]` attribute type.
    """
    assert_type(ConditionToken(lambda: False, doc=None).doc, Optional[str])
    ConditionToken(lambda: False, cancelled=True, doc='d')
    ConditionToken(lambda: False, SimpleToken(), doc='d')
    ConditionToken(
        lambda: False,
        suppress_exceptions=False,
        default=True,
        before=lambda: None,
        after=lambda: None,
        caching=False,
        doc='d',
    )


@pytest.mark.mypy_testing
def test_condition_token_rejects_invalid_doc_types():
    """
    `ConditionToken` rejects non-`None`, non-string `doc` values statically and at runtime.

    Each invalid value has a mypy expected-error marker and is wrapped in
    `pytest.raises` because the same line is executed as a runtime test.
    """
    expected_message = match('The token description must be a string.')

    with pytest.raises(TypeError, match=expected_message):
        ConditionToken(lambda: False, doc=1)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        ConditionToken(lambda: False, doc=True)  # E: [arg-type]

    with pytest.raises(TypeError, match=expected_message):
        ConditionToken(lambda: False, doc=[])  # E: [arg-type]


@pytest.mark.mypy_testing
def test_condition_token_nested_positional_arguments_must_be_tokens():
    """
    `ConditionToken` treats a positional string after the condition as an invalid nested-token argument in the static type contract.

    The constructor call is intentionally not wrapped in `pytest.raises`
    because runtime token validation for `*tokens` is outside this check.
    """
    ConditionToken(lambda: False, 'd')  # E: [arg-type]
