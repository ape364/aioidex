import asyncio
import logging
from asyncio import AbstractEventLoop
from typing import Dict, Union, Optional

import backoff
import ujson
import websockets
from shortid import ShortId
from websockets.client import WebSocketClientProtocol

from aioidex.datastream.sub_manager import SubscriptionManager
from aioidex.exceptions import IdexHandshakeException, IdexAuthenticationFailure, IdexResponseSidError, \
    IdexDataStreamError, IdexInvalidVersion, IdexHandshakeTimeout


class IdexDatastream:
    _ws: WebSocketClientProtocol = None
    _sid: str = None

    def __init__(
            self,
            api_key: str = '17paIsICur8sA0OBqG6dH5G1rmrHNMwt4oNk4iX9',
            version: str = '1.0.0',
            ws_endpoint: str = 'wss://datastream.idex.market',
            handshake_timeout: float = 1.0,
            return_sub_responses=False,
            loop: AbstractEventLoop = None
    ):
        self._API_KEY = api_key
        self._WS_ENDPOINT = ws_endpoint
        self._WS_VERSION = version
        self._HANDSHAKE_TIMEOUT = handshake_timeout

        self._loop = loop or asyncio.get_event_loop()
        self._logger = logging.getLogger(__name__)

        self._rid = ShortId()

        self.sub_manager = SubscriptionManager(self, return_sub_responses)

    async def _check_connection(self):
        if not self._ws:
            self._logger.info('Connection not created yet, creating...')
            await self.init()

    async def init(self, ws: WebSocketClientProtocol = None):
        await self._init_connection(ws)
        await self._shake_hand()

    @backoff.on_exception(backoff.expo, Exception, max_time=30)  # TODO: clarify exception
    async def _init_connection(self, ws: WebSocketClientProtocol = None):
        self._ws = ws or await self.create_connection()
        self._logger.info('WS connection created: %s, %s', self._ws, self._ws.state)

    async def create_connection(self):
        return await websockets.connect(self._WS_ENDPOINT)

    async def send_message(self, request: str, payload: Dict, rid: str = None) -> str:
        await self._check_connection()

        request_rid = rid or self._get_rid()

        message = self._compose_message(request_rid, request, payload)

        await self._ws.send(self._encode(message))
        self._logger.debug('Sent message: %s', message)

        return request_rid

    def _compose_message(self, rid: str, request: str, payload: Dict):
        return dict(
            rid=rid,
            sid=self._sid,
            request=request,
            payload=payload
        )

    async def listen(self):
        await self._check_connection()
        while True:
            try:
                async for msg in self._ws:
                    self._logger.debug('New message: %s', msg)
                    message = self._process_message(msg)
                    if message:
                        yield message
            except (websockets.ConnectionClosed, IdexResponseSidError) as e:
                self._logger.error(e)
                self._logger.warning('Reconnecting...')
                await self.init()
                await self.sub_manager.resubscribe()

    def _process_message(self, message: str) -> Optional[Dict]:
        decoded_msg = self._decode(message)
        self._logger.debug('New message: %s', decoded_msg)

        self._check_warnings(decoded_msg)
        self._check_errors(decoded_msg)
        self._check_sid(decoded_msg)

        if self.sub_manager.is_sub_response(decoded_msg):
            return self.sub_manager.process_sub_response(decoded_msg)

        return decoded_msg

    def _check_warnings(self, message: Dict):
        '''When an upcoming change to the specification is expected, a handshake request may return a warnings property
        which can be used to alert you when an update to your integration will be required.

        https://docs.idex.market/#tag/Datastream-Versioning
        '''
        if 'warnings' in message:
            for warning in message['warnings']:
                self._logger.warning(f'Response warning: {warning}')

    @staticmethod
    def _check_errors(message: Dict):
        if message.get('result') == 'error':
            payload = message['payload']
            error_msg = payload.get('message', message)
            raise IdexDataStreamError(f'Response error: {error_msg}')

    def _check_sid(self, message: Dict):
        '''Your client should monitor the sid value with every response and immediately reconnect if not a match.'''
        sid = message['sid']
        if sid != self._sid:
            raise IdexResponseSidError(f'Received sid {sid!r} differs from existing sid {self._sid!r}, reconnecting...')

    async def _shake_hand(self):
        self._set_sid(None)
        self._logger.info('Shaking hand...')
        await self.send_message('handshake', dict(version=self._WS_VERSION, key=self._API_KEY))
        self._process_handshake_response(await self._wait_for_handshake_response())

    async def _wait_for_handshake_response(self) -> Dict:
        try:
            logging.info('Waiting for handshake response with timeout %s seconds...', self._HANDSHAKE_TIMEOUT)
            response = await asyncio.wait_for(self._ws.recv(), self._HANDSHAKE_TIMEOUT, loop=self._loop)
        except websockets.ConnectionClosed as e:
            if e.code == 1002:
                if e.reason == 'AuthenticationFailure':
                    raise IdexAuthenticationFailure(e)
                elif e.reason == 'InvalidVersion':
                    raise IdexInvalidVersion(e)
            raise
        except asyncio.TimeoutError:
            raise IdexHandshakeTimeout(f'Handshake response is not received within {self._HANDSHAKE_TIMEOUT} seconds')
        else:
            return self._decode(response)

    def _process_handshake_response(self, message: Dict):
        if message['result'] != 'success' or message['request'] != 'handshake':
            raise IdexHandshakeException(message)
        self._logger.info('Got handshake response: %s', message)
        self._set_sid(message['sid'])

    def _get_rid(self) -> str:
        return f'rid:{self._rid.generate()}'

    def _set_sid(self, sid: Union[str, None]):
        if self._sid == sid:
            return
        self._logger.info('Sid changed from %r to %r', self._sid, sid)
        self._sid = sid

    @staticmethod
    def _encode(data: Dict) -> str:
        return ujson.dumps(data)

    @staticmethod
    def _decode(data: str) -> Dict:
        decoded_msg = ujson.loads(data)

        for field in ('payload', 'warnings'):
            if field in decoded_msg and isinstance(decoded_msg[field], str):
                decoded_msg[field] = ujson.loads(decoded_msg[field])

        return decoded_msg
