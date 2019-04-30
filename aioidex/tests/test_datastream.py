import asyncio
from logging import Logger

import pytest
import websockets
from asynctest import CoroutineMock, Mock, MagicMock, patch
from shortid import ShortId

from aioidex import IdexDatastream
from aioidex.exceptions import IdexDataStreamError, IdexResponseSidError, IdexHandshakeException
from aioidex.datastream.sub_manager import SubscriptionManager


@pytest.fixture()
async def ds():
    ds = IdexDatastream()
    yield ds


@pytest.mark.asyncio
async def test_init():
    api_key = 'testkey'
    version = '0.0.1'
    ws_endpoint = 'wss://end.point'
    handshake_timeout = 3.21
    return_sub_responses = True
    loop = asyncio.get_event_loop()

    ds = IdexDatastream(
        api_key,
        version,
        ws_endpoint,
        handshake_timeout,
        return_sub_responses,
        loop,
    )

    assert ds._API_KEY == api_key
    assert ds._WS_ENDPOINT == ws_endpoint
    assert ds._WS_VERSION == version
    assert ds._HANDSHAKE_TIMEOUT == handshake_timeout
    assert ds._loop is loop
    assert isinstance(ds._logger, Logger)
    assert isinstance(ds._rid, ShortId)
    assert isinstance(ds.sub_manager, SubscriptionManager)


@pytest.mark.asyncio
async def test_check_connection(ds: IdexDatastream):
    ds.init = CoroutineMock()

    ds._ws = object
    await ds._check_connection()
    ds.init.assert_not_awaited()

    ds._ws = None
    await ds._check_connection()
    ds.init.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_ds(ds: IdexDatastream):
    ds._init_connection = CoroutineMock()
    ds._shake_hand = CoroutineMock()

    await ds.init()

    ds._init_connection.assert_awaited_once()
    ds._shake_hand.assert_awaited_once()


@pytest.mark.asyncio
async def test_init_connection(ds: IdexDatastream):
    ws_mock = Mock()
    create_conn_mock = CoroutineMock(return_value=ws_mock)
    ds.create_connection = create_conn_mock

    await ds._init_connection()

    create_conn_mock.assert_awaited_once()
    assert ds._ws is ws_mock

    another_mock_ws = Mock()

    await ds._init_connection(another_mock_ws)

    assert ds._ws is another_mock_ws


@pytest.mark.asyncio
async def test_create_connection(ds: IdexDatastream):
    ds._check_connection = CoroutineMock()
    ds._get_rid = Mock(return_value='rid:smth')
    ds._compose_message = Mock(return_value={'some': 'data'})
    ds._ws = Mock()
    ds._ws.send = CoroutineMock()
    ds._encode = Mock()

    result = await ds.send_message('some_request', {'some': 'payload'})

    ds._check_connection.assert_awaited_once()
    ds._get_rid.assert_called_once()
    ds._compose_message.assert_called_once_with('rid:smth', 'some_request', {'some': 'payload'})
    ds._encode.assert_called_once_with({'some': 'data'})
    ds._ws.send.assert_awaited_once()
    assert result == 'rid:smth'


@pytest.mark.asyncio
async def test_create_connection_rid(ds: IdexDatastream):
    ds._check_connection = CoroutineMock()
    ds._get_rid = Mock(return_value='rid:smth')
    ds._compose_message = Mock(return_value={'some': 'data'})
    ds._ws = Mock()
    ds._ws.send = CoroutineMock()
    ds._encode = Mock()

    result = await ds.send_message('some_request', {'some': 'payload'}, 'somerid')

    ds._check_connection.assert_awaited_once()
    ds._get_rid.assert_not_called()
    ds._compose_message.assert_called_once_with('somerid', 'some_request', {'some': 'payload'})
    ds._encode.assert_called_once_with({'some': 'data'})
    ds._ws.send.assert_awaited_once()
    assert result == 'somerid'


def test_compose_message(ds: IdexDatastream):
    ds._set_sid('somesid')
    assert ds._compose_message('somerid', 'somerequest', {'some': 'payload'}) == dict(
        rid='somerid',
        sid='somesid',
        request='somerequest',
        payload={'some': 'payload'}
    )


@pytest.mark.asyncio
async def test_listen(ds: IdexDatastream):
    msg_data = '{"payload":"{"some": "data"}"}'

    ds._check_connection = CoroutineMock()
    ds._ws = MagicMock()
    ds._ws.__aiter__.return_value = (msg_data,)

    processed_message = {'a': 'b'}
    ds._process_message: Mock = Mock()
    ds._process_message.return_value = processed_message

    msg = None
    async for m in ds.listen():
        msg = m
        break

    ds._process_message.assert_called_once_with(msg_data)
    assert msg == processed_message


@pytest.mark.asyncio
async def test_listen_reconnect(ds: IdexDatastream):
    class BreakExc(Exception):
        pass

    exc = websockets.ConnectionClosed(code=999, reason='some reason')
    exit_exc = BreakExc('to break the infinite loop')

    ds._check_connection = CoroutineMock()
    ds._ws = MagicMock()
    ds._ws.__aiter__.side_effect = exc

    ds.init = CoroutineMock()

    ds.sub_manager.resubscribe = CoroutineMock()
    ds.sub_manager.resubscribe.side_effect = exit_exc

    ds._logger.error = Mock()

    with pytest.raises(BreakExc):
        async for m in ds.listen():
            break

    ds._check_connection.assert_awaited_once()
    ds._logger.error.assert_called_once_with(exc)
    ds.init.assert_awaited_once()
    ds.sub_manager.resubscribe.assert_awaited_once()


@pytest.mark.asyncio
async def test_listen_raise(ds: IdexDatastream):
    class UnhandledExc(Exception):
        pass

    exc = UnhandledExc('some unknown exception')

    ds._check_connection = CoroutineMock()
    ds._ws = MagicMock()
    ds._ws.__aiter__.side_effect = exc

    with pytest.raises(UnhandledExc):
        async for m in ds.listen():
            break

    ds._check_connection.assert_awaited_once()


def test_process_message(ds: IdexDatastream):
    msg = '{"payload":"{"some": "data"}"}'
    decoded_msg = {1: 2}

    ds._decode = Mock()
    ds._decode.return_value = decoded_msg

    ds._check_warnings = Mock()
    ds._check_errors = Mock()
    ds._check_sid = Mock()

    ds.sub_manager.is_sub_response = Mock()
    ds.sub_manager.is_sub_response.return_value = False

    result = ds._process_message(msg)

    ds._decode.assert_called_once_with(msg)
    ds.sub_manager.is_sub_response.assert_called_once_with(decoded_msg)
    ds._check_warnings.assert_called_once_with(decoded_msg)
    ds._check_errors.assert_called_once_with(decoded_msg)
    ds._check_sid.assert_called_once_with(decoded_msg)

    assert result == decoded_msg


def test_process_message_sub_response(ds: IdexDatastream):
    msg = '{"payload":"{"some": "data"}"}'
    decoded_msg = {1: 2}
    sub_response = {3: 4}

    ds._decode = Mock()
    ds._decode.return_value = decoded_msg

    ds._check_warnings = Mock()
    ds._check_errors = Mock()
    ds._check_sid = Mock()

    ds.sub_manager.is_sub_response = Mock()
    ds.sub_manager.is_sub_response.return_value = True

    ds.sub_manager.process_sub_response = Mock()
    ds.sub_manager.process_sub_response.return_value = sub_response

    result = ds._process_message(msg)

    ds._decode.assert_called_with(msg)
    ds.sub_manager.is_sub_response.assert_called_once_with(decoded_msg)
    ds.sub_manager.process_sub_response.assert_called_once_with(decoded_msg)
    ds._check_warnings.assert_called_once_with(decoded_msg)
    ds._check_errors.assert_called_once_with(decoded_msg)
    ds._check_sid.assert_called_once_with(decoded_msg)

    assert result == sub_response


def test_check_warnings_exists(ds: IdexDatastream):
    msg = {'warnings': ['warning1', 'warning2']}

    ds._logger.warning = Mock()

    ds._check_warnings(msg)

    assert ds._logger.warning.call_count == 2


def test_check_warnings_not_exists(ds: IdexDatastream):
    msg = {}

    ds._logger.warning = Mock()

    ds._check_warnings(msg)

    ds._logger.warning.assert_not_called()


def test_check_error_exists(ds: IdexDatastream):
    msg = {'result': 'error', 'payload': {'message': 'error message'}}

    with pytest.raises(IdexDataStreamError):
        ds._check_errors(msg)


def test_check_error_not_exists(ds: IdexDatastream):
    msg = {'result': 'success'}

    ds._check_errors(msg)


def test_check_sid_raise(ds: IdexDatastream):
    ds._sid = 'sid:one'

    msg = {'sid': 'sid:another'}

    with pytest.raises(IdexResponseSidError):
        ds._check_sid(msg)


def test_check_sid_not_raise(ds: IdexDatastream):
    ds._sid = 'sid:one'

    msg = {'sid': ds._sid}

    ds._check_sid(msg)


@pytest.mark.asyncio
async def test_shake_hand(ds: IdexDatastream):
    ds._WS_VERSION = 'v1'
    ds._API_KEY = 'key'

    handshake_result = 'some result'

    ds._set_sid = Mock()
    ds.send_message = CoroutineMock()
    ds._wait_for_handshake_response = CoroutineMock()
    ds._wait_for_handshake_response.return_value = handshake_result
    ds._process_handshake_response = Mock()

    await ds._shake_hand()

    ds._set_sid.assert_called_with(None)
    ds.send_message.assert_awaited_once_with('handshake', dict(version='v1', key='key'))
    ds._wait_for_handshake_response.assert_awaited_once()
    ds._process_handshake_response.assert_called_once_with(handshake_result)


@pytest.mark.asyncio
async def test_wait_for_handshake_response(ds: IdexDatastream):
    ds._ws = CoroutineMock()

    loop_mock = CoroutineMock()
    ds._loop = loop_mock

    recv_mock = Mock()
    recv_mock.return_value = None
    ds._ws.recv = recv_mock

    with patch('asyncio.wait_for', new=CoroutineMock()) as mock:
        mock.return_value = '{"some":"data"}'
        await ds._wait_for_handshake_response()

        mock.assert_awaited_once_with(None, ds._HANDSHAKE_TIMEOUT, loop=loop_mock)


def test_process_handshake_response(ds: IdexDatastream):
    ds._set_sid = Mock()

    with pytest.raises(IdexHandshakeException):
        ds._process_handshake_response({'result': 'not_success'})

    with pytest.raises(IdexHandshakeException):
        ds._process_handshake_response({'result': 'success', 'request': 'not_handshake'})

    ds._process_handshake_response({'result': 'success', 'request': 'handshake', 'sid': 'some_sid'})
    ds._set_sid.assert_called_once_with('some_sid')


def test_get_rid(ds: IdexDatastream):
    rid = ds._get_rid()

    assert isinstance(rid, str)
    assert rid.startswith('rid:')
    # Max accepted length is 50 characters. Your rid will be truncated if any longer than this.
    # Clients sending rid's which are longer than 50 characters risk eventual disconnects, blacklisting, or bans.
    assert len(rid) <= 50

    rid2 = ds._get_rid()
    assert rid != rid2


def test_sid(ds: IdexDatastream):
    ds._logger.info = Mock()

    ds._set_sid('some_sid')

    ds._logger.info.assert_called_once()
    assert ds._sid == 'some_sid'


def test_sid_equal(ds: IdexDatastream):
    ds._logger.info = Mock()

    ds._sid = 'some_sid'
    ds._set_sid('some_sid')

    ds._logger.info.assert_not_called()
    assert ds._sid == 'some_sid'


def test_encode(ds: IdexDatastream):
    data = {'some': 'data', 'arr': [{'k1': 'v1'}, {'k2': 'v2'}]}
    expected = '{"some":"data","arr":[{"k1":"v1"},{"k2":"v2"}]}'

    assert ds._encode(data) == expected


def test_decode(ds: IdexDatastream):
    assert ds._decode('{"some":"data"}') == {'some': 'data'}
    assert ds._decode('{"payload": "{\\"some\\": \\"data\\"}"}') == {'payload': {'some': 'data'}}
    assert ds._decode('{"warnings": "[\\"warn1\\", \\"warn2\\"]"}') == {'warnings': ['warn1', 'warn2']}
