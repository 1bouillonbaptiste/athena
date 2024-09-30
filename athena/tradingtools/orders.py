import datetime

from pydantic import BaseModel

from athena.core.interfaces import Candle
from athena.core.types import Coin, Side

FEES_PCT = 0.001


class Position(BaseModel):
    """A position is the expression of a market commitment, or exposure, held by a trader. When the position is closed,
    it becomes a trade, profit, loss or other metrics can then be calculated.

    A position is defined by its size (amount of coin) and direction ('LONG' or 'SHORT').
    - 'LONG' position means that you are buying an asset (or speculating that the asset will increase in value).
    - 'SHORT' position aims to make a profit when an asset’s price decreases (not implemented yet).

    Attributes:
        strategy_name: the nickname of the strategy used to open the position
        coin: the coin that have been bought
        currency: the currency used to buy the coin
        amount: coin's amount that have been bought
        side: weather the position is a 'LONG' or a 'SHORT'

        open_date: the date when the position was open, usually the open_date of a candle
        open_price: coin's price when the position was open
        initial_investment: the initial amount of currency the trader invested
        open_fees: cost of opening the position, fees are being taken before calculating coin amount
        stop_loss: stop your loss if price drops too low (close the position)
        take_profit: take your profits if price reaches your target (close the position)

        close_date: the date when a position was closed, could be any time
        close_price: coin's price when the position was closed
        close_fees: fees from selling the position

        total_fees: sum of open and close fees
        total_profit: remaining money when we compare initial investment, return and fees
        profit_pct: trade's return
        is_win: if we made money on this trade or not
        trade_duration: position total lifetime
    """

    strategy_name: str = ""
    coin: Coin = Coin.default_coin()
    currency: Coin = Coin.default_currency()
    amount: float
    side: Side

    open_date: datetime.datetime
    open_price: float
    initial_investment: float
    open_fees: float
    stop_loss: float = 0
    take_profit: float = float("inf")

    # these parameters are None until the position is closed

    close_date: datetime.datetime | None = None
    close_price: float | None = None
    close_fees: float | None = None

    total_fees: float | None = None
    total_profit: float | None = None
    profit_pct: float | None = None
    is_win: bool | None = None
    trade_duration: datetime.timedelta | None = None

    @property
    def is_closed(self) -> bool:
        """Check if the position is closed or still opened."""
        return self.close_date is not None

    @classmethod
    def open(
        cls,
        open_date: datetime.datetime,
        open_price: float,
        money_to_invest: float,
        strategy_name: str = "strategy",
        coin: Coin = Coin.default_coin(),
        currency: Coin = Coin.default_currency(),
        stop_loss: float = 0,
        take_profit: float = float("inf"),
        side: Side = Side.LONG,
    ):
        """Invest some money on a coin, compute associated fees and real amount bought."""
        open_fees = money_to_invest * FEES_PCT
        amount = (money_to_invest - open_fees) / open_price
        return cls(
            strategy_name=strategy_name,
            coin=coin,
            currency=currency,
            open_date=open_date,
            open_price=open_price,
            amount=amount,
            open_fees=open_fees,
            initial_investment=money_to_invest,
            stop_loss=stop_loss,
            take_profit=take_profit,
            side=side,
        )

    def close(self, close_date: datetime.datetime, close_price: float):
        """Sell the traded amount.

        Args:
            close_date: time when the position is closed
            close_price: price when the position is closed
        """
        self.close_date = close_date
        self.close_price = close_price

        self.close_fees = self.close_price * self.amount * FEES_PCT
        self.total_fees = self.close_fees + self.open_fees
        self.total_profit = (
            (self.amount * self.close_price) - self.initial_investment - self.total_fees
        )
        self.profit_pct = (
            (self.total_profit / self.initial_investment)
            if self.initial_investment
            else 0
        )
        self.trade_duration = self.close_date - self.open_date

        self.is_win = self.total_profit > 0
        self.trade_duration = self.close_date - self.open_date

    def check_exit_signals(
        self, candle: Candle
    ) -> tuple[float | None, datetime.datetime | None]:
        """Check if a candle reaches position's take profit or stop loss.

        Args:
            candle: a market candle

        Returns:
            close_price: the sell price of the position or None if position remains open
            close_date: the close date of the position or None if position remains open
        """

        price_reach_tp = candle.high > self.take_profit
        price_reach_sl = candle.low < self.stop_loss

        if (
            price_reach_tp and price_reach_sl
        ):  # candle's price range is very wide, check which bound was reached first
            if (candle.high_time is not None) and (candle.low_time is not None):
                if candle.high_time < candle.low_time:  # price reached high before low
                    close_price = self.take_profit
                    close_date = candle.high_time
                else:  # price reached low before high
                    close_price = self.stop_loss
                    close_date = candle.low_time
            else:  # we don't have granularity, assume close price is close enough to real sell price
                close_price = candle.close
                close_date = candle.close_time
        elif price_reach_tp:
            close_price = self.take_profit
            close_date = candle.high_time or candle.close_time
        elif price_reach_sl:
            close_price = self.stop_loss
            close_date = candle.low_time or candle.close_time
        else:  # we don't close the position
            close_price = None
            close_date = None

        return close_price, close_date


class Portfolio(BaseModel):
    """A mapping of an account's available coins.

    Attributes:
        assets: a dictionary where each key is a coin and the associated value is the available amount of that coin
    """

    assets: dict[Coin, float]

    def get_available(self, coin: Coin) -> float:
        return self.assets.get(coin, 0)

    @classmethod
    def default(cls):
        return cls.model_validate({"assets": {Coin.default_currency(): 100}})

    def update_coin_amount(self, coin: Coin, amount_to_add: float) -> None:
        """Update coin's available amount in portfolio.

        Args:
            coin: the coin name to update
            amount_to_add: the coin's amount to be added, could be negative

        Raises:
            ValueError: if coin's amount falls below zero
        """
        updated_amount = self.get_available(coin) + amount_to_add
        if updated_amount < 0:
            raise ValueError(f"Trying to set a negative amount of `{coin}`")
        self.assets[coin] = updated_amount
