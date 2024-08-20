import pytest
import datetime

from athena.types import Candle
import pandas as pd


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
    def generate_candles(timeframe):
        return [
            Candle(
                coin="BTC",
                currency="USDT",
                period=timeframe,
                open_time=datetime.datetime.fromisoformat("2020-01-01 00:00:00"),
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
                coin="BTC",
                currency="USDT",
                period=timeframe,
                open_time=datetime.datetime.fromisoformat("2020-01-01 04:00:00"),
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
