import enum


class Signal(enum.Enum):
    BUY = "buy"
    SELL = "sell"
    WAIT = "wait"


class Side(enum.Enum):
    LONG = "long"
    SHORT = "short"


class Coin(enum.Enum):
    BTC = "BTC"
    USDT = "USDT"
