from typing import Dict, List

from aioidex.http.modules.base import BaseModule


class Public(BaseModule):
    """Read-Only Endpoints

    https://docs.idex.market/#tag/Read-Only-Endpoints
    """

    async def ticker(self, market: str = None) -> Dict:
        """Designed to behave similar to the API call of the same name provided by the Poloniex HTTP API, with the addition of highs and lows. Returns all necessary 24 hr data.

        https://docs.idex.market/#operation/returnTicker
        """
        return await self._post('returnTicker', {'market': market}, )

    async def currencies(self) -> Dict:
        """Returns an object of token data indexed by symbol.

        https://docs.idex.market/#operation/returnCurrencies
        """
        return await self._post('returnCurrencies')

    async def volume_24hr(self) -> Dict:
        """Returns the 24-hour volume for all markets, plus totals for primary currencies.

        https://docs.idex.market/#operation/return24Volume
        """
        return await self._post('return24Volume')

    async def balances(self, address: str) -> Dict:
        """Returns available balances for an address(total deposited minus amount in open orders) indexed by token symbol.

        https://docs.idex.market/#operation/returnBalances
        """
        return await self._post('returnBalances', {'address': address})

    async def complete_balances(self, address: str) -> Dict:
        """Returns available balances for an address along with the amount of open orders for each token, indexed by token symbol.

        https://docs.idex.market/#operation/returnCompleteBalances
        """
        return await self._post('returnCompleteBalances', {'address': address})

    async def deposits_withdrawals(self, address: str, start: int = None, end: int = None) -> Dict:
        """Returns your deposit and withdrawal history within a range, specified by the "start" and "end" properties of the JSON input, both of which must be UNIX timestamps.

        https://docs.idex.market/#operation/returnDepositsWithdrawals
        """
        return await self._post('returnDepositsWithdrawals', {'address': address, 'start': start, 'end': end})

    async def open_orders(
            self,
            market: str = None,
            address: str = None,
            count: int = None,
            cursor: int = None
    ) -> List[Dict]:
        """Returns a paginated list of all open orders for a given market or address.

        https://docs.idex.market/#operation/returnOpenOrders
        """
        if not market and not address:
            raise ValueError('Either market or address is required.')

        if count is not None and count not in range(1, 101):
            raise ValueError('Count must be in the interval [ 1 .. 100 ]')

        return await self._post(
            'returnOpenOrders',
            {'market': market, 'address': address, 'count': count, 'cursor': cursor}
        )

    async def order_book(self, market: str, count: int = None) -> Dict:
        """Returns the best-priced open orders for a given market.

        https://docs.idex.market/#operation/returnOrderBook
        """
        if count is not None and count not in range(1, 101):
            raise ValueError('Count must be in the interval [ 1 .. 100 ]')

        return await self._post('returnOrderBook', {'market': market, 'count': count})

    async def order_status(self, order_hash: str) -> Dict:
        """Returns a single order.

        https://docs.idex.market/#operation/returnOrderStatus
        """
        return await self._post('returnOrderStatus', {'orderHash': order_hash})

    async def order_trades(self, order_hash: str) -> List[Dict]:
        """Returns all trades involving a given order hash.

        https://docs.idex.market/#operation/returnOrderTrades
        """
        return await self._post('returnOrderTrades', {'orderHash': order_hash})

    async def trade_history(
            self,
            market: str = None,
            address: str = None,
            start: int = None,
            end: int = None,
            sort: str = None,
            count: int = None,
            cursor: int = None
    ) -> List[Dict]:
        """Returns a paginated list of all trades for a given market or address, sorted by date.

        https://docs.idex.market/#operation/returnTradeHistory
        """
        if not market and not address:
            raise ValueError('Either market or address is required.')

        if count is not None and count not in range(1, 101):
            raise ValueError('Count must be in the interval [ 1 .. 100 ]')

        if sort is not None and sort not in ('asc', 'desc'):
            raise ValueError('Possible values are asc (oldest first) and desc (newest first). Defaults to desc.')

        return await self._post(
            'returnTradeHistory',
            {
                'market': market,
                'address': address,
                'start': start,
                'end': end,
                'sort': sort,
                'count': count,
                'cursor': cursor
            }
        )

    async def contract_address(self) -> Dict:
        """Returns the contract address used for depositing, withdrawing, and posting orders.

        https://docs.idex.market/#operation/returnContractAddress
        """
        return await self._post('returnContractAddress')

    async def next_nonce(self, address: str) -> Dict:
        """Returns the lowest nonce that you can use from the given address in one of the contract-backed trade functions.

        https://docs.idex.market/#operation/returnNextNonce
        """
        return await self._post('returnNextNonce', {'address': address})
