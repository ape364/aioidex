import asyncio

import aiohttp
import pytest
from aiohttp import ContentTypeError
from asynctest import CoroutineMock, MagicMock, patch, Mock

from aioidex.exceptions import IdexClientContentTypeError, IdexClientApiError
from aioidex.http.network import Network, HttpMethod


def get_loop():
    return asyncio.get_event_loop()


@pytest.fixture()
async def nw():
    nw = Network()
    yield nw
    await nw.close(0.01)


@pytest.mark.asyncio
async def test_init():
    myloop = get_loop()
    mytimeout = 3
    with patch('aioidex.http.network.Network._init_session', new=CoroutineMock()) as mock:
        n = Network(loop=myloop, timeout=mytimeout)
        mock.assert_called_once_with(mytimeout)

    assert n._loop == myloop


@pytest.mark.asyncio
async def test_init_session():
    myloop = get_loop()
    mytimeout = 3
    n = Network(loop=myloop, timeout=mytimeout)

    assert isinstance(n._session, aiohttp.ClientSession)
    assert n._session._loop == myloop
    assert n._session._timeout.total == mytimeout
    assert 'Accept' in n._session._default_headers
    assert n._session._default_headers['Accept'] == 'application/json'
    assert 'User-Agent' in n._session._default_headers


@pytest.mark.asyncio
async def test_close(nw: Network):
    nw._session = CoroutineMock()
    nw._session.close = CoroutineMock()

    with patch('asyncio.sleep') as mock:
        await nw.close(0.01)
        mock.assert_awaited_once_with(0.01)

    nw._session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_api_uri(nw: Network):
    nw._API_URL = 'someurl'
    assert nw._create_api_uri('somepath') == 'someurl/somepath'


@pytest.mark.asyncio
async def test_request_api(nw: Network):
    nw._request = CoroutineMock()
    nw._create_api_uri = Mock()
    nw._create_api_uri.return_value = 'someuri'

    method = HttpMethod.POST
    path = 'somepath'
    data = {'some': 'data'}

    await nw._request_api(method, path, data)

    nw._create_api_uri.assert_called_once_with(path)
    nw._request.assert_awaited_once_with(method, 'someuri', data)


@pytest.mark.asyncio
async def test_request(nw: Network):
    class MagicMockContext(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            type(self).__aenter__ = CoroutineMock(return_value='response data')
            type(self).__aexit__ = CoroutineMock(return_value=MagicMock())

    method = HttpMethod.POST
    url = 'someurl'
    data = {'some': 'data'}

    nw._handle_response = CoroutineMock()
    nw._handle_response.return_value = 'some value'

    with patch('aiohttp.ClientSession.post', new_callable=MagicMockContext) as m:
        result = await nw._request(method, url, data)
        m.assert_called_once_with(url, data=data)
        nw._handle_response.assert_awaited_once_with('response data')
        assert result == 'some value'


@pytest.mark.asyncio
async def test_handle_response(nw: Network):
    return_value = {'some': 'response'}

    response = CoroutineMock()
    response.json = CoroutineMock()
    response.json.return_value = return_value

    nw._raise_if_error = Mock()
    nw._raise_if_error.return_value = return_value

    result = await nw._handle_response(response)

    response.json.assert_awaited_once()
    nw._raise_if_error.assert_called_once_with(return_value)

    assert result == {'some': 'response'}


@pytest.mark.asyncio
async def test_handle_response_content_type_error(nw: Network):
    response = CoroutineMock()
    response.status = 123
    response.text = CoroutineMock()
    response.text.return_value = 'some content'
    response.json = CoroutineMock()
    response.json.side_effect = ContentTypeError(None, None)

    with pytest.raises(IdexClientContentTypeError):
        await nw._handle_response(response)


@pytest.mark.asyncio
async def test_raise_if_error(nw: Network):
    resp = {'no': 'error'}
    assert resp == nw._raise_if_error(resp)

    with pytest.raises(IdexClientApiError):
        nw._raise_if_error({'error': 'some error msg'})


@pytest.mark.asyncio
async def test_post(nw: Network):
    nw._request_api = CoroutineMock()

    await nw.post('somepath', {'some': 'data'})

    nw._request_api.assert_awaited_once_with(HttpMethod.POST, 'somepath', {'some': 'data'})
