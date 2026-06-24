import asyncio
from contextlib import redirect_stdout
from io import StringIO

import pytest

from cantok import SimpleToken


@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_waiting_of_cancelled_token():
    async def do_something(token):
        await asyncio.sleep(0.1)  # Imitation of some real async activity.
        token.cancel()

    async def main():
        token = SimpleToken()
        await do_something(token)
        await token.wait()
        print('Something has been done!')  # noqa: T201

    buffer = StringIO()
    with redirect_stdout(buffer):
        asyncio.run(main())

    assert buffer.getvalue() == 'Something has been done!\n'


@pytest.mark.skip(reason='The universal sync/async wait() method is no longer supported because it suppressed exceptions raised during wait-time cancellation checks.')
def test_waiting_of_cancelled_token_with_gather():
    async def do_something(token):
        await asyncio.sleep(0.1)  # Imitation of some real async activity.
        token.cancel()

    async def main():
        token = SimpleToken()
        await asyncio.gather(do_something(token), token.wait())
        print('Something has been done!')  # noqa: T201

    buffer = StringIO()
    with redirect_stdout(buffer):
        asyncio.run(main())

    assert buffer.getvalue() == 'Something has been done!\n'
