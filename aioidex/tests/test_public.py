import pytest
from asynctest import CoroutineMock, patch

from aioidex import Client
from aioidex.http.modules.public import Public


@pytest.fixture()
async def p():
    with patch('aioidex.http.network.Network._init_session', new=CoroutineMock) as m:
        c = Client()
        yield c.public


@pytest.mark.asyncio
async def test_ticker(p: Public):
    p._post = CoroutineMock()
    await p.ticker('some market')
    p._post.assert_awaited_once_with('returnTicker', {'market': 'some market'})


@pytest.mark.asyncio
async def test_currencies(p: Public):
    p._post = CoroutineMock()
    await p.currencies()
    p._post.assert_awaited_once_with('returnCurrencies')


@pytest.mark.asyncio
async def test_volume_24hr(p: Public):
    p._post = CoroutineMock()
    await p.volume_24hr()
    p._post.assert_awaited_once_with('return24Volume')


@pytest.mark.asyncio
async def test_balances(p: Public):
    p._post = CoroutineMock()
    await p.balances('some addr')
    p._post.assert_awaited_once_with('returnBalances', {'address': 'some addr'})


@pytest.mark.asyncio
async def test_complete_balances(p: Public):
    p._post = CoroutineMock()
    await p.complete_balances('some addr')
    p._post.assert_awaited_once_with('returnCompleteBalances', {'address': 'some addr'})


@pytest.mark.asyncio
async def test_deposits_withdrawals(p: Public):
    p._post = CoroutineMock()
    await p.deposits_withdrawals('some addr', 1, 2)
    p._post.assert_awaited_once_with('returnDepositsWithdrawals', {'address': 'some addr', 'start': 1, 'end': 2})


@pytest.mark.asyncio
async def test_open_orders(p: Public):
    with pytest.raises(ValueError) as excinfo:
        await p.open_orders()
    assert str(excinfo.value) == 'Either market or address is required.'

    p._post = CoroutineMock()
    await p.open_orders(market='ETH_AURA')
    p._post.assert_awaited_once_with(
        'returnOpenOrders',
        {'market': 'ETH_AURA', 'address': None, 'count': None, 'cursor': None}
    )

    p._post = CoroutineMock()
    await p.open_orders(address='some address')
    p._post.assert_awaited_once_with(
        'returnOpenOrders',
        {'market': None, 'address': 'some address', 'count': None, 'cursor': None}
    )

    p._post = CoroutineMock()
    params = {'market': 'some market', 'address': 'some address', 'count': 1, 'cursor': 2}
    await p.open_orders(**params)
    p._post.assert_awaited_once_with(
        'returnOpenOrders',
        {'market': 'some market', 'address': 'some address', 'count': 1, 'cursor': 2}
    )


@pytest.mark.asyncio
async def test_order_book(p: Public):
    with pytest.raises(ValueError) as excinfo:
        await p.order_book('ETH_AURA', 102)
    assert str(excinfo.value) == 'Count must be in the interval [ 1 .. 100 ]'

    p._post = CoroutineMock()
    await p.order_book('ETH_AURA')
    p._post.assert_awaited_once_with('returnOrderBook', {'market': 'ETH_AURA', 'count': None})


@pytest.mark.asyncio
async def test_order_status(p: Public):
    p._post = CoroutineMock()
    await p.order_status('some hash')
    p._post.assert_awaited_once_with('returnOrderStatus', {'orderHash': 'some hash'})


@pytest.mark.asyncio
async def test_order_trades(p: Public):
    p._post = CoroutineMock()
    await p.order_trades('some hash')
    p._post.assert_awaited_once_with('returnOrderTrades', {'orderHash': 'some hash'})


@pytest.mark.asyncio
async def test_trade_history(p: Public):
    with pytest.raises(ValueError) as excinfo:
        await p.trade_history()
    assert str(excinfo.value) == 'Either market or address is required.'

    with pytest.raises(ValueError) as excinfo:
        await p.trade_history('ETH_AURA', count=102)
    assert str(excinfo.value) == 'Count must be in the interval [ 1 .. 100 ]'

    with pytest.raises(ValueError) as excinfo:
        await p.trade_history(address='some addr', sort='wrong')
    assert str(excinfo.value) == 'Possible values are asc (oldest first) and desc (newest first). Defaults to desc.'

    p._post = CoroutineMock()
    params = {
        'market': 'some market',
        'address': 'some address',
        'start': 0,
        'end': 1,
        'sort': 'asc',
        'count': 2,
        'cursor': 3
    }
    await p.trade_history(**params)
    p._post.assert_awaited_once_with(
        'returnTradeHistory',
        {
            'market': 'some market',
            'address': 'some address',
            'start': 0,
            'end': 1,
            'sort': 'asc',
            'count': 2,
            'cursor': 3
        }
    )


@pytest.mark.asyncio
async def test_contract_address(p: Public):
    p._post = CoroutineMock()
    await p.contract_address()
    p._post.assert_awaited_once_with('returnContractAddress')


@pytest.mark.asyncio
async def test_next_nonce(p: Public):
    p._post = CoroutineMock()
    await p.next_nonce('some addr')
    p._post.assert_awaited_once_with('returnNextNonce', {'address': 'some addr'})
