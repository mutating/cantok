> ⚠️ `CounterToken` is deprecated. A new mechanism for limiting attempts and iterations will be introduced in future releases.

`CounterToken` is the least intuitive of the tokens provided by this library. Do not use it if you are not sure that you understand how it works. However, it can be very useful in situations where you want to limit the number of attempts to perform an operation.

`CounterToken` is initialized with an integer greater than or equal to zero. Each time cancellation is checked, this number is decremented by one. When this number becomes zero, the token is considered cancelled:

```python
from cantok import CounterToken

token = CounterToken(5)
counter = 0

while token:
    counter += 1

print(counter)  #> 5
```

The counter inside the `CounterToken` is decremented under one of three conditions:

- Access to the `cancelled` attribute.
- Calling the `is_cancelled()` method.
- Calling the `keep_on()` method.

If you use `CounterToken` inside other tokens, the wrapping token can query the status of the `CounterToken`. To avoid unintended side effects, querying the status does not decrease the counter. However, if for some reason you need it to decrease, pass `direct=False` as an argument:

```python
from cantok import SimpleToken, CounterToken

first_counter_token = CounterToken(1, direct=False)
second_counter_token = CounterToken(1, direct=True)

print(SimpleToken(first_counter_token, second_counter_token).cancelled)  #> False
print(first_counter_token.cancelled)  #> True
print(second_counter_token.cancelled)  #> False
```

Like all other tokens, `CounterToken` can accept other tokens as parameters during initialization:

```python
from cantok import SimpleToken, CounterToken, TimeoutToken

token = CounterToken(15, SimpleToken(), TimeoutToken(5))
```
