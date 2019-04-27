from __future__ import annotations  # PEP 563

import logging
from typing import Dict, List, Iterable
from typing import TYPE_CHECKING

from aioidex.types.subscriptions import Subscription, Category, Action

# PEP 563
if TYPE_CHECKING:
    from aioidex.datastream import IdexDatastream


class SubscriptionManager:
    _CATEGORY_VALUES = set(_.value for _ in Category)
    subscriptions: Dict[Category, Subscription]

    def __init__(self, datastream: IdexDatastream, return_responses: bool):
        self._init_subscriptions()

        self._ds = datastream
        self._return_responses = return_responses

        self._logger = logging.getLogger(__name__)

    async def subscribe(self, subscription: Subscription, rid: str = None) -> str:
        self._logger.info('Sending subscribe request: %s', subscription)
        if subscription.category in self.subscriptions:
            self._logger.warning(
                'Already subscribed to category %s: %s. '
                'Replacing current subscriptions for the category with the newly provided values',
                subscription.category,
                self.subscriptions[subscription.category]
            )
        return await self._ds.send_message(
            subscription.category.value,
            self._sub_payload(Action.SUBSCRIBE, topics=subscription.topics, events=subscription.events),
            rid
        )

    async def get(self, category: Category, rid: str = None) -> str:
        return await self._ds.send_message(category.value, self._sub_payload(Action.GET), rid)

    async def unsubscribe(self, category: Category, topics: List[str], rid: str = None) -> str:
        return await self._ds.send_message(category.value, self._sub_payload(Action.UNSUBSCRIBE, topics), rid)

    async def clear(self, category: Category, rid: str = None) -> str:
        return await self._ds.send_message(category.value, self._sub_payload(Action.CLEAR), rid)

    async def resubscribe(self):
        subs = self.subscriptions.values()
        self._init_subscriptions()
        for sub in subs:
            await self.subscribe(sub)

    def is_sub_response(self, response: Dict) -> bool:
        return response.get('request') in self._CATEGORY_VALUES

    def process_sub_response(self, message: Dict):
        self._logger.debug('Subscription response: %s', message)

        success = message['result'] == 'success'
        category = Category(message['request'])
        payload = message['payload']
        action = payload['action']

        if not success:
            self._logger.error('Subscription error: %s', message)  # raise an exception?
            return

        handler = {
            'subscribe': self._process_subscribe_action_response,
            'get': self._process_get_action_response,
            'unsubscribe': self._process_unsubscribe_action_response,
            'clear': self._process_clear_action_response,
        }.get(action)

        if not handler:
            self._logger.error('Handler for the subscription response not found: %s', message)  # raise an exception?
            return

        handler(category, payload)
        if self._return_responses:
            return message

    def _init_subscriptions(self):
        self.subscriptions = {}

    def _process_subscribe_action_response(self, category: Category, payload: Dict):
        self.subscriptions[category] = Subscription(
            category,
            payload['events'],
            payload['topics']
        )
        self._logger.info('Successfully subbed to category %s: %s', category, payload)

    def _process_get_action_response(self, category: Category, payload: Dict):
        if category in self.subscriptions:
            self.subscriptions[category].topics = payload['topics']
            self._logger.info('%s got topics: %s', category, payload)

    def _process_unsubscribe_action_response(self, category: Category, payload: Dict):
        if category in self.subscriptions:
            unsubbed_topics = list(set(self.subscriptions[category].topics) - set(payload['topics']))
            self._logger.info('%s unsubscribed from topics: %s', category, unsubbed_topics)
            self.subscriptions[category].topics = payload['topics']

    def _process_clear_action_response(self, category: Category, payload: Dict):
        if category in self.subscriptions:
            self.subscriptions[category].topics = []
            self._logger.info('%s clear subscriptions: %s', category, payload)

    def _sub_payload(self, action: Action, topics: Iterable[str] = None, events: Iterable[str] = None):
        return self._filter_none(
            dict(
                action=action.value,
                topics=topics,
                events=events
            )
        )

    @staticmethod
    def _filter_none(data: Dict) -> Dict:
        return {k: v for k, v in data.items() if v is not None}
