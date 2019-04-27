import re
from enum import Enum, EnumMeta
from typing import Tuple, List, Union

from aioidex.types.events import AccountEvents, MarketEvents, ChainEvents


class Category(Enum):
    ACCOUNT = 'subscribeToAccounts'
    MARKET = 'subscribeToMarkets'
    CHAIN = 'subscribeToChains'


class Action(Enum):
    SUBSCRIBE = 'subscribe'
    GET = 'get'
    UNSUBSCRIBE = 'unsubscribe'
    CLEAR = 'clear'


class Subscription:
    category: Category = None
    _events: Tuple[str] = None
    _topics: Tuple[str] = None

    def __init__(self, category: Category, events: List[Enum], topics: List[str]) -> None:
        self.category = category
        self.events = events
        self.topics = topics

    def __str__(self):
        return f'Subscription(category={self.category}, events={self.events}, topics={self.topics})'

    @property
    def events(self) -> Tuple[str]:
        return self._events

    @events.setter
    def events(self, value: List[Union[Enum, str]]):
        self._events = self._normalize(value)

    @property
    def topics(self) -> Tuple[str]:
        return self._topics

    @topics.setter
    def topics(self, value: List[str]):
        self._topics = self._normalize(value)

    @staticmethod
    def _normalize(data: List[Union[str, Enum]]) -> Tuple[str]:
        result = set()

        for i in data:
            if isinstance(i, Enum):
                item = i.value
            elif isinstance(i, str):
                item = i.strip().upper()
            else:
                continue

            result.add(item)

        return tuple(sorted(result))

    @staticmethod
    def _check_events(events: List[Enum], enum_cls: EnumMeta):
        for event in events:
            enum_cls(event)

        return events


class AccountSubscription(Subscription):
    __ETH_ADDRESS = re.compile(r'0x[a-fA-F0-9]{40}')

    def __init__(self, events: List[AccountEvents], addresses: List[str]):
        super().__init__(
            Category.ACCOUNT,
            self._check_events(events, AccountEvents),
            self._check_addresses(addresses)
        )

    def _check_addresses(self, addresses: List[str]) -> List[str]:
        for address in addresses:
            if not self.__ETH_ADDRESS.match(address):
                raise ValueError(
                    f'Invalid Ethereum address {address!r}, must match regex {self.__ETH_ADDRESS.pattern!r}'
                )

        return addresses


class MarketSubscription(Subscription):
    __MARKET_VALIDATE_REGEX = re.compile(r'[A-Za-z0-9]+_[A-Za-z0-9]+')

    def __init__(self, events: List[MarketEvents], markets: List[str]):
        super().__init__(
            Category.MARKET,
            self._check_events(events, MarketEvents),
            self._check_markets(markets)
        )

    def _check_markets(self, markets: List[str]) -> List[str]:
        for market in markets:
            if not self.__MARKET_VALIDATE_REGEX.match(market):
                raise ValueError(
                    f'Invalid market {market}, must match regex {self.__MARKET_VALIDATE_REGEX.pattern}'
                )
        return markets


class ChainSubscription(Subscription):
    def __init__(self, events: List[ChainEvents]):
        super().__init__(
            Category.CHAIN,
            self._check_events(events, ChainEvents),
            ['ETH', ]
        )
