from logging import Logger

import pytest
from asynctest import Mock, patch, CoroutineMock

from aioidex import IdexDatastream
from aioidex.datastream.sub_manager import SubscriptionManager
from aioidex.types.events import MarketEvents
from aioidex.types.subscriptions import Category, Subscription, Action


@pytest.fixture()
async def sm():
    ds = IdexDatastream()
    yield ds.sub_manager


@pytest.mark.asyncio
async def test_init():
    datastream = Mock()
    return_sub_responses = False

    with patch('aioidex.datastream.sub_manager.SubscriptionManager._init_subscriptions') as mock:
        sm = SubscriptionManager(datastream, return_sub_responses)
        mock.assert_called_once()
        assert sm._ds is datastream
        assert sm._return_responses == return_sub_responses
        assert isinstance(sm._logger, Logger)
        assert sm._CATEGORY_VALUES == set(_.value for _ in Category)


@pytest.mark.asyncio
async def test_subscribe(sm: SubscriptionManager):
    send_mock = CoroutineMock()
    send_mock.return_value = 'some return value'
    sm._ds.send_message = send_mock

    sm._sub_payload = Mock()
    sub_payload_value = 'some value'
    sm._sub_payload.return_value = sub_payload_value

    sub = Subscription(
        category=Category.MARKET,
        events=[MarketEvents.CANCELS, MarketEvents.ORDERS],
        topics=['ETH_AURA', 'ETH_ZRX']
    )

    result = await sm.subscribe(sub)

    sm._sub_payload.assert_called_once_with(
        Action.SUBSCRIBE,
        topics=sub.topics,
        events=sub.events
    )
    send_mock.assert_awaited_once_with(
        sub.category.value,
        sub_payload_value,
        None
    )
    assert result == 'some return value'


@pytest.mark.asyncio
async def test_subscribe_warning(sm: SubscriptionManager):
    sm._logger.warning = Mock()

    send_mock = CoroutineMock()
    send_mock.return_value = 'some return value'
    sm._ds.send_message = send_mock

    sm._sub_payload = Mock()
    sub_payload_value = 'some value'
    sm._sub_payload.return_value = sub_payload_value

    sub = Subscription(
        category=Category.MARKET,
        events=[MarketEvents.CANCELS, MarketEvents.ORDERS],
        topics=['ETH_AURA', 'ETH_ZRX']
    )

    sm.subscriptions[sub.category] = {}

    result = await sm.subscribe(sub)

    sm._logger.warning.assert_called_once()

    sm._sub_payload.assert_called_once_with(
        Action.SUBSCRIBE,
        topics=sub.topics,
        events=sub.events
    )
    send_mock.assert_awaited_once_with(
        sub.category.value,
        sub_payload_value,
        None
    )
    assert result == 'some return value'


@pytest.mark.asyncio
async def test_subscribe_rid(sm: SubscriptionManager):
    send_mock = CoroutineMock()
    send_mock.return_value = 'some return value'
    sm._ds.send_message = send_mock

    sm._sub_payload = Mock()
    sub_payload_value = 'some value'
    sm._sub_payload.return_value = sub_payload_value

    sub = Subscription(
        category=Category.MARKET,
        events=[MarketEvents.CANCELS, MarketEvents.ORDERS],
        topics=['ETH_AURA', 'ETH_ZRX']
    )

    result = await sm.subscribe(sub, 'some rid')

    sm._sub_payload.assert_called_once_with(
        Action.SUBSCRIBE,
        topics=sub.topics,
        events=sub.events
    )
    send_mock.assert_awaited_once_with(
        sub.category.value,
        sub_payload_value,
        'some rid'
    )
    assert result == 'some return value'


@pytest.mark.asyncio
async def test_get(sm: SubscriptionManager):
    sm._ds.send_message = CoroutineMock(return_value='some return value')
    sm._sub_payload = Mock(return_value='some value')

    category = Category.MARKET

    result = await sm.get(category)

    sm._sub_payload.assert_called_once_with(Action.GET)
    sm._ds.send_message.assert_awaited_once_with(category.value, 'some value', None)

    assert result == 'some return value'


@pytest.mark.asyncio
async def test_get_rid(sm: SubscriptionManager):
    sm._ds.send_message = CoroutineMock(return_value='some return value')
    sm._sub_payload = Mock(return_value='some value')

    category = Category.MARKET

    result = await sm.get(category, 'some_rid')

    sm._sub_payload.assert_called_once_with(Action.GET)
    sm._ds.send_message.assert_awaited_once_with(category.value, 'some value', 'some_rid')

    assert result == 'some return value'


@pytest.mark.asyncio
async def test_unsubscribe(sm: SubscriptionManager):
    sm._ds.send_message = CoroutineMock(return_value='some return value')
    sm._sub_payload = Mock(return_value='some value')

    category = Category.MARKET

    result = await sm.unsubscribe(category, ['ETH_AURA'])

    sm._sub_payload.assert_called_once_with(Action.UNSUBSCRIBE, ['ETH_AURA'])
    sm._ds.send_message.assert_awaited_once_with(category.value, 'some value', None)

    assert result == 'some return value'


@pytest.mark.asyncio
async def test_unsubscribe_rid(sm: SubscriptionManager):
    sm._ds.send_message = CoroutineMock(return_value='some return value')
    sm._sub_payload = Mock(return_value='some value')

    category = Category.MARKET

    result = await sm.unsubscribe(category, ['ETH_AURA'], 'some_rid')

    sm._sub_payload.assert_called_once_with(Action.UNSUBSCRIBE, ['ETH_AURA'])
    sm._ds.send_message.assert_awaited_once_with(category.value, 'some value', 'some_rid')

    assert result == 'some return value'


@pytest.mark.asyncio
async def test_clear(sm: SubscriptionManager):
    sm._ds.send_message = CoroutineMock(return_value='some return value')
    sm._sub_payload = Mock(return_value='some value')

    category = Category.MARKET

    result = await sm.clear(category)

    sm._sub_payload.assert_called_once_with(Action.CLEAR)
    sm._ds.send_message.assert_awaited_once_with(category.value, 'some value', None)

    assert result == 'some return value'


@pytest.mark.asyncio
async def test_clear_rid(sm: SubscriptionManager):
    sm._ds.send_message = CoroutineMock(return_value='some return value')
    sm._sub_payload = Mock(return_value='some value')

    category = Category.MARKET

    result = await sm.clear(category, 'some_rid')

    sm._sub_payload.assert_called_once_with(Action.CLEAR)
    sm._ds.send_message.assert_awaited_once_with(category.value, 'some value', 'some_rid')

    assert result == 'some return value'


@pytest.mark.asyncio
async def test_resubscribe(sm: SubscriptionManager):
    sub = Subscription(
        category=Category.MARKET,
        events=[MarketEvents.CANCELS, MarketEvents.ORDERS],
        topics=['ETH_AURA', 'ETH_ZRX']
    )
    sm.subscriptions = {Category.MARKET: sub}

    sm._init_subscriptions = Mock()
    sm.subscribe = CoroutineMock()

    await sm.resubscribe()

    sm._init_subscriptions.assert_called_once()
    sm.subscribe.assert_awaited_once_with(sub)


def test_is_sub_response(sm: SubscriptionManager):
    assert sm.is_sub_response({'request': Category.MARKET.value}) is True
    assert sm.is_sub_response({'request': 'not sub'}) is False


def test_process_sub_response_error(sm: SubscriptionManager):
    message = dict(
        result='error',
        request='subscribeToMarkets',
        payload=dict(
            action='get'
        ),
    )

    sm._logger.error = Mock()

    result = sm.process_sub_response(message)

    sm._logger.error.assert_called_once_with('Subscription error: %s', message)
    assert result is None


def test_process_sub_response_no_handler(sm: SubscriptionManager):
    message = dict(
        result='success',
        request='subscribeToMarkets',
        payload=dict(
            action='unknown'
        ),
    )

    sm._logger.error = Mock()

    result = sm.process_sub_response(message)

    sm._logger.error.assert_called_once_with('Handler for the subscription response not found: %s', message)
    assert result is None


def test_process_sub_response_get_handler(sm: SubscriptionManager):
    message = dict(
        result='success',
        request='subscribeToMarkets',
        payload=dict(
            action='get'
        ),
    )

    sm._logger.error = Mock()
    sm._process_get_action_response = Mock()

    result = sm.process_sub_response(message)

    sm._process_get_action_response.assert_called_once_with(Category(message['request']), message['payload'])
    assert result is None


def test_process_sub_response_get_handler_return_response(sm: SubscriptionManager):
    message = dict(
        result='success',
        request='subscribeToMarkets',
        payload=dict(
            action='get'
        ),
    )

    sm._logger.error = Mock()
    sm._process_get_action_response = Mock()

    sm._return_responses = True

    result = sm.process_sub_response(message)

    sm._process_get_action_response.assert_called_once_with(Category(message['request']), message['payload'])
    assert result == message


def test_process_subscribe_action_response(sm: SubscriptionManager):
    category = Category.MARKET
    events = [MarketEvents.ORDERS, MarketEvents.CANCELS]
    topics = ['ETH_AURA', 'ETH_ZRX']
    payload = dict(
        events=events,
        topics=topics
    )

    assert sm.subscriptions == {}

    sm._process_subscribe_action_response(category, payload)

    assert category in sm.subscriptions
    sub = sm.subscriptions[category]
    assert sub.category == category

    assert len(sub.events) == len(events)
    assert sub.events == (MarketEvents.CANCELS.value, MarketEvents.ORDERS.value)

    assert len(sub.topics) == len(topics)
    assert sub.topics == ('ETH_AURA', 'ETH_ZRX')


def test_process_get_action_response(sm: SubscriptionManager):
    category = Category.MARKET
    events = [MarketEvents.ORDERS, MarketEvents.CANCELS]
    topics = ['ETH_AURA', 'ETH_ZRX']
    payload = dict(
        events=events,
        topics=topics
    )

    assert sm.subscriptions == {}

    sm._process_get_action_response(category, payload)

    assert sm.subscriptions == {}

    sm._process_subscribe_action_response(category, payload)

    payload['topics'] = ['ETH_SAN']
    old_events = sm.subscriptions[category].events
    sm._process_get_action_response(category, payload)

    assert sm.subscriptions[category].events == old_events
    assert sm.subscriptions[category].topics == ('ETH_SAN',)


def test_process_unsubscribe_action_response(sm: SubscriptionManager):
    category = Category.MARKET
    events = [MarketEvents.ORDERS, MarketEvents.CANCELS]
    topics = ['ETH_AURA', 'ETH_ZRX']
    payload = dict(
        events=events,
        topics=topics
    )

    sm._process_subscribe_action_response(category, payload)

    old_topics = sm.subscriptions[category].topics
    sm._process_unsubscribe_action_response(Category.CHAIN, payload)
    assert old_topics == sm.subscriptions[category].topics

    topics = ['ETH_AURA']
    payload = dict(
        events=events,
        topics=topics
    )
    sm._process_unsubscribe_action_response(category, payload)
    assert sm.subscriptions[category].topics == ('ETH_AURA',)


def test_process_clear_action_response(sm: SubscriptionManager):
    category = Category.MARKET
    events = [MarketEvents.ORDERS, MarketEvents.CANCELS]
    topics = ['ETH_AURA', 'ETH_ZRX']
    payload = dict(
        events=events,
        topics=topics
    )

    sm._process_subscribe_action_response(category, payload)

    assert len(sm.subscriptions[category].topics) == len(topics)

    sm._process_clear_action_response(category, payload)

    assert len(sm.subscriptions[category].topics) == 0


def test_init_subscriptions(sm: SubscriptionManager):
    sm._init_subscriptions()

    assert isinstance(sm.subscriptions, dict)
    assert sm.subscriptions == {}


def test_sub_payload(sm: SubscriptionManager):
    sm._filter_none = Mock(return_value='value')
    params = dict(
        action=Action.SUBSCRIBE,
        topics=['ETH_AURA'],
        events=MarketEvents.ORDERS
    )

    result = sm._sub_payload(**params)

    sm._filter_none.assert_called_once_with(
        dict(
            action=Action.SUBSCRIBE.value,
            topics=['ETH_AURA'],
            events=MarketEvents.ORDERS
        )
    )

    assert result == 'value'


def test_filter_none(sm: SubscriptionManager):
    assert sm._filter_none({1: 2}) == {1: 2}
    assert sm._filter_none({1: 2, 3: None}) == {1: 2}
