from datetime import datetime

from athena.client.binance import BinanceClient
from athena.client.fetch import fetch_historical_data
from athena.core.fluctuations import Fluctuations
from athena.core.types import Period, Coin
from athena.testing.generate import generate_bars, generate_candles


def test_fetch_historical_data(mocker, sample_candles):
    generated_bars = generate_bars(size=10)
    mocker.patch(
        "athena.client.binance.BinanceClient.get_historical_klines",
        return_value=generated_bars,
    )

    assert (
        fetch_historical_data(
            client=BinanceClient(),
            coin="BTC",
            currency="USDT",
            period=Period(timeframe="1m"),
            start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
            end_date=datetime.strptime("2020-01-02", "%Y-%m-%d"),
        ).model_dump()
        == Fluctuations.from_candles(
            generate_candles(bars=generated_bars, coin=Coin.BTC, currency=Coin.USDT)
        ).model_dump()
    )
