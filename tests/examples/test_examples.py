from random import randint
from threading import Thread

from cantok import ConditionToken, CounterToken, TimeoutToken

counter = 0

def test_cancel_simple_token_with_function_and_thread():
    """
    A quick-start Condition, Counter, and Timeout composition can stop a worker thread.

    The worker receives the composed token, performs some work while `.cancelled`
    is false, and exits once the random condition, indirect counter poll, or
    timeout cancels the shared token.
    """
    def function(token):
        global counter  # noqa: PLW0603
        while not token.cancelled:
            counter += 1

    token = ConditionToken(lambda: randint(1, 100_000) == 1984) + CounterToken(400_000, direct=False) + TimeoutToken(1)
    thread = Thread(target=function, args=(token, ))
    thread.start()
    thread.join()

    assert counter


def test_cancel_simple_token_with_function_and_thread_2():
    """
    A quick-start Condition, Counter, and Timeout composition can be a truthy loop guard.

    The loop makes progress while the composed token is active, then stops once the
    random condition, indirect counter poll, or timeout cancels it.
    """
    token = ConditionToken(lambda: randint(1, 100_000) == 1984) + CounterToken(400_000, direct=False) + TimeoutToken(1)
    counter = 0

    while token:
      counter += 1

    assert counter
