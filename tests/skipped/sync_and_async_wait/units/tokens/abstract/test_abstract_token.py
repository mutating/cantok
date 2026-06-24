import asyncio
from functools import partial
from time import perf_counter

import pytest

from cantok import (
    ConditionToken,
    CounterToken,
    DefaultToken,
    SimpleToken,
    TimeoutToken,
)

ALL_TOKEN_CLASSES = [SimpleToken, ConditionToken, TimeoutToken, CounterToken]
ALL_ARGUMENTS_FOR_TOKEN_CLASSES = [tuple(), (lambda: False, ), (15, ), (15, )]
ALL_TOKENS_FABRICS = [partial(token_class, *arguments) for token_class, arguments in zip(ALL_TOKEN_CLASSES, ALL_ARGUMENTS_FOR_TOKEN_CLASSES)]


@pytest.mark.parametrize(
    'parameters',
    [
        {'step': -1},
        {'step': -1, 'timeout': -1},
        {'step': -1, 'timeout': 0},
        {'timeout': -1},
        {'step': 1, 'timeout': -1},
        {'step': -1, 'timeout': 1},
        {'step': 2, 'timeout': 1},
    ],
)
@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
@pytest.mark.parametrize(
    'do_await',
    [
        True,
    ],
)
@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_wait_wrong_parameters(token_fabric, parameters, do_await):
    token = token_fabric()

    if do_await:
        with pytest.raises(ValueError, match=r'.'):
            asyncio.run(token.wait(**parameters))
    else:
        with pytest.raises(ValueError, match=r'.'):
            token.wait(**parameters)


@pytest.mark.parametrize(
    'token_fabric',
    [*ALL_TOKENS_FABRICS, DefaultToken],
)
@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_async_wait_timeout(token_fabric):
    timeout = 0.0001
    token = token_fabric()

    with pytest.raises(TimeoutToken.exception):
        asyncio.run(token.wait(timeout=timeout))


@pytest.mark.parametrize(
    'token_fabric',
    ALL_TOKENS_FABRICS,
)
@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_async_wait_with_cancel(token_fabric):
    timeout = 0.001
    token = token_fabric()

    async def cancel_with_timeout(token):
        await asyncio.sleep(timeout)
        token.cancel()

    async def runner(token):
        coroutines = [cancel_with_timeout(token), token.wait() ]
        return await asyncio.gather(*coroutines)

    start_time = perf_counter()
    asyncio.run(runner(token))
    finish_time = perf_counter()

    assert not token
    assert finish_time - start_time >= timeout
