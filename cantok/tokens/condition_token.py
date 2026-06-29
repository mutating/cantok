from contextlib import suppress
from typing import Any, Callable, Dict, Optional

from cantok import AbstractToken
from cantok.errors import ConditionCancellationError


class ConditionToken(AbstractToken):
    """
    A token that cancels automatically when a condition function returns True.

    The condition function is evaluated on every cancellation check. Once it
    returns True, the result is cached by default and the token stays cancelled.

    :param function: A callable returning bool. Called on each cancellation check.
    :param suppress_exceptions: If True (default), exceptions from the function
                                are swallowed and treated as the default value.
    :param default: Value to use when the function raises and suppress_exceptions
                    is True. Defaults to False.
    :param before: Callable invoked before the condition function on each check.
    :param after: Callable invoked after the condition function on each check.
    :param caching: If True (default), the token stays cancelled once the
                    condition has returned True, without re-evaluating it.

    >>> items = []
    >>> token = ConditionToken(lambda: len(items) >= 3)
    >>> token.cancelled
    False
    >>> items += [1, 2, 3]
    >>> token.cancelled
    True
    """

    exception = ConditionCancellationError

    def __init__(self, function: Callable[[], bool], *tokens: AbstractToken, cancelled: bool = False, suppress_exceptions: bool = True, default: bool = False, before: Callable[[], Any] = lambda: None, after: Callable[[], Any] = lambda: None, caching: bool = True, doc: Optional[str] = None):  # noqa: PLR0913
        super().__init__(*tokens, cancelled=cancelled, doc=doc)

        self._function = function
        self._before = before
        self._after = after
        self._suppress_exceptions = suppress_exceptions
        self._default = default
        self._caching = caching
        self._was_cancelled_by_condition = False

    def _superpower(self) -> bool:
        if self._was_cancelled_by_condition and self._caching:
            return True

        if not self._suppress_exceptions:
            self._before()
            result = self._run_function()
            self._after()
            return result

        result = self._default

        with suppress(Exception):
            self._before()
        with suppress(Exception):
            result = self._run_function()
        with suppress(Exception):
            self._after()

        return result

    def _run_function(self) -> bool:
        result = self._function()

        if not isinstance(result, bool):
            if not self._suppress_exceptions:
                raise TypeError(f'The condition function can only return a bool value. The passed function returned "{result}" ({type(result).__name__}).')
            return self._default

        if result:
            self._was_cancelled_by_condition = True

        return result

    def _text_representation_of_superpower(self) -> str:
        if hasattr(self._function, '__name__'):
            result = self._function.__name__

            if result == '<lambda>':
                return 'λ'

            return result

        return repr(self._function)

    def _get_extra_kwargs(self) -> Dict[str, Any]:
        result = {}

        if not self._suppress_exceptions:
            result['suppress_exceptions'] = self._suppress_exceptions

        if self._default is not False:
            result['default'] = self._default  # type: ignore[assignment]

        return result

    def _get_superpower_exception_message(self) -> str:
        return 'The cancellation condition was satisfied.'
