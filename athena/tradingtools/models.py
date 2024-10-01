import datetime
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from athena.core.interfaces import Candle
from athena.core.types import Coin, Side

FEES_PCT = 0.001


@dataclass
class ExitSignal:
    """How a Position needs to be closed.

    The signal can be:
    - take profit at high time
    - take profit at undefined time (take close time)
    - stop loss at low time
    - stop loss at undefined time (take close time)
    - close at close time
    """

    price_signal: Literal["take_profit", "stop_loss", "close"]
    date_signal: Literal["high", "low", "close"]

    def to_price_date(
        self, position: "Position", candle: Candle
    ) -> tuple[float, datetime.datetime]:
        """Convert the signal to actual price and date."""
        match self.price_signal:
            case "take_profit":
                price = position.take_profit
            case "stop_loss":
                price = position.stop_loss
            case "close":
                price = candle.close
        match self.date_signal:
            case "high":
                date = candle.high_time
            case "low":
                date = candle.low_time
            case "close":
                date = candle.close_time

        return price, date


class Position(BaseModel):
    """A position is the expression of a market commitment, or exposure, held by a trader.

    When the position is closed, it becomes a trade. Profit, loss or other metrics can then be calculated.

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

    is_closed: bool = False

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

    def close(self, close_date: datetime.datetime, close_price: float) -> "Trade":
        """Sell the traded amount.

        Args:
            close_date: time when the position is closed
            close_price: price when the position is closed

        Returns:
            closed position as a new trade

        Raises:
            ValueError: if the position is already closed
        """

        if self.is_closed:
            raise ValueError("Position il already closed.")

        self.is_closed = True

        close_fees = close_price * self.amount * FEES_PCT
        total_fees = close_fees + self.open_fees
        total_profit = (
            (self.amount * close_price) - self.initial_investment - total_fees
        )
        profit_pct = (
            (total_profit / self.initial_investment)
            if self.initial_investment  # to avoid 0 division, should never happen in real life
            else 0
        )

        return Trade(
            strategy_name=self.strategy_name,
            coin=self.coin,
            currency=self.currency,
            amount=self.amount,
            side=self.side,
            open_date=self.open_date,
            open_price=self.open_price,
            initial_investment=self.initial_investment,
            open_fees=self.open_fees,
            stop_loss=self.stop_loss,
            take_profit=self.take_profit,
            close_date=close_date,
            close_price=close_price,
            close_fees=close_fees,
            total_fees=total_fees,
            total_profit=total_profit,
            profit_pct=profit_pct,
            is_win=total_profit > 0,
            trade_duration=close_date - self.open_date,
        )

    def get_exit_signal(self, candle: Candle) -> ExitSignal | None:
        """Check if a candle reaches position's take profit or stop loss.

        Args:
            candle: a market candle

        Returns:
            close_price: the sell price of the position or None if position remains open
            close_date: the close date of the position or None if position remains open
        """

        price_reach_tp = candle.high >= self.take_profit
        price_reach_sl = candle.low <= self.stop_loss

        if (
            price_reach_tp and price_reach_sl
        ):  # candle's price range is very wide, check which bound was reached first
            if (candle.high_time is not None) and (candle.low_time is not None):
                if candle.high_time < candle.low_time:  # price reached high before low
                    return ExitSignal(price_signal="take_profit", date_signal="high")
                else:  # price reached low before high
                    return ExitSignal(price_signal="stop_loss", date_signal="low")
            else:  # we don't have granularity, assume close price is close enough to real sell price
                return ExitSignal(price_signal="close", date_signal="close")
        elif price_reach_tp:
            return ExitSignal(
                price_signal="take_profit",
                date_signal="high" if candle.high_time else "close",
            )
        elif price_reach_sl:
            return ExitSignal(
                price_signal="stop_loss",
                date_signal="low" if candle.low_time else "close",
            )

        return None


@dataclass
class Trade:
    """A Trade is a closed Position.

    Can only be instantiated with Position.close()

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

    strategy_name: str
    coin: Coin
    currency: Coin
    amount: float
    side: Side

    open_date: datetime.datetime
    open_price: float
    initial_investment: float
    open_fees: float
    stop_loss: float
    take_profit: float

    close_date: datetime.datetime
    close_price: float
    close_fees: float

    total_fees: float
    total_profit: float
    profit_pct: float
    is_win: bool
    trade_duration: datetime.timedelta


class Portfolio(BaseModel):
    """A mapping of an account's available coins.

    Attributes:
        assets: a dictionary where each key is a coin and the associated value is the available amount of that coin
    """

    assets: dict[Coin, float]

    def get_available(self, coin: Coin) -> float:
        return self.assets.get(coin, 0)

    @classmethod
    def default(cls, currency: Coin | None = None):
        """Initialize portfolio with a coin or the default one.."""
        return cls.model_validate(
            {"assets": {currency or Coin.default_currency(): 100}}
        )

    def update_from_position(self, position: Position) -> None:
        """Change coin and currency amounts after a position is opened."""
        self.update_coin_amount(
            coin=position.currency, amount_to_add=-position.initial_investment
        )
        self.update_coin_amount(coin=position.coin, amount_to_add=position.amount)

    def update_from_trade(self, trade: Trade) -> None:
        """Change coin and currency amounts after a position is closed."""
        self.update_coin_amount(
            coin=trade.currency,
            amount_to_add=trade.initial_investment + trade.total_profit,
        )
        self.update_coin_amount(coin=trade.coin, amount_to_add=-trade.amount)

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
