# aioidex

[![PyPi](https://img.shields.io/pypi/v/aioidex.svg)](https://pypi.org/project/aioidex/)
[![License](https://img.shields.io/pypi/l/aioidex.svg)](https://pypi.org/project/aioidex/)
[![Build](https://travis-ci.com/ape364/aioidex.svg?branch=master)](https://travis-ci.com/ape364/aioidex)
[![Coveralls](https://img.shields.io/coveralls/ape364/aioidex.svg)](https://coveralls.io/github/ape364/aioidex)
[![Versions](https://img.shields.io/pypi/pyversions/aioidex.svg)](https://pypi.org/project/aioidex/)


[Idex](https://idex.market/) [API](https://docs.idex.market/) async Python non-official wrapper. Tested only with Python 3.7.

## Features

### REST API 

Supports only [public read-only endpoints](https://docs.idex.market/#group/HTTP-API) at this moment.

### Datastream Realtime API

Full [Datastream realtime API](https://docs.idex.market/#tag/Datastream-Introduction) support (via [websockets](https://github.com/aaugustin/websockets)).

## Installation

```sh
pip install -U aioidex
```

## Usage

### Datastream

```python

import asyncio

from aioidex import IdexDatastream, MarketEvents, MarketSubscription, ChainSubscription, ChainEvents


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

### HTTP
```python

import asyncio

from aioidex import Client


async def main():
    c = Client()

    try:
        result = await c.public.ticker()
    except Exception as e:
        print(f'Error ({type(e).__name__}): {e}')
    else:
        print(result)
    finally:
        await c.close()


if __name__ == '__main__':
    asyncio.run(main())
```