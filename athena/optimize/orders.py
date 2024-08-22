import datetime

from athena.types import Side, Coin
from pydantic import BaseModel

FEES_PCT = 0.001


class Position(BaseModel):
    """A position is an opened long or short that is waiting an exit signal. When a Position is closed, it usually leads
    to a Trade.

    Attributes:
        strategy_name: the nickname of the strategy used to open the position
        coin: the coin that have been bought
        currency: the currency use to buy the coin
        open_date: the date when the position was opened, usually the open_date of a candle
        open_price: coin's price when the position was opened
        amount: coin's amount that have been bought
        open_fees: cost of opening a new position, fees are taken before calculating coin amount
        initial_investment: the initial amount of currency the trader invested
        stop_loss: stop your loss, close the position if the price reach this level
        take_profit: take your profit, close the position if the price reach this level
        side: weather the position is a long or a short
    """

    strategy_name: str = ""
    coin: Coin
    currency: Coin

    open_date: datetime.datetime
    open_price: float
    amount: float
    open_fees: float
    initial_investment: float

    stop_loss: float | None
    take_profit: float | None
    side: Side

    @classmethod
    def from_money_to_invest(
        cls,
        strategy_name: str,
        coin: Coin,
        currency: Coin,
        open_date: datetime.datetime,
        open_price: float,
        money_to_invest: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
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


class Trade(Position):
    """A trade is a closed Position.

    Attributes:
        ...
        close_date: the date when a position was closed
        close_price: the closing price of the position
        close_fees: fees from selling the position
        total_fees: sum of open and close fees
        total_profit: remaining money when we sell the position and remove fees
        is_win: if we made money on this trade or not
        trade_duration: position total lifetime
    """

    close_date: datetime.datetime
    close_price: float
    close_fees: float

    total_fees: float
    total_profit: float
    is_win: bool
    trade_duration: datetime.timedelta

    @classmethod
    def from_position(
        cls, position: Position, close_date: datetime.datetime, close_price: float
    ):
        close_fees = close_price * position.amount * FEES_PCT
        total_fees = close_fees + position.open_fees
        total_profit = (
            (position.amount * close_price) - position.initial_investment - total_fees
        )
        trade_duration = close_date - position.open_date
        return cls(
            close_fees=close_fees,
            total_fees=total_fees,
            close_date=close_date,
            close_price=close_price,
            total_profit=total_profit,
            is_win=total_profit > 0,
            trade_duration=trade_duration,
            **position.model_dump(),
        )


class Portfolio(BaseModel):
    """A mapping of an account's available coins.

    Attributes:
        assets: a dictionary where each key is a coin and the associated value is the available amount of that coin
    """

    assets: dict[Coin, float]

    def get_available(self, coin: Coin) -> float:
        return self.assets.get(coin, 0)
