# aioidex

[![PyPi](https://img.shields.io/pypi/v/aioidex.svg)](https://pypi.org/project/aioidex/)
[![License](https://img.shields.io/pypi/l/aioidex.svg)](https://pypi.org/project/aioidex/)
[![Build](https://travis-ci.com/ape364/aioidex.svg?branch=master)](https://travis-ci.com/ape364/aioidex)
[![Coveralls](https://img.shields.io/coveralls/ape364/aioidex.svg)](https://coveralls.io/github/ape364/aioidex)
[![Versions](https://img.shields.io/pypi/pyversions/aioidex.svg)](https://pypi.org/project/aioidex/)


[Idex](https://idex.market/) [API](https://docs.idex.market/) async Python non-official wrapper. Tested only with Python 3.7.

## Features

### REST API 

Does not support [HTTP API](https://docs.idex.market/#tag/HTTP-API-Introduction) yet.

### Datastream Realtime API

Full [Datastream realtime API](https://docs.idex.market/#tag/Datastream-Introduction) support (via [websockets](https://github.com/aaugustin/websockets)).

## Installation

```sh
pip install -U aioidex
```

## Usage

```python
import asyncio

from aioidex import IdexDatastream
from aioidex.types.events import MarketEvents, ChainEvents
from aioidex.types.subscriptions import MarketSubscription, ChainSubscription


def get_subs():
    return [
        MarketSubscription([MarketEvents.ORDERS], ['ETH_AURA', 'ETH_KIN']),
        ChainSubscription([ChainEvents.SERVER_BLOCK]),
    ]


async def main():
    ds = IdexDatastream()

    for sub in get_subs():
        await ds.sub_manager.subscribe(sub)

    # # init connection manually
    # await ds.init()
    # # or pass an already exists connection
    # ws = await ds.create_connection()
    # await ds.init(ws)

    # or simply start to listen, connection will be created automatically
    async for msg in ds.listen():
        print(msg)


if __name__ == '__main__':
    asyncio.run(main())
```