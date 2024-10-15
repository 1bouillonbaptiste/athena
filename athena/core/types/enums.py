import enum


class Signal(enum.Enum):
    BUY = "buy"
    SELL = "sell"
    WAIT = "wait"


class Side(enum.Enum):
    LONG = "long"
    SHORT = "short"


class Coin(enum.Enum):
    COIN = "COIN"  # when the base coin is not known, we still want to process it
    BTC = "BTC"
    ETH = "ETH"

    CURRENCY = "CURRENCY"  # when the quote is not known, we still want to process it
    USDT = "USDT"
    EUR = "EUR"

    @classmethod
    def default_coin(cls):
        return cls.COIN

    @classmethod
    def default_currency(cls):
        return cls.CURRENCY
