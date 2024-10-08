import pytest
import datetime

from athena.core.interfaces import Fluctuations, Candle
from athena.core.types import Coin, Period


@pytest.fixture
def input_fluctuations():
    period = Period(timeframe="1h")
    return Fluctuations.from_candles(
        candles=[
            Candle(
                coin=Coin.default_coin(),
                currency=Coin.default_currency(),
                open_time=open_time,
                period=period.timeframe,
                close_time=open_time + period.to_timedelta(),
                high_time=(open_time + datetime.timedelta(minutes=45)),
                low_time=(open_time + datetime.timedelta(minutes=15)),
                open=open,
                high=high,
                low=low,
                close=close,
                volume=100,
                quote_volume=(open + high) / 2 * 100,
                nb_trades=100,
                taker_volume=50,
                taker_quote_volume=(open + high) / 2 * 100 / 2,
            )
            for open_time, open, high, low, close in zip(
                [
                    datetime.datetime(2024, 8, 19) + ii * period.to_timedelta()
                    for ii in range(7)
                ],
                [50, 100, 200, 100, 200, 300],
                [150, 250, 150, 250, 350, 150],
                [50, 150, 50, 150, 250, 50],
                [100, 200, 100, 200, 300, 100],
            )
        ]
    )
