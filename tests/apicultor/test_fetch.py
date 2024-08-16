from athena.apicultor.fetch import fetch_historical_data
from athena.apicultor.client import (
    BinanceClient,
)
from athena.apicultor.types import Candle, Period

from datetime import datetime
import pytest


@pytest.fixture
def bars():
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


def test_fetch_historical_data(mocker, bars):
    mocker.patch(
        "athena.apicultor.client.BinanceClient.get_historical_klines",
        return_value=bars
        + [
            [
                1577865600000,
                "7225.0",
                "7236.2",
                "7199.1",
                "7209.8",
                "2061.3",
                1577872899999,  # + 2h, should be filtered out
                "14890182.3",
                29991,
                "1049.7",
                "7582850.4",
                "0",
            ],
        ],
    )
    period = Period(timeframe="4h")
    assert fetch_historical_data(
        client=BinanceClient(),
        coin="BTC",
        currency="USDT",
        period=period,
        start_date="2020-01-01",
        end_date="2020-01-02",
    ) == [
        Candle(
            coin="BTC",
            currency="USDT",
            period=period,
            open_time=datetime.fromtimestamp(row[0] / 1000.0),
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
        for row in bars
    ]
