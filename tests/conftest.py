import datetime

import pandas as pd
import pytest

from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import Candle, Position
from athena.core.types import Coin, Period


@pytest.fixture(autouse=True)
def patch_client(mocker):
    mocker.patch("athena.client.binance.get_credentials", return_value=(None, None))


@pytest.fixture()
def sample_candles():
    def _sample_candles(
        coin=Coin.BTC, currency=Coin.USDT, period=Period(timeframe="4h")
    ):
        return [
            Candle(
                coin=coin,
                currency=currency,
                period=period,
                open_time=datetime.datetime.fromisoformat("2020-01-01 00:00:00"),
                high_time=datetime.datetime.fromisoformat("2020-01-01 03:35:00"),
                low_time=datetime.datetime.fromisoformat("2020-01-01 01:15:00"),
                close_time=datetime.datetime.fromisoformat("2020-01-01 00:00:00")
                + period.to_timedelta(),
                open=7195.2,
                high=7245.0,
                low=7175.4,
                close=7225.0,
                volume=2833.7,
                quote_volume=20445895.8,
                nb_trades=32476,
                taker_volume=1548.8,
                taker_quote_volume=11176594.4,
            ),
            Candle(
                coin=coin,
                currency=currency,
                period=period,
                open_time=datetime.datetime.fromisoformat("2020-01-01 04:00:00"),
                high_time=datetime.datetime.fromisoformat("2020-01-01 07:35:00"),
                low_time=datetime.datetime.fromisoformat("2020-01-01 05:15:00"),
                close_time=datetime.datetime.fromisoformat("2020-01-01 04:00:00")
                + period.to_timedelta(),
                open=7225.0,
                high=7236.2,
                low=7199.1,
                close=7209.8,
                volume=2061.3,
                quote_volume=14890182.3,
                nb_trades=29991,
                taker_volume=1049.7,
                taker_quote_volume=7582850.4,
            ),
        ]

    return _sample_candles


@pytest.fixture()
def sample_fluctuations():
    def generate_fluctuations(coin="BTC", currency="USDT", timeframe="4h"):
        return pd.DataFrame(
            {
                "coin": [coin] * 2,
                "currency": [currency] * 2,
                "period": [timeframe] * 2,
                "open_time": [
                    datetime.datetime.fromisoformat("2020-01-01 00:00:00"),
                    datetime.datetime.fromisoformat("2020-01-01 04:00:00"),
                ],
                "high_time": [
                    datetime.datetime.fromisoformat("2020-01-01 03:35:00"),
                    datetime.datetime.fromisoformat("2020-01-01 07:35:00"),
                ],
                "low_time": [
                    datetime.datetime.fromisoformat("2020-01-01 01:15:00"),
                    datetime.datetime.fromisoformat("2020-01-01 05:15:00"),
                ],
                "close_time": [
                    datetime.datetime.fromisoformat("2020-01-01 04:00:00"),
                    datetime.datetime.fromisoformat("2020-01-01 08:00:00"),
                ],
                "open": [7195.2, 7225.0],
                "high": [7245.0, 7236.2],
                "low": [7175.4, 7199.1],
                "close": [7225.0, 7209.8],
                "volume": [2833.7, 2061.3],
                "quote_volume": [20445895.8, 14890182.3],
                "nb_trades": [32476, 29991],
                "taker_volume": [1548.8, 1049.7],
                "taker_quote_volume": [11176594.4, 7582850.4],
            }
        )

    return generate_fluctuations


@pytest.fixture
def fluctuations():
    def _fluctuations(
        coin=Coin.BTC,
        currency=Coin.USDT,
        timeframe="4h",
        include_high_time: bool = True,
        include_low_time: bool = True,
    ) -> Fluctuations:
        period = Period(timeframe=timeframe)
        return Fluctuations.from_candles(
            candles=[
                Candle(
                    coin=coin,
                    currency=currency,
                    open_time=open_time,
                    period=period.timeframe,
                    close_time=open_time + period.to_timedelta(),
                    high_time=(open_time + datetime.timedelta(hours=12))
                    if include_high_time
                    else None,
                    low_time=(open_time + datetime.timedelta(hours=3))
                    if include_low_time
                    else None,
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
                    [50, 100, 150, 200, 250, 300, 350],
                    [125, 175, 225, 275, 325, 375, 425],
                    [40, 90, 140, 190, 240, 290, 340],
                    [100, 150, 200, 250, 300, 350, 400],
                )
            ]
        )

    return _fluctuations


@pytest.fixture
def sample_trades():
    """Returns 3 closed positions.

    trade 1 : sell at higher price, it's a win
    trade 2 : sell at same price, it's a loss due to fees
    trade 3 : sell at lower price, it's a loss

    Overall we should make money

    Returns:
        trades as list of closed positions
    """
    trade1 = Position.open(
        open_date=datetime.datetime(2024, 8, 20),
        open_price=100,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 8, 21), close_price=120)

    trade2 = Position.open(
        open_date=datetime.datetime(2024, 8, 22),
        open_price=130,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 8, 23), close_price=130)

    trade3 = Position.open(
        open_date=datetime.datetime(2024, 8, 24),
        open_price=130,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 8, 25), close_price=120)
    return [trade1, trade2, trade3]
