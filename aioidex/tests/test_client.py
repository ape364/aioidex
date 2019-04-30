import asyncio
from unittest.mock import patch

import pytest
from asynctest import CoroutineMock

from aioidex.http.client import Client
from aioidex.http.modules.public import Public
from aioidex.http.network import Network


@pytest.fixture()
async def client():
    loop = asyncio.get_event_loop()
    c = Client(loop=loop, timeout=55)
    yield c
    await c.close()


@pytest.mark.asyncio
async def test_client_init(client: Client):
    assert isinstance(client._http, Network)
    assert client._http._session._timeout.total == 55


@pytest.mark.asyncio
async def test_loop():
    loop = asyncio.get_event_loop()
    c = Client(loop=loop)
    assert c._http._loop is loop
    assert c._http._session._loop is loop


@pytest.mark.asyncio
async def test_modules_init(client: Client):
    assert isinstance(client.public, Public)


@pytest.mark.asyncio
async def test_close_session(client: Client):
    with patch('aioidex.http.network.Network.close', new_callable=CoroutineMock) as m:
        await client.close(0.01)
        m.assert_awaited_once_with(0.01)
