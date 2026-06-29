import time
from typing import Any, Callable, Dict, Optional, Union

from cantok import AbstractToken, ConditionToken
from cantok.errors import TimeoutCancellationError


class TimeoutToken(ConditionToken):
    """
    A token that cancels automatically after a specified duration.

    The timeout is measured from the moment the token is created. When the
    deadline is reached, any cancellation check will return True and subsequent
    check() calls will raise TimeoutCancellationError.

    :param timeout: Duration in seconds before cancellation. Must be >= 0.
    :param monotonic: If True, uses time.monotonic_ns() instead of
                      time.perf_counter(), which is unaffected by system
                      clock adjustments. Defaults to False.

    >>> import time
    >>>
    >>> token = TimeoutToken(0.1)
    >>> token.cancelled
    False
    >>> time.sleep(0.2)
    >>> token.cancelled
    True
    """

    exception = TimeoutCancellationError

    def __init__(self, timeout: Union[int, float], *tokens: AbstractToken, cancelled: bool = False, monotonic: bool = False, doc: Optional[str] = None):
        if timeout < 0:
            raise ValueError('You cannot specify a timeout less than zero.')

        self._timeout = timeout
        self._monotonic = monotonic

        timer: Callable[[], Union[int, float]]
        if monotonic:
            timeout *= 1_000_000_000
            timer = time.monotonic_ns
        else:
            timer = time.perf_counter

        start_time: Union[int, float] = timer()
        deadline = start_time + timeout
        def function() -> bool:
            return timer() >= deadline

        super().__init__(function, *tokens, cancelled=cancelled, doc=doc)

    def _text_representation_of_superpower(self) -> str:
        return str(self._timeout)

    def _get_extra_kwargs(self) -> Dict[str, Any]:
        if self._monotonic:
            return {
                'monotonic': self._monotonic,
            }
        return {}

    def _get_superpower_exception_message(self) -> str:
        return f'The timeout of {self._timeout} seconds has expired.'
