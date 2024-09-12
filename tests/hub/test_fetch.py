from datetime import datetime

from athena.hub.fetch import fetch_historical_data
from athena.hub.client import (
    BinanceClient,
)
from athena.core.types import Period
from athena.core.interfaces import Fluctuations


def test_fetch_historical_data(mocker, sample_bars, sample_candles):
    mocker.patch(
        "athena.hub.client.BinanceClient.get_historical_klines",
        return_value=sample_bars
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
    candles = sample_candles(timeframe=period.timeframe)
    for candle in candles:
        candle.high_time = None
        candle.low_time = None
    assert (
        fetch_historical_data(
            client=BinanceClient(),
            coin="BTC",
            currency="USDT",
            period=period,
            start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
            end_date=datetime.strptime("2020-01-02", "%Y-%m-%d"),
        ).model_dump()
        == Fluctuations.from_candles(candles).model_dump()
    )
