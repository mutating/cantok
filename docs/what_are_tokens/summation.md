Tokens can be summed using the operator `+`:

```python
first_token = TimeoutToken(5)
second_token = ConditionToken(lambda: True)
print(repr(first_token + second_token))
#> SimpleToken(TimeoutToken(5), ConditionToken(λ))
```

This feature is convenient to use if your function has received a token with certain restrictions and needs to pass it to other called functions, imposing additional restrictions:

```python
from cantok import AbstractToken, TimeoutToken

def function(token: AbstractToken):
  ...
  another_function(token + TimeoutToken(5))  # Imposes an additional restriction on the function being called: work for no more than 5 seconds. At the same time, it does not know anything about what restrictions were imposed earlier.
  ...
```

The token summation operation always generates a new [`SimpleToken`](../types_of_tokens/SimpleToken.md). If at least one of the nested operand tokens is cancelled, the sum will also be cancelled. It is also guaranteed that the cancellation of this token does not lead to the cancellation of the operands. Direct [`DefaultToken`](../types_of_tokens/DefaultToken.md) operands are not nested into the sum.
