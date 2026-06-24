Each token has a `wait()` method, which allows you to block the current thread until the token is cancelled.

```python
from cantok import TimeoutToken

token = TimeoutToken(5)
token.wait()  # It will take about 5 seconds.
token.check()  # Since the timeout has expired, an exception will be raised.
#> ...
#> cantok.errors.TimeoutCancellationError: The timeout of 5 seconds has expired.
```

This is useful when one thread needs to wait for cancellation requested from another thread:

```python
from threading import Thread
from time import sleep
from cantok import SimpleToken

def do_something(token):
  sleep(3)  # Imitation of some real activity.
  token.cancel()

token = SimpleToken()
thread = Thread(target=do_something, args=(token,))
thread.start()

token.wait()
thread.join()
print('Something has been done!')
```

In addition to the above, the `wait()` method has two optional arguments:

- **`timeout`** (`int` or `float`) — the maximum waiting time in seconds. If this time is exceeded, a [`TimeoutCancellationError` exception](../what_are_tokens/exceptions.md) will be raised. By default, the `timeout` is not set.
- **`step`** (`int` or `float`, by default `0.0001`) — the duration of each iteration during which the token state is polled, in seconds. For obvious reasons, you cannot set this value to a number that exceeds the `timeout`.
