from asyncio import AbstractEventLoop

from aioidex.http.modules.public import Public
from aioidex.http.network import Network


class Client:
    def __init__(self, loop: AbstractEventLoop = None, timeout: int = None) -> None:
        self._http = Network(loop, timeout)

        self.public = Public(self._http)

    async def close(self, delay: float = 0.250):
        await self._http.close(delay)
