When a token is cancelled, you can call the `check()` method on it and an exception will be raised:

```python
from cantok import TimeoutToken

token = TimeoutToken(1)
token.wait()
token.check()
#> ...
#> cantok.errors.TimeoutCancellationError: The timeout of 1 second has expired.
```

The `wait()` method can also raise an exception directly when its own waiting timeout expires:

```python
from cantok import SimpleToken, TimeoutCancellationError

token = SimpleToken()

try:
    token.wait(timeout=1)
except TimeoutCancellationError:
    print('Waiting took too long.')
```

Each type of token (except [`DefaultToken`](../types_of_tokens/DefaultToken.md)) has a corresponding type of exception that can be raised in this case:

- [`SimpleToken`](../types_of_tokens/SimpleToken.md) -> `CancellationError`
- [`ConditionToken`](../types_of_tokens/ConditionToken.md) -> `ConditionCancellationError`
- [`TimeoutToken`](../types_of_tokens/TimeoutToken.md) -> `TimeoutCancellationError`
- [`CounterToken`](../types_of_tokens/CounterToken.md) -> `CounterCancellationError`

When you call the `check()` method on any token, one of two things will happen. If it (or any of the tokens nested in it) has been cancelled by calling the `cancel()` method, `CancellationError` will always be raised. But if the cancellation occurred as a result of the unique ability of the token, such as timeout expiration for `TimeoutToken`, then an exception specific to this type of token will be raised.

`check()` also accepts a keyword-only `exception` argument. Omit it or pass `None` to keep the behavior described above. Pass an exception class, and `check()` raises an instance of it with the standard message for the cancellation cause; pass an existing exception object, and `check()` raises that object as is. If the token is not cancelled, `check()` still does nothing and the override is not used.

```python
from cantok import SimpleToken

token = SimpleToken()
token.cancel()
token.check(exception=RuntimeError)
#> ...
#> RuntimeError: The token has been cancelled.
```

`ConditionCancellationError`, `TimeoutCancellationError`, and `CounterCancellationError` are inherited from `CancellationError`, so if you're not sure which specific exception you're catching, catch `CancellationError`. All of the listed exceptions can also be imported separately:

```python
from cantok import CancellationError, ConditionCancellationError, TimeoutCancellationError, CounterCancellationError
```

You can also choose not to import these exceptions at all. For each token class, the corresponding exception class is accessible as the `exception` attribute:

```python
from cantok import TimeoutToken, CancellationError

token = TimeoutToken(0)

try:
    token.check()
except CancellationError as e:
    print(type(e) is TimeoutToken.exception)  #> True
```

And each exception object has a `token` attribute indicating the specific token that was cancelled. This can be useful in situations where several tokens are nested in one another and you want to find out which one has been cancelled:

```python
from cantok import SimpleToken, TimeoutToken, CancellationError

nested_token = TimeoutToken(0)
token = SimpleToken(nested_token)

try:
    token.check()
except CancellationError as e:
    print(e.token is nested_token)  #> True
```

You can also create any token with a `doc` description. It is included in `repr()` and, if that token causes a cancellation exception, added to the exception message. This makes it easier to recognize the specific cancelled token in nested token chains.
