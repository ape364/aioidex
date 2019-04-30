from abc import ABC
from enum import Enum
from typing import Dict, Optional

from aioidex.http.network import Network


class BaseModule(ABC):
    def __init__(self, network):
        self._http: Network = network

    async def _post(self, path: str, data: Optional[Dict] = None):
        return await self._http.post(path, data=self._filter_params(data))

    @staticmethod
    def _filter_params(params: Dict) -> Dict:
        return {
            k: v.value if isinstance(v, Enum) else v
            for k, v in params.items()
            if v is not None
        } if params else {}
