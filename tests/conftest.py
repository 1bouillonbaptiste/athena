import pytest
import datetime

from athena.types import Candle


@pytest.fixture
def sample_bars():
    return [
        [
            1577836800000,
            "7195.2",
            "7245.",
            "7175.4",
            "7225.0",
            "2833.7",
            1577851199999,
            "20445895.8",
            32476,
            "1548.8",
            "11176594.4",
            "0",
        ],
        [
            1577851200000,
            "7225.0",
            "7236.2",
            "7199.1",
            "7209.8",
            "2061.3",
            1577865599999,
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
                open_time=datetime.datetime.fromtimestamp(row[0] / 1000.0),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                quote_volume=float(row[7]),
                nb_trades=int(row[8]),
                taker_volume=float(row[9]),
                taker_quote_volume=float(row[10]),
            )
            for row in sample_bars
        ]

    return generate_candles
