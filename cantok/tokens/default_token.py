from typing import Optional

from cantok import AbstractToken
from cantok.errors import ImpossibleCancelError


class DefaultToken(AbstractToken):
    """
    An immutable token that never cancels.

    Useful as a neutral default argument: a function that accepts a token can
    receive a DefaultToken when no real cancellation is needed, without
    requiring None checks. Calling cancel() raises ImpossibleCancelError.

    >>> def run(token: AbstractToken = DefaultToken()) -> bool:
    ...     return token.keep_on()
    >>> run()               # True — DefaultToken never cancels
    True
    >>> run(SimpleToken())  # True — SimpleToken not yet cancelled
    True
    """

    exception = ImpossibleCancelError

    def __init__(self, *, doc: Optional[str] = None) -> None:
        super().__init__(doc=doc)

    @property
    def cancelled(self) -> bool:
        return False

    @cancelled.setter
    def cancelled(self, new_value: bool) -> None:
        if new_value == True:
            self._raise_superpower_exception()

    def keep_on(self) -> bool:
        return True

    def is_cancelled(self, direct: bool = True) -> bool:  # noqa: ARG002
        return False

    def cancel(self) -> 'AbstractToken':  # type: ignore[return]
        self._raise_superpower_exception()

    def _superpower(self) -> bool:
        return False

    def _text_representation_of_superpower(self) -> str:
        return ''

    def _get_superpower_exception_message(self) -> str:
        return 'You cannot cancel a default token.'  # pragma: no cover
