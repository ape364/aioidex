from enum import unique, Enum


@unique
class AccountEvents(Enum):
    """This request allows you to handle subscription for account-level events.

    These include updates on an accounts balances, nonce, trade actions (across all markets), and more.
    For subscribeToAccounts, topics are represented as the ethereum address for your account(s) that you wish to monitor
    """

    # Received whenever the subscribed accounts nonce has been updated.
    # This new nonce must be used as the base nonce for all future requests.
    NONCE = 'account_nonce'

    # Received when a deposit is received and credited to the account.
    # At this point the deposited funds are available for trading.
    DEPOSIT_COMPLETE = 'account_deposit_complete'

    # When the subscribed account has new orders received and processed by the exchange, this event will be provided
    # including each of the orders that were processed in the given batch.
    # At this point the orders should be considered pending.
    ORDERS = 'account_orders'

    # When the subscribed account has new cancels received and processed by the exchange, this event will be provided
    # including each of the cancels that were processed in the given batch.
    # At this point the cancels should be considered pending
    CANCELS = 'account_cancels'

    # When the subscribed account has new trades received and processed by the exchange, this event will be provided
    # including each of the trades that were processed in the given batch.
    # At this point the trades should be considered pending.
    TRADES = 'account_trades'

    # A withdrawal request is first received by the server and queued to be dispatched to the blockchain.
    # At this point the withdrawal should be considered as pending.
    WITHDRAWAL_CREATED = 'account_withdrawal_created'

    # A withdrawal request is first dispatched to the blockchain.
    # At this point the withdrawal should be considered as confirming.
    WITHDRAWAL_DISPATCHED = 'account_withdrawal_dispatched'

    # A withdrawal request is considered confirmed.
    WITHDRAWAL_COMPLETE = 'account_withdrawal_complete'

    # A trade request is first dispatched to the blockchain.
    # At this point the trade should be considered as confirming.
    TRADE_DISPATCHED = 'account_trade_dispatched'

    # A trade request is considered confirmed.
    TRADE_COMPLETE = 'account_trade_complete'

    # An invalidation request is first dispatched to the blockchain.
    # At this point the invalidation should be considered as confirming.
    INVALIDATION_DISPATCHED = 'account_invalidation_dispatched'

    # An invalidation is considered confirmed.
    INVALIDATION_COMPLETE = 'account_invalidation_complete'

    # The updated balance sheet for the account. Triggered whenever the accounts balances are updated by a given action
    # and includes all non-zero balances for the account. Balances are represented as WEI.
    BALANCE_SHEET = 'account_balance_sheet'

    # Provides updates on the subscribed account's AURA rewards.
    REWARDS = 'account_rewards'


@unique
class MarketEvents(Enum):
    """This request allows you to handle subscription for market-level events.

    These generally are limited to trade-action events such as orders, cancels, and trades.
    Topics for subscribeToMarkets are the markets which you wish to receive updates for. These markets will general be
    formatted like ${base_token}_${trade_token} (ETH_AURA, WBTC_AURA).
    """

    # Provides an aggregated group of new orders which have occurred on the subscribed market.
    ORDERS = 'market_orders'

    # Provides an aggregated group of new cancels which have occurred on the subscribed market.
    CANCELS = 'market_cancels'

    # Provides an aggregated group of new trades which have occurred on the subscribed market.
    TRADES = 'market_trades'

    # Provides events on the subscribed markets listing status, action will be either listed, delisted, or renamed.
    LISTING = 'market_listing'


@unique
class ChainEvents(Enum):
    """This request allows you to handle subscription for chain-level events.

    These generally provide general status events and metadata updates.
    At this time the only available topic is ETH.
    """

    # When the IDEX internal backend transitions to different states, such as temporarily disabled trading, this event
    # will be dispatched.
    STATUS = 'chain_status'

    # Provides listing events to capture new listings or updates to listed markets.
    # Current possible action values are: listed, delisted, and renamed.
    MARKET_LISTING = 'chain_market_listing'

    # This event is dispatched to provide the current block that the IDEX Backend is currently processing.
    SERVER_BLOCK = 'chain_server_block'

    # Receives the latest usd pricing used by the exchange for the given symbol.
    SYMBOL_USD_PRICE = 'chain_symbol_usd_price'

    # Provides updates on the current total reward pool volume size for AURA rewards calculations.
    REWARD_POOL_SIZE = 'chain_reward_pool_size'

    # Provides the latest gas price in GWEI used by the exchange.
    GAS_PRICE = 'chain_gas_price'

    # Provides the previous 24 hour volume (in USD) to the time of the event. It is dispatched every 30 seconds.
    USD_VOLUME_24HR = 'chain_24hr_usd_volume'
