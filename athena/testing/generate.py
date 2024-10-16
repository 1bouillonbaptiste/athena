import datetime

import numpy as np

from athena.core.candle import convert_candles_to_period
from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import Candle
from athena.core.types import Period, Coin


def generate_bars(
    size: int = 1000,
    period: Period = Period(timeframe="1m"),
    from_date: datetime.datetime | None = None,
    to_date: datetime.datetime | None = None,
):
    """Mock Binance data fetch.

    Each bar is randomly generated, based on the previous bar with a starting close at 1000.

    Args:
        size: number of bars to generate
        period: the duration of each bar
        from_date: earliest open date
        to_date: latest close date

    Returns:
        randomly generated bars as a list
    """

    if from_date is None and to_date is None:
        initial_open_time = datetime.datetime.fromisoformat("2020-01-01 00:00:00")
        last_close_time = initial_open_time + period.to_timedelta() * size
    elif from_date is None and to_date is not None:
        last_close_time = to_date
        initial_open_time = to_date - period.to_timedelta() * size
    elif from_date is not None and to_date is None:
        initial_open_time = from_date
        last_close_time = from_date + period.to_timedelta() * size
    else:
        initial_open_time = from_date
        last_close_time = to_date

    size = int((last_close_time - initial_open_time) / period.to_timedelta())
    close_price = 1000
    bars = []
    for ii in range(size):
        open_price = close_price
        close_price = open_price * (1 + np.random.normal(scale=0.01))
        high_price = np.max([open_price, close_price]) * (
            1 + np.random.beta(a=2, b=5) / 100
        )
        low_price = np.min([open_price, close_price]) * (
            1 - np.random.beta(a=2, b=5) / 100
        )
        volume = (np.random.beta(a=2, b=2) / 2 + 0.25) * 1000
        buyer_volume = volume * (np.random.beta(a=2, b=2) / 2 + 0.25)
        bars.append(
            [
                (initial_open_time + ii * period.to_timedelta()).timestamp() * 1000,
                str(open_price),
                str(high_price),
                str(low_price),
                str(close_price),
                str(volume),
                (
                    initial_open_time
                    + (ii + 1) * period.to_timedelta()
                    - datetime.timedelta(milliseconds=90)
                ).timestamp()
                * 1000,
                str((open_price + close_price) / 2 * volume),
                np.random.randint(low=1000, high=10000),
                str(buyer_volume),
                str((open_price + close_price) / 2 * buyer_volume),
                "0",
            ]
        )
    return bars


def generate_candles(
    bars: list | None = None,
    size: int = 1000,
    coin: Coin = Coin.default_coin(),
    currency: Coin = Coin.default_currency(),
    period: Period = Period(timeframe="1m"),
    from_date: datetime.datetime | None = None,
    to_date: datetime.datetime | None = None,
):
    """Generate candles from random bars.

    Args:
        bars: generate candles from bars if available
        size: number of candles to generate
        coin: the coin to base the candles on
        currency: the currency to base the candles on
        period: the duration of each candle
        from_date: open date of the first candle
        to_date: close date of the last candle

    Returns:

    """
    if bars is None:
        bars = generate_bars(
            size=size, period=period, from_date=from_date, to_date=to_date
        )
    return [
        Candle(
            coin=coin,
            currency=currency,
            period=period,
            open_time=datetime.datetime.fromtimestamp(bar[0] / 1000.0),
            close_time=datetime.datetime.fromtimestamp(bar[0] / 1000.0)
            + period.to_timedelta(),
            open=float(bar[1]),
            high=float(bar[2]),
            low=float(bar[3]),
            close=float(bar[4]),
            volume=float(bar[5]),
            quote_volume=float(bar[7]),
            nb_trades=int(bar[8]),
            taker_volume=float(bar[9]),
            taker_quote_volume=float(bar[10]),
        )
        for bar in bars
    ]


def generate_fluctuations(
    size: int = 1000,
    period: Period = Period(timeframe="1m"),
    include_high_time: bool = False,
    include_low_time: bool = False,
    from_date: datetime.datetime | None = None,
    to_date: datetime.datetime | None = None,
):
    candles = generate_candles(
        size=int(size * period.to_timedelta() / Period(timeframe="1m").to_timedelta()),
        period=Period(timeframe="1m"),
        from_date=from_date,
        to_date=to_date,
    )
    if period.timeframe != "1m":
        candles = convert_candles_to_period(candles, target_period=period)
        for candle in candles:
            if not include_high_time:
                candle.high_time = None
            if not include_low_time:
                candle.low_time = None
    return Fluctuations.from_candles(candles)
