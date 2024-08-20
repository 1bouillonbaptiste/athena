import datetime

from athena.types import Side
from pydantic import BaseModel


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
        stop_loss: stop your loss, close the position if the price reach this level
        take_profit: take your profit, close the position if the price reach this level
        side: weather the position is a long or a short
    """

    strategy_name: str = ""
    coin: str
    currency: str

    open_date: datetime.datetime
    open_price: float
    amount: float

    stop_loss: float
    take_profit: float
    side: Side


class Trade(Position):
    """A trade is a closed Position.

    Attributes:
        ...
        close_date: the date when a position was closed
        close_price: the closing price of the position
    """

    close_date: datetime.datetime
    close_price: float

    @classmethod
    def from_position(
        cls, position: Position, close_date: datetime.datetime, close_price: float
    ):
        return cls(
            close_date=close_date, close_price=close_price, **position.model_dump()
        )
