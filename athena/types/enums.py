import enum


class Signal(enum.Enum):
    BUY: str = "buy"
    SELL: str = "sell"
    WAIT: str = "wait"


class Side(enum.Enum):
    LONG = "long"
    SHORT = "short"
