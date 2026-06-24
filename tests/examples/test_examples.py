from random import randint
from threading import Thread

from cantok import ConditionToken, CounterToken, TimeoutToken

counter = 0

def test_cancel_simple_token_with_function_and_thread():
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
    token = ConditionToken(lambda: randint(1, 100_000) == 1984) + CounterToken(400_000, direct=False) + TimeoutToken(1)
    counter = 0

    while token:
      counter += 1

    assert counter
