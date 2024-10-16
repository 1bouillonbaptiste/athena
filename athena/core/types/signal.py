from dataclasses import dataclass
from typing import Literal


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
