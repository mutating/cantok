import asyncio
from time import perf_counter

import pytest

from cantok import TimeoutToken


@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_async_wait_timeout():
    sleep_duration = 0.0001
    token = TimeoutToken(sleep_duration)

    start_time = perf_counter()
    asyncio.run(token.wait())
    finish_time = perf_counter()

    assert sleep_duration <= finish_time - start_time


@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_run_async_multiple_timeouts():
    sleep_duration = 0.001
    number_of_tokens = 100

    tokens = [TimeoutToken(sleep_duration) for x in range(number_of_tokens)]

    async def runner():
        return await asyncio.gather(*(x.wait() for x in tokens))

    start_time = perf_counter()
    asyncio.run(runner())
    finish_time = perf_counter()

    assert (finish_time - start_time) < (sleep_duration * number_of_tokens)
