from cantok import (
    CancellationError,
    ConditionCancellationError,
    ConditionToken,
    CounterCancellationError,
    CounterToken,
    DefaultToken,
    ImpossibleCancelError,
    SimpleToken,
    TimeoutCancellationError,
    TimeoutToken,
)


def test_exception_inheritance_hierarchy():
    """Specialized cancellation errors share the common cancellation base class."""
    assert issubclass(ConditionCancellationError, CancellationError)
    assert issubclass(TimeoutCancellationError, CancellationError)
    assert issubclass(CounterCancellationError, CancellationError)
    assert issubclass(ImpossibleCancelError, CancellationError)


def test_exception_inheritance_hierarchy_from_view_of_tokens_classes():
    """
    Concrete token classes expose their configured cancellation exception types.

    Specialized token exceptions remain compatible with the base error exposed by
    SimpleToken, and DefaultToken exposes the error used by its impossible-cancel
    paths.
    """
    assert issubclass(ConditionToken.exception, SimpleToken.exception)
    assert issubclass(TimeoutToken.exception, SimpleToken.exception)
    assert issubclass(CounterToken.exception, SimpleToken.exception)
    assert issubclass(DefaultToken.exception, SimpleToken.exception)

    assert SimpleToken.exception is CancellationError
    assert ConditionToken.exception is ConditionCancellationError
    assert TimeoutToken.exception is TimeoutCancellationError
    assert CounterToken.exception is CounterCancellationError
    assert DefaultToken.exception is ImpossibleCancelError
