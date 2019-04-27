from unittest.mock import patch, call

import pytest

from aioidex.types.events import MarketEvents, AccountEvents, ChainEvents
from aioidex.types.subscriptions import Category, AccountSubscription, MarketSubscription, ChainSubscription
from aioidex.types.subscriptions import Subscription


@pytest.fixture()
def sub():
    s = Subscription(
        category=Category.MARKET,
        events=[MarketEvents.ORDERS, MarketEvents.CANCELS],
        topics=['ETH_ZRX', 'ETH_AURA']
    )
    yield s


def test_sub_init():
    category = Category.MARKET
    events = [MarketEvents.ORDERS, MarketEvents.CANCELS]
    topics = ['ETH_ZRX', 'ETH_AURA']

    with patch('aioidex.types.subscriptions.Subscription._normalize') as m:
        s = Subscription(
            category=category,
            events=events,
            topics=topics
        )
        m.assert_has_calls(
            [
                call(events),
                call(topics)
            ]
        )
        assert isinstance(s.category, Category)
        assert s.category == category


def test_normalize(sub: Subscription):
    assert isinstance(sub._normalize([]), tuple)
    assert sub._normalize(['b', 'c', 'a']) == ('A', 'B', 'C')
    assert sub._normalize(['b', MarketEvents.TRADES, 'a']) == ('A', 'B', MarketEvents.TRADES.value)
    assert sub._normalize(
        [MarketEvents.ORDERS, MarketEvents.CANCELS]
    ) == (MarketEvents.CANCELS.value, MarketEvents.ORDERS.value)


def test_check_events(sub: Subscription):
    evts = [MarketEvents.ORDERS, MarketEvents.ORDERS]
    assert sub._check_events(evts, MarketEvents) == evts
    with pytest.raises(ValueError):
        sub._check_events([AccountEvents.ORDERS, AccountEvents.TRADES], MarketEvents)
    assert sub._check_events(
        [AccountEvents.TRADES.value, AccountEvents.CANCELS.value], AccountEvents
    ) == [AccountEvents.TRADES.value, AccountEvents.CANCELS.value, ]


def test_account_subscription():
    with pytest.raises(ValueError):
        AccountSubscription(
            events=[AccountEvents.TRADES],
            addresses=['qwe']
        )

    s = AccountSubscription(
        events=[AccountEvents.TRADES],
        addresses=['0xcdcfc0f66c522fd086a1b725ea3c0eeb9f9e8814']
    )

    assert s.category == Category.ACCOUNT
    assert s.events == ('account_trades',)
    assert s.topics == ('0XCDCFC0F66C522FD086A1B725EA3C0EEB9F9E8814',)


def test_market_subscription():
    with pytest.raises(ValueError):
        MarketSubscription(
            events=[MarketEvents.CANCELS],
            markets=['qwe']
        )

    s = MarketSubscription(
        events=[MarketEvents.CANCELS],
        markets=['eth_aura']
    )

    assert s.category == Category.MARKET
    assert s.events == ('market_cancels',)
    assert s.topics == ('ETH_AURA',)


def test_chain_subscription():
    s = ChainSubscription(events=[ChainEvents.GAS_PRICE])

    assert s.category == Category.CHAIN
    assert s.events == ('chain_gas_price',)
    assert s.topics == ('ETH',)
