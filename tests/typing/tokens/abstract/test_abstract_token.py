from sys import version_info
from typing import Optional

if version_info < (3, 11):
    from typing_extensions import assert_type
else:
    from typing import assert_type

import pytest

from cantok import AbstractToken, SimpleToken


@pytest.mark.mypy_testing
def test_abstract_token_exposes_doc_attribute_as_optional_string():
    """
    `AbstractToken` exposes `doc` as an optional string in the type contract.

    A concrete token with `doc` is assigned to an `AbstractToken` variable, and
    `assert_type` fixes the public attribute type.
    """
    token: AbstractToken = SimpleToken(doc='d')

    assert_type(token.doc, Optional[str])
