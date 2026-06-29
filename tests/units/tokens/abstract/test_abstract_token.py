from functools import partial
from threading import Thread
from time import perf_counter, sleep

import pytest
from full_match import match

from cantok import (
    CancellationError,
    ConditionToken,
    CounterToken,
    DefaultToken,
    ImpossibleCancelError,
    SimpleToken,
    TimeoutCancellationError,
    TimeoutToken,
)
from cantok.tokens.abstract.abstract_token import (
    AbstractToken,
    CancelCause,
    CancellationReport,
)

ALL_TOKEN_CLASSES = [SimpleToken, ConditionToken, TimeoutToken, CounterToken]
ALL_SUPERPOWER_TOKEN_CLASSES = [ConditionToken, TimeoutToken, CounterToken]
ALL_ARGUMENTS_FOR_TOKEN_CLASSES = [tuple(), (lambda: False, ), (15, ), (15, )]
ALL_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS = [(lambda: True, ), (0, ), (0, )]
ALL_NOT_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS = [(lambda: False, ), (15, ), (15, )]
ALL_TOKENS_FABRICS = [partial(token_class, *arguments) for token_class, arguments in zip(ALL_TOKEN_CLASSES, ALL_ARGUMENTS_FOR_TOKEN_CLASSES)]
ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER = [partial(token_class, *arguments) for token_class, arguments in zip(ALL_SUPERPOWER_TOKEN_CLASSES, ALL_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS)]
ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER = [partial(token_class, *arguments) for token_class, arguments in zip(ALL_SUPERPOWER_TOKEN_CLASSES, ALL_NOT_CANCELLING_ARGUMENTS_FOR_TOKEN_CLASSES_WITH_SUPERPOWERS)]


def test_cant_instantiate_abstract_token():
    with pytest.raises(TypeError):
        AbstractToken()


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_doc_attribute_stores_optional_description_for_all_tokens(token_fabric):
    """
    Every public token exposes `doc` as the stored description.

    Omitted and explicit `None` values become `None`; a valid string is
    preserved as passed.
    """
    assert token_fabric().doc is None
    assert token_fabric(doc=None).doc is None
    assert token_fabric(doc='d').doc == 'd'


@pytest.mark.parametrize(
    'cancelled_flag',
    [True, False],
)
@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_cancelled_true_as_parameter(token_fabric, cancelled_flag):
    token = token_fabric(cancelled=cancelled_flag)

    assert token.cancelled == cancelled_flag
    assert token.is_cancelled() == cancelled_flag
    assert token.keep_on() == (not cancelled_flag)

    if cancelled_flag:
        with pytest.raises(CancellationError):
            token.check()
    else:
        token.check()


@pytest.mark.parametrize(
    ('first_cancelled_flag', 'second_cancelled_flag', 'expected_value'),
    [
        (True, True, True),
        (False, False, False),
        (False, True, True),
        (True, False, None),
    ],
)
@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_change_attribute_cancelled(token_fabric, first_cancelled_flag, second_cancelled_flag, expected_value):
    token = token_fabric(cancelled=first_cancelled_flag)

    if expected_value is None:
        with pytest.raises(ValueError, match=r'You cannot restore a cancelled token\.'):
            token.cancelled = second_cancelled_flag

    else:
        token.cancelled = second_cancelled_flag
        assert token.cancelled == expected_value
        assert token.is_cancelled() == expected_value
        assert token.keep_on() == (not expected_value)

        if second_cancelled_flag:
            with pytest.raises(CancellationError):
                token.check()
        else:
            token.check()


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_set_cancelled_false_if_this_token_is_not_cancelled_but_nested_token_is(token_fabric):
    token = token_fabric(SimpleToken(cancelled=True))

    with pytest.raises(ValueError, match=match('You cannot restore a cancelled token.')):
        token.cancelled = False


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_repr(token_fabric):
    """
    Every public token has a stable shared repr shape.

    The common assertion checks the repr assembled from superpower text and
    extra kwargs; explicit `doc=None` must keep the same representation.
    """
    token = token_fabric()

    superpower_text = token._text_representation_of_superpower()
    extra_kwargs_text = token._text_representation_of_extra_kwargs()

    elements = ', '.join(x for x in (superpower_text, extra_kwargs_text) if x)

    assert repr(token) == f'{type(token).__name__}({elements})'
    assert repr(token_fabric(doc=None)) == repr(token)


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_repr_with_another_token(token_fabric):
    nested_token = token_fabric()
    token = token_fabric(nested_token)

    superpower_text = token._text_representation_of_superpower()
    extra_kwargs_text = token._text_representation_of_extra_kwargs()

    assert repr(token) == type(token).__name__ + '(' + ('' if not superpower_text else f'{superpower_text}, ') + repr(nested_token) + (', ' + extra_kwargs_text if extra_kwargs_text else '') + ')'


@pytest.mark.parametrize(
    'first_token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
@pytest.mark.parametrize(
    'second_token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_default_token_with_doc_remains_neutral_in_composition(first_token_fabric, second_token_fabric):
    """
    `DefaultToken` remains neutral in composition even when it has `doc`.

    The sum must keep only non-default operands, and its repr must match a
    `SimpleToken` built from the operands that were not filtered out.
    """
    first_token = first_token_fabric(doc='left')
    second_token = second_token_fabric(doc='right')
    expected_tokens = [
        token for token in (first_token, second_token)
        if not isinstance(token, DefaultToken)
    ]

    tokens_sum = first_token + second_token

    assert tokens_sum._tokens == expected_tokens
    assert repr(tokens_sum) == repr(SimpleToken(*expected_tokens))


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_str(token_fabric):
    token = token_fabric()

    assert str(token) == '<' + type(token).__name__ + ' (not cancelled)>'

    token.cancel()

    assert str(token) == '<' + type(token).__name__ + ' (cancelled)>'


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    ('make_token', 'make_token_without_doc'),
    [
        (
            lambda fabric: fabric(doc='visible-doc'),
            lambda fabric: fabric(),
        ),
        (
            lambda fabric: fabric(doc='visible-doc').cancel(),
            lambda fabric: fabric().cancel(),
        ),
        (
            lambda fabric: fabric(
                SimpleToken(cancelled=True, doc='nested-doc'),
                doc='visible-doc',
            ),
            lambda fabric: fabric(SimpleToken(cancelled=True)),
        ),
    ],
)
def test_str_with_doc_is_unchanged(token_fabric, make_token, make_token_without_doc):
    """
    `doc` must not affect `str(token)`.

    The exact `str()` text is covered by `test_str`, so this test only compares
    equivalent regular tokens with and without `doc`.
    """
    token = make_token(token_fabric)
    token_without_doc = make_token_without_doc(token_fabric)

    assert str(token) == str(token_without_doc)


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
)
def test_str_with_doc_is_unchanged_for_superpower_cancelled_tokens(token_fabric):
    """
    `doc` must not affect `str(token)` for superpower cancellation.

    The exact `str()` text is covered by `test_str`, so this test only compares
    equivalent superpower-cancelled tokens with and without `doc`.
    """
    token = token_fabric(doc='visible-doc')
    token_without_doc = token_fabric()

    assert str(token) == str(token_without_doc)


@pytest.mark.parametrize(
    ('doc_kwargs', 'expected_suffix'),
    [
        ({}, ''),
        ({'doc': None}, ''),
        ({'doc': 'manual-doc'}, " Token description: 'manual-doc'."),
        ({'doc': '  manual-doc  '}, " Token description: '  manual-doc  '."),
        ({'doc': "manual ' doc"}, ' Token description: "manual \' doc".'),
    ],
)
@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_manual_cancellation_message_includes_doc_only_when_present(token_fabric, doc_kwargs, expected_suffix):
    """
    Manual cancellation messages append `doc` only when it is present.

    Omitted `doc` and explicit `None` keep the old exact message; valid text
    adds the shared token-description suffix while preserving token identity
    and surrounding whitespace.
    """
    token = token_fabric(**doc_kwargs)
    token.cancel()

    with pytest.raises(CancellationError, match=match('The token has been cancelled.' + expected_suffix)) as exc_info:
        token.check()

    assert type(exc_info.value) is CancellationError
    assert exc_info.value.token is token


@pytest.mark.parametrize(
    ('doc_kwargs', 'expected_suffix'),
    [
        ({}, ''),
        ({'doc': None}, ''),
        ({'doc': 'manual-doc'}, " Token description: 'manual-doc'."),
        ({'doc': "manual ' doc"}, ' Token description: "manual \' doc".'),
    ],
)
@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
)
def test_manual_cancellation_message_overrides_active_superpower_with_optional_doc(token_fabric, doc_kwargs, expected_suffix):
    """
    Manual cancellation has priority over an active superpower.

    Even when a token's superpower would already cancel it, `.cancel()` must make
    `check()` raise the generic manual message with the optional `doc` suffix.
    """
    token = token_fabric(**doc_kwargs)
    token.cancel()

    with pytest.raises(CancellationError, match=match('The token has been cancelled.' + expected_suffix)) as exc_info:
        token.check()

    assert type(exc_info.value) is CancellationError
    assert exc_info.value.token is token


@pytest.mark.parametrize(
    ('doc_kwargs', 'expected_suffix'),
    [
        ({}, ''),
        ({'doc': None}, ''),
        ({'doc': 'type-doc'}, " Token description: 'type-doc'."),
        ({'doc': '  type-doc  '}, " Token description: '  type-doc  '."),
        ({'doc': "type ' doc"}, ' Token description: "type \' doc".'),
    ],
)
def test_superpower_and_impossible_cancel_messages_include_doc_only_when_present(doc_kwargs, expected_suffix):
    """
    Type-specific cancellation messages append `doc` only when it is present.

    The same suffix rule is fixed for Condition, Counter, Timeout, and both
    `DefaultToken` impossible-cancel paths.
    """
    for token_fabric in ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER:
        token = token_fabric(**doc_kwargs)

        with pytest.raises(token.exception, match=match(token._get_superpower_exception_message() + expected_suffix)) as exc_info:
            token.check()

        assert type(exc_info.value) is token.exception
        assert exc_info.value.token is token

    expected_impossible_message = match('You cannot cancel a default token.' + expected_suffix)
    token = DefaultToken(**doc_kwargs)

    with pytest.raises(ImpossibleCancelError, match=expected_impossible_message) as exc_info:
        token.cancel()

    assert type(exc_info.value) is ImpossibleCancelError
    assert exc_info.value.token is token

    token = DefaultToken(**doc_kwargs)

    with pytest.raises(ImpossibleCancelError, match=expected_impossible_message) as exc_info:
        token.cancelled = True

    assert type(exc_info.value) is ImpossibleCancelError
    assert exc_info.value.token is token


@pytest.mark.parametrize(
    'nested_token_fabric',
    [
        partial(SimpleToken, cancelled=True),
        *ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
    ],
)
@pytest.mark.parametrize(
    'doc_case',
    [
        (None, ''),
        ('nested-doc', " Token description: 'nested-doc'."),
        ("nested ' doc", ' Token description: "nested \' doc".'),
    ],
)
@pytest.mark.parametrize(
    'parent_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_nested_cancellation_message_uses_causing_token_doc(parent_token_fabric, nested_token_fabric, doc_case):
    """
    Nested cancellation messages describe the token that caused cancellation.

    Parent `doc` must not leak into the message when a nested token is the
    cancellation source.
    """
    doc, expected_suffix = doc_case
    nested_token = nested_token_fabric(doc=doc)
    token = parent_token_fabric(nested_token, doc='parent-doc')

    with pytest.raises(nested_token.exception, match=match(nested_token._get_superpower_exception_message() + expected_suffix)) as exc_info:
        token.check()

    assert type(exc_info.value) is nested_token.exception
    assert exc_info.value.token is nested_token


@pytest.mark.parametrize(
    'parent_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_parent_manual_cancellation_message_takes_precedence_over_nested_doc(parent_token_fabric):
    """
    Parent manual cancellation takes precedence over a cancelled nested token.

    The raised message must use the parent token and parent `doc`, not the
    already-cancelled nested token description.
    """
    nested_token = SimpleToken(cancelled=True, doc='nested-doc')
    token = parent_token_fabric(nested_token, doc='parent-doc')
    token.cancel()

    with pytest.raises(CancellationError, match=match("The token has been cancelled. Token description: 'parent-doc'.")) as exc_info:
        token.check()

    assert type(exc_info.value) is CancellationError
    assert exc_info.value.token is token


@pytest.mark.parametrize(
    'parent_token_fabric',
    ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
)
def test_parent_superpower_cancellation_message_takes_precedence_over_nested_doc(parent_token_fabric):
    """
    Parent superpower cancellation takes precedence over a cancelled nested token.

    The type-specific message must use the parent token and parent `doc`, not
    the already-cancelled nested token description.
    """
    nested_token = SimpleToken(cancelled=True, doc='nested-doc')
    parent_token = parent_token_fabric(nested_token, doc='parent-doc')

    with pytest.raises(parent_token.exception, match=match(f"{parent_token._get_superpower_exception_message()} Token description: 'parent-doc'.")) as exc_info:
        parent_token.check()

    assert type(exc_info.value) is parent_token.exception
    assert exc_info.value.token is parent_token


@pytest.mark.parametrize(
    'parent_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_cached_nested_cancellation_report_does_not_override_later_parent_manual_cancellation(parent_token_fabric):
    """
    A cached nested report must not hide later parent manual cancellation.

    The test warms the nested-cancellation cache, cancels the parent afterwards,
    and verifies that `check()` reports the parent and its `doc`.
    """
    nested_token = SimpleToken(cancelled=True, doc='nested-doc')
    nested_report = CancellationReport(
        cause=CancelCause.CANCELLED,
        from_token=nested_token,
    )
    token = parent_token_fabric(nested_token, doc='parent-doc')

    assert token.cancelled
    assert token._cached_report == nested_report
    token.cancel()

    with pytest.raises(CancellationError, match=match("The token has been cancelled. Token description: 'parent-doc'.")) as exc_info:
        token.check()

    assert type(exc_info.value) is CancellationError
    assert exc_info.value.token is token


def test_cached_nested_cancellation_report_does_not_override_later_parent_superpower_cancellation(monkeypatch):
    """
    A cached nested report must not hide later parent superpower cancellation.

    After warming the nested-cancellation cache, the test triggers each parent
    superpower and verifies that `check()` reports the parent token with parent
    `doc`.
    """
    nested_token = SimpleToken(cancelled=True, doc='nested-doc')
    nested_report = CancellationReport(
        cause=CancelCause.CANCELLED,
        from_token=nested_token,
    )

    condition_is_satisfied = False
    token = ConditionToken(lambda: condition_is_satisfied, nested_token, doc='parent-doc')

    assert token.cancelled
    assert token._cached_report == nested_report
    condition_is_satisfied = True

    with pytest.raises(token.exception, match=match(f"{token._get_superpower_exception_message()} Token description: 'parent-doc'.")) as exc_info:
        token.check()

    assert type(exc_info.value) is token.exception
    assert exc_info.value.token is token

    token = CounterToken(1, nested_token, doc='parent-doc')

    assert token.cancelled
    assert token._cached_report == nested_report

    with pytest.raises(token.exception, match=match(f"{token._get_superpower_exception_message()} Token description: 'parent-doc'.")) as exc_info:
        token.check()

    assert type(exc_info.value) is token.exception
    assert exc_info.value.token is token

    current_time = 0.0
    monkeypatch.setattr('cantok.tokens.timeout_token.perf_counter', lambda: current_time)
    token = TimeoutToken(1, nested_token, doc='parent-doc')

    assert token.cancelled
    assert token._cached_report == nested_report
    current_time = 2.0

    with pytest.raises(token.exception, match=match(f"{token._get_superpower_exception_message()} Token description: 'parent-doc'.")) as exc_info:
        token.check()

    assert type(exc_info.value) is token.exception
    assert exc_info.value.token is token


@pytest.mark.parametrize(
    'first_token_fabric',
    [
        partial(SimpleToken, cancelled=True),
        *ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
    ],
)
@pytest.mark.parametrize(
    'second_token_fabric',
    [
        partial(SimpleToken, cancelled=True),
        *ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
    ],
)
def test_first_cancelled_nested_token_wins_over_later_sibling(first_token_fabric, second_token_fabric):
    """
    The first cancelled nested token supplies the cancellation message.

    When several nested tokens are already cancelled, `_tokens` order chooses
    the exception class, message, and `doc` suffix.
    """
    first_token = first_token_fabric(doc='first-doc')
    second_token = second_token_fabric(doc='second-doc')
    token = SimpleToken(first_token, second_token)

    with pytest.raises(first_token.exception, match=match(f"{first_token._get_superpower_exception_message()} Token description: 'first-doc'.")) as exc_info:
        token.check()

    assert type(exc_info.value) is first_token.exception
    assert exc_info.value.token is first_token


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_internal_wait_timeout_does_not_inherit_outer_token_doc(token_fabric):
    """
    The internal timeout token created by `wait()` must not inherit outer `doc`.

    A wait timeout still raises the old timeout message and exposes a plain
    internal `TimeoutToken` with `doc is None`.
    """
    with pytest.raises(TimeoutCancellationError, match=match('The timeout of 0 seconds has expired.')) as exc_info:
        token_fabric(doc='outer-doc').wait(step=0, timeout=0)

    timeout_token = exc_info.value.token
    assert repr(timeout_token) == 'TimeoutToken(0)'
    assert timeout_token.doc is None


@pytest.mark.parametrize(
    'doc',
    [
        1,
        True,
        False,
        [],
    ],
)
@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_invalid_doc_type_is_rejected_for_all_tokens(token_fabric, doc):
    """
    Non-`None`, non-string token descriptions are rejected by every public token.

    Each factory receives otherwise valid constructor arguments plus invalid
    `doc`, and must raise the shared `TypeError` message.
    """
    with pytest.raises(TypeError, match=match('The token description must be a string.')):
        token_fabric(doc=doc)


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_empty_doc_is_rejected_for_all_tokens(token_fabric):
    """
    Empty string descriptions are rejected by every public token.

    The test fixes the shared `ValueError` message for `doc=''`.
    """
    with pytest.raises(ValueError, match=match('The token description cannot be empty.')):
        token_fabric(doc='')


@pytest.mark.parametrize(
    'doc',
    [
        ' ',
        '   ',
        '\t\n',
    ],
)
@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_whitespace_only_doc_is_rejected_for_all_tokens(token_fabric, doc):
    """
    Whitespace-only descriptions are rejected with the whitespace-only diagnostic.

    Different whitespace shapes must raise the dedicated `ValueError` message.
    """
    with pytest.raises(ValueError, match=match('The token description cannot be empty (the passed string contains only whitespace characters).')):
        token_fabric(doc=doc)


@pytest.mark.parametrize(
    ('token_fabric', 'expected_repr'),
    [
        (SimpleToken, "SimpleToken(doc='  d  ')"),
        (partial(ConditionToken, lambda: False), "ConditionToken(λ, doc='  d  ')"),
        (partial(CounterToken, 1), "CounterToken(1, doc='  d  ')"),
        (partial(TimeoutToken, 1), "TimeoutToken(1, doc='  d  ')"),
        (DefaultToken, "DefaultToken(doc='  d  ')"),
    ],
)
def test_non_blank_doc_with_surrounding_whitespace_is_allowed_and_preserved(token_fabric, expected_repr):
    """
    Non-blank descriptions with surrounding whitespace stay valid.

    The test verifies both public `doc` storage and repr preservation without
    stripping.
    """
    doc = '  d  '
    token = token_fabric(doc=doc)

    assert token.doc == doc
    assert repr(token) == expected_repr


@pytest.mark.parametrize(
    ('trigger_non_cancellation_error', 'exception_type', 'expected_message'),
    [
        (
            lambda: setattr(SimpleToken(cancelled=True, doc='d'), 'cancelled', False),
            ValueError,
            'You cannot restore a cancelled token.',
        ),
        (
            lambda: SimpleToken(doc='d') + 1,  # type: ignore[operator]
            TypeError,
            'Cancellation Token can only be combined with another Cancellation Token.',
        ),
        (
            lambda: CounterToken(-1, doc='d'),
            ValueError,
            'The counter must be greater than or equal to zero.',
        ),
        (
            lambda: TimeoutToken(-1, doc='d'),
            ValueError,
            'You cannot specify a timeout less than zero.',
        ),
        (
            lambda: ConditionToken(lambda: 'not bool', suppress_exceptions=False, doc='d').cancelled,  # type: ignore[arg-type, return-value]
            TypeError,
            'The condition function can only return a bool value. The passed function returned "not bool" (str).',
        ),
        (
            lambda: SimpleToken(doc='d').wait(step=-1),
            ValueError,
            'The token polling iteration time cannot be less than zero.',
        ),
    ],
)
def test_non_cancellation_errors_do_not_include_doc(trigger_non_cancellation_error, exception_type, expected_message):
    """
    `doc` must not change non-cancellation errors.

    The cases cover explicit cantok errors outside cancellation reporting and
    verifies their old type and message without the `doc` suffix.
    """
    with pytest.raises(exception_type, match=match(expected_message)) as exc_info:
        trigger_non_cancellation_error()

    assert type(exc_info.value) is exception_type


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_bound_tokens(first_token_fabric, second_token_fabric):
    first_token = first_token_fabric()
    second_token = second_token_fabric()

    tokens_sum = first_token + second_token

    assert isinstance(tokens_sum, SimpleToken)
    assert tokens_sum is not first_token
    assert tokens_sum is not second_token
    assert len(tokens_sum._tokens) == 2
    assert tokens_sum._tokens[0] is first_token
    assert tokens_sum._tokens[1] is second_token


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_inline_tokens(first_token_fabric, second_token_fabric):
    tokens_sum = first_token_fabric() + second_token_fabric()

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 2
    assert isinstance(tokens_sum._tokens[0], first_token_fabric.func)
    assert isinstance(tokens_sum._tokens[1], second_token_fabric.func)


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_default_token_and_inline_token(token_fabric):
    tokens_sum = DefaultToken() + token_fabric()

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 1
    assert isinstance(tokens_sum._tokens[0], token_fabric.func)


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_inline_token_and_default_token(token_fabric):
    tokens_sum = token_fabric() + DefaultToken()

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 1
    assert isinstance(tokens_sum._tokens[0], token_fabric.func)


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'third_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_three_tokens_keeps_intermediate_sum(first_token_fabric, second_token_fabric, third_token_fabric):
    first_token = first_token_fabric()
    second_token = second_token_fabric()
    third_token = third_token_fabric()

    tokens_sum = first_token + second_token + third_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 2
    assert isinstance(tokens_sum._tokens[0], SimpleToken)
    assert tokens_sum._tokens[1] is third_token
    assert tokens_sum._tokens[0]._tokens[0] is first_token
    assert tokens_sum._tokens[0]._tokens[1] is second_token


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_empty_simple_token_intermediate_as_regular_operand(token_fabric):
    empty_sum = DefaultToken() + DefaultToken()
    another_token = token_fabric()

    tokens_sum = empty_sum + another_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 2
    assert tokens_sum._tokens[0] is empty_sum
    assert tokens_sum._tokens[1] is another_token
    assert tokens_sum

    empty_sum.cancel()

    assert not tokens_sum


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_cancelled_first_operand_keeps_original_operand(token_fabric):
    cancelled_token = token_fabric(cancelled=True)
    another_token = SimpleToken()

    tokens_sum = cancelled_token + another_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 2
    assert tokens_sum._tokens[0] is cancelled_token
    assert tokens_sum._tokens[1] is another_token
    assert not tokens_sum


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_cancelled_second_operand_keeps_original_operand(token_fabric):
    another_token = SimpleToken()
    cancelled_token = token_fabric(cancelled=True)

    tokens_sum = another_token + cancelled_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 2
    assert tokens_sum._tokens[0] is another_token
    assert tokens_sum._tokens[1] is cancelled_token
    assert not tokens_sum


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_attribute_operand_on_right(stored_token_fabric):
    class Holder:
        def __init__(self, token):
            self.token = token

        def combine(self):
            return DefaultToken() + self.token

    holder = Holder(stored_token_fabric())
    tokens_sum = holder.combine()

    assert tokens_sum

    holder.token.cancel()

    assert not holder.token
    assert not tokens_sum


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_attribute_operand_on_left(stored_token_fabric):
    class Holder:
        def __init__(self, token):
            self.token = token

        def combine(self):
            return self.token + DefaultToken()

    holder = Holder(stored_token_fabric())
    tokens_sum = holder.combine()

    assert tokens_sum

    holder.token.cancel()

    assert not holder.token
    assert not tokens_sum


@pytest.mark.parametrize(
    'extra_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_attribute_operand_with_extra_token(extra_token_fabric, stored_token_fabric):
    class Holder:
        def __init__(self, token):
            self.token = token

        def combine(self, extra_token):
            return extra_token + self.token

    holder = Holder(stored_token_fabric())
    tokens_sum = holder.combine(extra_token_fabric())

    assert tokens_sum

    holder.token.cancel()

    assert not holder.token
    assert not tokens_sum


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_inside_generator_preserves_link_to_attribute_operand(stored_token_fabric):
    class Crawler:
        def __init__(self, token):
            self.token = token

        def go(self, token=DefaultToken()):  # noqa: B008
            token = token + self.token
            for index in range(5):
                yield index, bool(token)

    instance_token = stored_token_fabric()
    crawler = Crawler(instance_token)
    iterator = crawler.go()

    assert next(iterator) == (0, True)

    instance_token.cancel()

    assert not instance_token
    assert next(iterator) == (1, False)


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_property_operand(stored_token_fabric):
    class Holder:
        def __init__(self, token):
            self._token = token

        @property
        def token(self):
            return self._token

        def combine(self):
            return DefaultToken() + self.token

    holder = Holder(stored_token_fabric())
    tokens_sum = holder.combine()

    assert tokens_sum

    holder.token.cancel()

    assert not tokens_sum


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_list_item_operand(stored_token_fabric):
    class Holder:
        def __init__(self, token):
            self.tokens = [token]

        def combine(self):
            return DefaultToken() + self.tokens[0]

    holder = Holder(stored_token_fabric())
    tokens_sum = holder.combine()

    assert tokens_sum

    holder.tokens[0].cancel()

    assert not tokens_sum


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_dict_item_operand(stored_token_fabric):
    class Holder:
        def __init__(self, token):
            self.tokens = {'main': token}

        def combine(self):
            return DefaultToken() + self.tokens['main']

    holder = Holder(stored_token_fabric())
    tokens_sum = holder.combine()

    assert tokens_sum

    holder.tokens['main'].cancel()

    assert not tokens_sum


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_nested_attribute_operand(stored_token_fabric):
    class Child:
        def __init__(self, token):
            self.token = token

    class Holder:
        def __init__(self, child):
            self.child = child

        def combine(self):
            return DefaultToken() + self.child.token

    child = Child(stored_token_fabric())
    holder = Holder(child)
    tokens_sum = holder.combine()

    assert tokens_sum

    child.token.cancel()

    assert not tokens_sum


@pytest.mark.parametrize(
    'stored_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_preserves_link_to_class_attribute_operand(stored_token_fabric):
    class Holder:
        token: AbstractToken

        def combine(self):
            return DefaultToken() + self.token

    Holder.token = stored_token_fabric()
    holder = Holder()
    tokens_sum = holder.combine()

    assert tokens_sum

    Holder.token.cancel()

    assert not tokens_sum


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS_WITH_NOT_CANCELLING_SUPERPOWER,
)
def test_add_another_token_and_bound_simple_token(first_token_fabric):
    simple_token = SimpleToken()
    first_token = first_token_fabric()

    tokens_sum = first_token + simple_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 2
    assert tokens_sum._tokens[0] is first_token
    assert tokens_sum._tokens[1] is simple_token


@pytest.mark.parametrize(
    'second_token_fabric',
    [x for x in ALL_TOKENS_FABRICS if x is not SimpleToken],
)
def test_add_bound_simple_token_and_another_token(second_token_fabric):
    simple_token = SimpleToken()
    second_token = second_token_fabric()

    tokens_sum = simple_token + second_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 2
    assert tokens_sum._tokens[0] is simple_token
    assert tokens_sum._tokens[1] is second_token


@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_tokens_and_first_is_default_token(second_token_fabric):
    first_token = DefaultToken()
    second_token = second_token_fabric()

    tokens_sum = first_token + second_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 1
    assert tokens_sum._tokens[0] is second_token


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_add_tokens_and_second_one_is_default_token(first_token_fabric):
    first_token = first_token_fabric()
    second_token = DefaultToken()

    tokens_sum = first_token + second_token

    assert isinstance(tokens_sum, SimpleToken)
    assert len(tokens_sum._tokens) == 1
    assert tokens_sum._tokens[0] is first_token


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
@pytest.mark.parametrize(
    'another_object',
    [
        1,
        'kek',
        '',
        None,
    ],
)
def test_add_token_and_not_token(token_fabric, another_object):
    with pytest.raises(TypeError, match=r'Cancellation Token can only be combined with another Cancellation Token\.'):
        token_fabric() + another_object

    with pytest.raises(TypeError):
        another_object + token_fabric()


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_check_cancelled_token(token_fabric):
    token = token_fabric()
    token.cancel()

    with pytest.raises(CancellationError):
        token.check()

    with pytest.raises(CancellationError) as exc_info:
        token.check()
    assert type(exc_info.value) is CancellationError
    assert exc_info.value.token is token


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_check_superpower_not_raised(token_fabric):
    token = token_fabric()

    assert token.check() is None


@pytest.mark.parametrize(
    'token_fabric_1',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'token_fabric_2',
    ALL_TOKENS_FABRICS,
)
def test_check_superpower_not_raised_nested(token_fabric_1, token_fabric_2):
    token = token_fabric_1(token_fabric_2())

    assert token.check() is None


@pytest.mark.parametrize(
    'token_fabric_1',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'token_fabric_2',
    ALL_TOKENS_FABRICS,
)
def test_check_cancelled_token_nested(token_fabric_1, token_fabric_2):
    nested_token = token_fabric_1()
    token = token_fabric_2(nested_token)
    nested_token.cancel()

    with pytest.raises(CancellationError):
        token.check()

    with pytest.raises(CancellationError) as exc_info:
        token.check()
    assert type(exc_info.value) is CancellationError
    assert exc_info.value.token is nested_token


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_get_report_not_cancelled(token_fabric):
    token = token_fabric()
    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.NOT_CANCELLED
    assert report.from_token is token


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_get_report_not_cancelled_nested(token_fabric):
    token = token_fabric(token_fabric())
    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.NOT_CANCELLED
    assert report.from_token is token


@pytest.mark.parametrize(
    'token_fabric_1',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'token_fabric_2',
    ALL_TOKENS_FABRICS,
)
def test_get_report_cancelled(token_fabric_1, token_fabric_2):
    nested_token = token_fabric_1()
    token = token_fabric_2(nested_token)
    nested_token.cancel()
    report = token._get_report()

    assert isinstance(report, CancellationReport)
    assert report.cause == CancelCause.CANCELLED
    assert report.from_token is nested_token


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_type_conversion_not_cancelled(token_fabric):
    token = token_fabric()

    assert token
    assert bool(token)


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_type_conversion_cancelled(token_fabric):
    token = token_fabric(cancelled=True)

    assert not token
    assert not bool(token)


@pytest.mark.parametrize(
    ('cancelled_flag_nested_token', 'cancelled_flag_token'),
    [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ],
)
@pytest.mark.parametrize(
    'token_fabric_1',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'token_fabric_2',
    ALL_TOKENS_FABRICS,
)
def test_repr_if_nested_token_is_cancelled(token_fabric_1, token_fabric_2, cancelled_flag_nested_token, cancelled_flag_token):
    nested_token = token_fabric_1(cancelled=cancelled_flag_nested_token)
    token = token_fabric_2(nested_token, cancelled=cancelled_flag_token)

    assert ('cancelled' in repr(token).replace(repr(nested_token), '')) == cancelled_flag_token
    assert ('cancelled' in repr(nested_token)) == cancelled_flag_nested_token


@pytest.mark.parametrize(
    'parameters',
    [
        {'step': -1},
        {'step': -1, 'timeout': -1},
        {'step': -1, 'timeout': 0},
        {'timeout': -1},
        {'step': 1, 'timeout': -1},
        {'step': -1, 'timeout': 1},
        {'step': 2, 'timeout': 1},
    ],
)
@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_wait_wrong_parameters(token_fabric, parameters):
    token = token_fabric()

    with pytest.raises(ValueError, match=r'.'):
        token.wait(**parameters)


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_sync_wait_with_cancel(token_fabric):
    timeout = 0.001
    token = token_fabric()

    def cancel_with_timeout(token):
        sleep(timeout)
        token.cancel()

    start_time = perf_counter()
    thread = Thread(target=cancel_with_timeout, args=(token,))
    thread.start()
    token.wait()
    thread.join()
    finish_time = perf_counter()

    assert finish_time - start_time >= timeout


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
def test_wait_timeout_exception_is_raised_synchronously(token_fabric):
    """
    `wait(timeout=...)` must raise the timeout exception in the caller's frame.

    The old universal sync/async wrapper ran the synchronous wait from a
    finalizer, so `TimeoutCancellationError` could be ignored by Python instead
    of being delivered to the caller. This test waits for a token that will not
    cancel by itself before the auxiliary timeout and verifies that the exception
    is raised directly by `wait()`.
    """
    timeout = 0.0001
    token = token_fabric()

    with pytest.raises(TimeoutToken.exception) as exc_info:
        token.wait(timeout=timeout)

    assert isinstance(exc_info.value.token, TimeoutToken)
    assert exc_info.value.token is not token


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_wait_timeout_returns_when_waited_token_cancellation_wins(token_fabric):
    """
    `wait(timeout=...)` must return normally when waited-token cancellation wins.

    The timeout token created inside `wait()` is only a maximum waiting limit,
    so a cancellation reported by the waited token must make `wait()` complete
    without raising `TimeoutCancellationError`. The test embeds a `CounterToken`
    into each waited token, then uses the cached report to prove that `wait()`
    itself observed the waited-token cancellation without an extra
    `CounterToken` poll in the assertion.
    """
    nested_token = CounterToken(1, direct=False)
    token = token_fabric(nested_token)
    result = token.wait(step=0, timeout=1)

    assert result is None
    assert token._cached_report == CancellationReport(
        cause=CancelCause.SUPERPOWER,
        from_token=nested_token,
    )


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_wait_without_timeout_returns_none(token_fabric):
    """
    Synchronous `wait()` must return `None`.

    A pre-cancelled token makes the wait finish immediately, so the test isolates
    the public return value from timing concerns and fixes the sync-only API:
    callers get completion, not an object to await.
    """
    token = token_fabric(cancelled=True)
    result = token.wait()

    assert result is None


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_insert_default_token_to_another_tokens(token_fabric):
    token = token_fabric(DefaultToken())

    assert not isinstance(token, DefaultToken)
    assert len(token._tokens) == 0


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'action',
    [
        lambda x: x.cancelled,
        lambda x: x.keep_on(),
        lambda x: bool(x),
        lambda x: x.is_cancelled(),
        lambda x: x._get_report(True),
        lambda x: x._get_report(False),
    ],
)
def test_report_cache_is_working_in_simple_case(first_token_fabric, second_token_fabric, action):
    token = first_token_fabric(second_token_fabric(cancelled=True))

    assert token._cached_report is None

    action(token)

    cached_report = token._cached_report

    assert cached_report is not None
    assert isinstance(cached_report, CancellationReport)
    assert cached_report.from_token.is_cancelled()
    assert cached_report.cause == CancelCause.CANCELLED

    assert token._get_report(True) is cached_report
    assert token._get_report(False) is cached_report


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.parametrize(
    'action',
    [
        lambda x: x.cancelled,
        lambda x: x.keep_on(),
        lambda x: bool(x),
        lambda x: x.is_cancelled(),
        lambda x: x._get_report(True),
        lambda x: x._get_report(False),
    ],
)
def test_cache_is_using_after_self_flag(first_token_fabric, second_token_fabric, action):
    token = first_token_fabric(second_token_fabric(cancelled=True))

    action(token)

    cached_report = token._cached_report

    token.cancel()

    for new_report in token._get_report(True), token._get_report(False):
        assert new_report is not cached_report
        assert new_report is not None
        assert isinstance(new_report, CancellationReport)
        assert new_report.from_token.is_cancelled()
        assert new_report.cause == CancelCause.CANCELLED


@pytest.mark.parametrize(
    'first_token_fabric',
    ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
)
@pytest.mark.parametrize(
    'second_token_fabric',
    ALL_TOKENS_FABRICS_WITH_CANCELLING_SUPERPOWER,
)
@pytest.mark.parametrize(
    'action',
    [
        lambda x: x.cancelled,
        lambda x: x.keep_on(),
        lambda x: bool(x),
        lambda x: x.is_cancelled(),
        lambda x: x._get_report(True),
        lambda x: x._get_report(False),
    ],
)
def test_superpower_is_more_important_than_cache(first_token_fabric, second_token_fabric, action):
    token = first_token_fabric(second_token_fabric(cancelled=True))

    for report in token._get_report(True), token._get_report(False):
        assert report is not None
        assert isinstance(report, CancellationReport)
        assert report.from_token is token
        assert report.cause == CancelCause.SUPERPOWER

    action(token)

    for report in token._get_report(True), token._get_report(False):
        assert report is not None
        assert isinstance(report, CancellationReport)
        assert report.from_token is token
        assert report.cause == CancelCause.SUPERPOWER

    token.cancel()

    for report in token._get_report(True), token._get_report(False):
        assert report is not None
        assert isinstance(report, CancellationReport)
        assert report.from_token is token
        assert report.cause == CancelCause.CANCELLED


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
def test_just_neste_simple_token_to_another_token(token_fabric):
    token = token_fabric(SimpleToken())

    assert len(token._tokens) == 1
    assert isinstance(token._tokens[0], SimpleToken)
    assert token
