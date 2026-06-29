A token is an object that can tell you whether to continue the action you started, or whether it has already been cancelled.

There are 4 main types of tokens in this library:

- [`SimpleToken`](../types_of_tokens/SimpleToken.md)
- [`ConditionToken`](../types_of_tokens/ConditionToken.md)
- [`TimeoutToken`](../types_of_tokens/TimeoutToken.md)
- [`CounterToken`](../types_of_tokens/CounterToken.md)

Additionally, there is a 5th type that cannot be cancelled:

- [`DefaultToken`](../types_of_tokens/DefaultToken.md)

Each of them has its own characteristics, but they also have something in common:

- Each token (except [`DefaultToken`](../types_of_tokens/DefaultToken.md)) can be cancelled manually, and some types of tokens can cancel themselves when a condition or timeout occurs. It doesn't matter how the token was cancelled; you work with it the same way.

- All types of tokens are thread-safe and can be used from multiple threads/coroutines. However, they are not intended to be shared across multiple processes.

- Token cancellation is a one-way operation. A token that has already been cancelled cannot be restored.

- All token classes accept `doc` as a human-readable token description. It is used in `repr()` and in cancellation exception messages; see [exceptions](exceptions.md) for details.

- All token classes inherit from `AbstractToken` and have a single interface that defines how they can be cancelled, how to find out their status, how to wait for their cancellation, and much more. If you are writing a function that accepts an unknown token type, you can use `AbstractToken` for type hints:

```python
from cantok import AbstractToken

def function(token: AbstractToken):
  ...
```
