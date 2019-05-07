import asyncio
from asyncio import AbstractEventLoop
from enum import Enum
from typing import Optional, Dict

from aiohttp import ClientSession, ClientTimeout, ClientResponse, ContentTypeError

from aioidex.exceptions import IdexClientContentTypeError, IdexClientApiError


class HttpMethod(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'


class Network:
    _API_URL = 'https://api.idex.market'

    def __init__(self, loop: AbstractEventLoop = None, timeout: int = 10):
        self._loop = loop or asyncio.get_event_loop()
        self._session = self._init_session(timeout)

    def _init_session(self, timeout: int) -> ClientSession:
        return ClientSession(
            headers={
                'Accept': 'application/json',
                'User-Agent': 'aioidex/python',
            },
            timeout=ClientTimeout(total=timeout),
            loop=self._loop
        )

    async def close(self, delay):
        '''Graceful shutdown.

        https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
        '''
        await asyncio.sleep(delay)
        await self._session.close()

    def _create_api_uri(self, path: str) -> str:
        return f'{self._API_URL}/{path}'

    async def _request_api(self, method: HttpMethod, path: str, data: Optional[dict] = None, ):
        return await self._request(method, self._create_api_uri(path), data)

    async def _request(self, method: HttpMethod, url: str, data: Optional[dict] = None):
        http_method = getattr(self._session, method.value)
        async with http_method(url, data=data) as response:
            return await self._handle_response(response)

    async def _handle_response(self, response: ClientResponse):
        try:
            response_json = await response.json()
        except ContentTypeError:
            raise IdexClientContentTypeError(response.status, await response.text())
        else:
            return self._raise_if_error(response_json)

    @staticmethod
    def _raise_if_error(response: Dict) -> Dict:
        if 'error' in response:
            raise IdexClientApiError(response['error'])
        return response

    async def post(self, path: str, data: Optional[Dict] = None):
        return await self._request_api(HttpMethod.POST, path, data)
