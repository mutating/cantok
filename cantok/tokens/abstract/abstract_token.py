from abc import ABC, abstractmethod
from threading import RLock
from time import sleep
from typing import Any, Dict, List, Optional, Union

from cantok.errors import CancellationError
from cantok.tokens.abstract.cancel_cause import CancelCause
from cantok.tokens.abstract.report import CancellationReport


class AbstractToken(ABC):
    """
    Abstract base class for all cancellation tokens.

    A cancellation token represents a signal that can be used to cooperatively
    cancel a long-running operation. Most subclasses add an automatic cancellation
    condition (superpower) evaluated on every check; SimpleToken and DefaultToken
    rely on manual cancellation only.

    Tokens can be composed with the + operator: the resulting token is cancelled
    when any of the combined tokens is cancelled.

    Use AbstractToken as a type hint when a function accepts any token type.
    Pass DefaultToken() as the default to make the token optional:

    >>> def run(token: AbstractToken = DefaultToken()) -> bool:
    ...     return token.keep_on()
    >>> run()                        # DefaultToken never cancels
    True
    >>> run(SimpleToken().cancel())  # cancelled token passed explicitly
    False

    The idiomatic loop pattern:

    >>> token = SimpleToken()
    >>> while token:
    ...     ...  # loop exits when token is cancelled
    """

    exception = CancellationError
    _rollback_if_nondirect_polling = False

    def __init__(self, *tokens: 'AbstractToken', cancelled: bool = False) -> None:
        from cantok import DefaultToken  # noqa: PLC0415

        self._cached_report: Optional[CancellationReport] = None
        self._cancelled: bool = cancelled
        self._tokens: List[AbstractToken] = [
            token for token in tokens if not isinstance(token, DefaultToken)
        ]

        self._lock: RLock = RLock()

    def __repr__(self) -> str:
        chunks = []
        superpower = self._text_representation_of_superpower()
        if superpower:
            chunks.append(superpower)
        other_tokens = ', '.join([repr(x) for x in self._tokens])
        if other_tokens:
            chunks.append(other_tokens)
        report = self._get_report(direct=False)
        if report.cause == CancelCause.NOT_CANCELLED:
            extra_kwargs = {}
        elif report.from_token is self and report.cause == CancelCause.CANCELLED:
            extra_kwargs = {'cancelled': True}
        else:
            extra_kwargs = {}
        extra_kwargs.update(**(self._get_extra_kwargs()))
        text_representation_of_extra_kwargs = self._text_representation_of_kwargs(
            **extra_kwargs,
        )
        if text_representation_of_extra_kwargs:
            chunks.append(text_representation_of_extra_kwargs)

        glued_chunks = ', '.join(chunks)
        return f'{type(self).__name__}({glued_chunks})'

    def __str__(self) -> str:
        cancelled_flag = (
            'cancelled' if self.is_cancelled(direct=False) else 'not cancelled'
        )
        return f'<{type(self).__name__} ({cancelled_flag})>'

    def __add__(self, item: 'AbstractToken') -> 'AbstractToken':
        if not isinstance(item, AbstractToken):
            raise TypeError(
                'Cancellation Token can only be combined with another Cancellation Token.',
            )

        from cantok import SimpleToken  # noqa: PLC0415

        return SimpleToken(self, item)

    def __bool__(self) -> bool:
        return self.keep_on()

    @property
    def cancelled(self) -> bool:
        """
        Whether the token is currently cancelled.

        Evaluated dynamically on each access, taking into account the token's own
        cancellation rules and all embedded tokens. Setting to True cancels the token;
        setting to False on an already cancelled token raises ValueError.

        >>> token = SimpleToken()
        >>> token.cancelled
        False
        >>> token.cancel()
        >>> token.cancelled
        True
        """
        return self.is_cancelled()

    @cancelled.setter
    def cancelled(self, new_value: bool) -> None:
        with self._lock:
            if new_value == True:
                self._cancelled = True
            elif self.is_cancelled():
                raise ValueError('You cannot restore a cancelled token.')

    def keep_on(self) -> bool:
        """
        Returns True if the token is not cancelled, False otherwise.
        The opposite of is_cancelled().

        >>> token = SimpleToken()
        >>> token.keep_on()
        True
        >>> token.cancel()
        >>> token.keep_on()
        False
        """
        return not self.is_cancelled()

    def is_cancelled(self, direct: bool = True) -> bool:
        """
        Returns True if the token is cancelled, False otherwise.

        :param direct: When False, tokens with rollback behaviour (e.g. CounterToken
                       with direct=True) do not apply their side effects while being
                       polled indirectly through a parent token. Defaults to True.

        >>> token = SimpleToken()
        >>> token.is_cancelled()
        False
        >>> token.cancel()
        >>> token.is_cancelled()
        True
        """
        return self._get_report(direct=direct).cause != CancelCause.NOT_CANCELLED

    def wait(
        self,
        step: Union[int, float] = 0.0001,
        timeout: Optional[Union[int, float]] = None,
    ) -> None:
        """
        Waits until the token is cancelled.

        Blocks the current thread until the token is cancelled.

        :param step: Interval between status checks, in seconds. Defaults to 0.0001.
        :param timeout: Maximum time to wait, in seconds. If exceeded,
                        raises TimeoutCancellationError. Defaults to None (no limit).

        >>> token = TimeoutToken(5)
        >>> token.wait()   # blocks for ~5 seconds, then returns
        """
        if step < 0:
            raise ValueError(
                'The token polling iteration time cannot be less than zero.',
            )
        if timeout is not None and timeout < 0:
            raise ValueError('The total timeout of waiting cannot be less than zero.')
        if timeout is not None and step > timeout:
            raise ValueError(
                'The total timeout of waiting cannot be less than the time of one iteration of the token polling.',
            )

        if timeout is None:
            from cantok import SimpleToken  # noqa: PLC0415

            token: AbstractToken = SimpleToken()
        else:
            from cantok import TimeoutToken  # noqa: PLC0415

            token = TimeoutToken(timeout)

        token_for_wait = self + token

        while token_for_wait:
            sleep(step)

        token.check()

    def cancel(self) -> 'AbstractToken':
        """
        Cancels the token. Returns the token itself to allow method chaining.

        Cancellation is irreversible: once cancelled, the token cannot be restored.

        >>> token = SimpleToken()
        >>> token.cancel()
        >>> token.cancelled
        True
        """
        self._cancelled = True
        return self

    def check(self) -> None:
        """
        Raises an exception if the token is cancelled; does nothing otherwise.

        The exception type depends on the cancellation cause:
        - Manual cancellation via cancel() raises CancellationError.
        - Automatic cancellation by a specific token type raises the corresponding
          subclass (e.g. TimeoutCancellationError for TimeoutToken).

        >>> token = SimpleToken()
        >>> token.check()   # nothing happens
        >>> token.cancel()
        >>> token.check()   # raises CancellationError
        """
        with self._lock:
            report = self._get_report()

            if report.cause == CancelCause.CANCELLED:
                report.from_token._raise_cancelled_exception()

            elif report.cause == CancelCause.SUPERPOWER:
                report.from_token._raise_superpower_exception()

    def _get_report(self, direct: bool = True) -> CancellationReport:
        if self._cancelled:
            return CancellationReport(
                cause=CancelCause.CANCELLED,
                from_token=self,
            )
        if self._check_superpower(direct):
            return CancellationReport(
                cause=CancelCause.SUPERPOWER,
                from_token=self,
            )
        if self._cached_report is not None:
            return self._cached_report

        for token in self._tokens:
            report = token._get_report(direct=False)
            if report.cause != CancelCause.NOT_CANCELLED:
                self._cached_report = report
                return report

        return CancellationReport(
            cause=CancelCause.NOT_CANCELLED,
            from_token=self,
        )

    @abstractmethod
    def _superpower(self) -> bool:  # pragma: no cover
        pass

    def _superpower_rollback(  # noqa: B027
        self,
        superpower_data: Dict[str, Any],
    ) -> None:  # pragma: no cover
        pass

    def _check_superpower(self, direct: bool) -> bool:
        if self._rollback_if_nondirect_polling and not direct:
            return self._check_superpower_with_rollback()
        return self._superpower()

    def _check_superpower_with_rollback(self) -> bool:
        with self._lock:
            superpower_data = self._get_superpower_data()
            result = self._superpower()
            self._superpower_rollback(superpower_data)
            return result

    def _get_superpower_data(self) -> Dict[str, Any]:  # pragma: no cover
        return {}

    @abstractmethod
    def _text_representation_of_superpower(self) -> str:  # pragma: no cover
        pass

    def _get_extra_kwargs(self) -> Dict[str, Any]:
        return {}

    def _text_representation_of_extra_kwargs(self) -> str:
        return self._text_representation_of_kwargs(**(self._get_extra_kwargs()))

    def _text_representation_of_kwargs(self, **kwargs: Any) -> str:
        pairs: List[str] = [f'{key}={value!r}' for key, value in kwargs.items()]
        return ', '.join(pairs)

    def _raise_cancelled_exception(self) -> None:
        raise CancellationError('The token has been cancelled.', self)

    def _raise_superpower_exception(self) -> None:
        raise self.exception(self._get_superpower_exception_message(), self)

    @abstractmethod
    def _get_superpower_exception_message(self) -> str:  # pragma: no cover
        return 'You have done the impossible to see this error.'
