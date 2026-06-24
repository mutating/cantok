import asyncio
from time import perf_counter

import pytest

from cantok import ConditionToken


@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_async_wait_condition():
    flag = False
    timeout = 0.001
    token = ConditionToken(lambda: flag)

    async def cancel_with_timeout(_token):
        nonlocal flag
        await asyncio.sleep(timeout)
        flag = True

    async def runner():
        return await asyncio.gather(token.wait(), cancel_with_timeout(token))

    start_time = perf_counter()
    asyncio.run(runner())
    finish_time = perf_counter()

    assert finish_time - start_time >= timeout
