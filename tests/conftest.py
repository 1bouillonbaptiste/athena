import pytest
import datetime


from athena.core.types import Period, Coin
from athena.core.interfaces import Candle, Fluctuations
import pandas as pd
import numpy as np


@pytest.fixture(autouse=True)
def patch_client(mocker):
    mocker.patch("athena.client.binance.get_credentials", return_value=(None, None))


@pytest.fixture
def generate_bars():
    def _generate_bars(
        size=1000,
        timeframe="1m",
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
    ):
        period = Period(timeframe=timeframe)

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

    return _generate_bars


@pytest.fixture
def generate_candles(generate_bars):
    def _generate_candles(
        size: int = 1000,
        coin="BTC",
        currency="USDT",
        timeframe="1m",
        from_date: datetime.datetime | None = None,
        to_date: datetime.datetime | None = None,
    ):
        return [
            Candle(
                coin=coin,
                currency=currency,
                period=timeframe,
                open_time=datetime.datetime.fromtimestamp(bar[0] / 1000.0),
                close_time=datetime.datetime.fromtimestamp(bar[0] / 1000.0)
                + Period(timeframe=timeframe).to_timedelta(),
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
            for bar in generate_bars(
                size=size, timeframe=timeframe, from_date=from_date, to_date=to_date
            )
        ]

    return _generate_candles


@pytest.fixture
def sample_bars():
    return [
        [
            datetime.datetime.fromisoformat("2020-01-01 00:00:00").timestamp() * 1000,
            "7195.2",
            "7245.",
            "7175.4",
            "7225.0",
            "2833.7",
            datetime.datetime.fromisoformat("2020-01-01 03:59:59").timestamp() * 1000,
            "20445895.8",
            32476,
            "1548.8",
            "11176594.4",
            "0",
        ],
        [
            datetime.datetime.fromisoformat("2020-01-01 04:00:00").timestamp() * 1000,
            "7225.0",
            "7236.2",
            "7199.1",
            "7209.8",
            "2061.3",
            datetime.datetime.fromisoformat("2020-01-01 07:59:59").timestamp() * 1000,
            "14890182.3",
            29991,
            "1049.7",
            "7582850.4",
            "0",
        ],
    ]


@pytest.fixture()
def sample_candles(sample_bars):
    def generate_candles(coin="BTC", currency="USDT", timeframe="4h"):
        return [
            Candle(
                coin=coin,
                currency=currency,
                period=timeframe,
                open_time=datetime.datetime.fromisoformat("2020-01-01 00:00:00"),
                high_time=datetime.datetime.fromisoformat("2020-01-01 03:35:00"),
                low_time=datetime.datetime.fromisoformat("2020-01-01 01:15:00"),
                close_time=datetime.datetime.fromisoformat("2020-01-01 00:00:00")
                + Period(timeframe=timeframe).to_timedelta(),
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
                period=timeframe,
                open_time=datetime.datetime.fromisoformat("2020-01-01 04:00:00"),
                high_time=datetime.datetime.fromisoformat("2020-01-01 07:35:00"),
                low_time=datetime.datetime.fromisoformat("2020-01-01 05:15:00"),
                close_time=datetime.datetime.fromisoformat("2020-01-01 04:00:00")
                + Period(timeframe=timeframe).to_timedelta(),
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

    return generate_candles


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
                Candle.model_validate(
                    {
                        "coin": coin,
                        "currency": currency,
                        "open_time": open_time,
                        "period": period.timeframe,
                        "close_time": open_time + period.to_timedelta(),
                        "high_time": (open_time + datetime.timedelta(hours=12))
                        if include_high_time
                        else None,
                        "low_time": (open_time + datetime.timedelta(hours=3))
                        if include_low_time
                        else None,
                        "open": open,
                        "high": high,
                        "low": low,
                        "close": close,
                        "volume": 100,
                        "quote_volume": (open + high) / 2 * 100,
                        "nb_trades": 100,
                        "taker_volume": 50,
                        "taker_quote_volume": (open + high) / 2 * 100 / 2,
                    }
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
