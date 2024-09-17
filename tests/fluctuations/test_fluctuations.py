import datetime
import pytest

from athena.core.interfaces import Candle
from athena.core.types import Coin
from athena.core.interfaces.fluctuations import sanitize_candles


@pytest.fixture
def candles():
    other_params = {
        "open": 100,
        "close": 100,
        "high": 150,
        "low": 70,
        "coin": Coin.BTC,
        "currency": Coin.USDT,
        "period": "1h",
        "open_time": datetime.datetime(2024, 1, 1),
        "close_time": datetime.datetime(2024, 1, 2),
        "quote_volume": 150,
        "nb_trades": 100,
        "taker_volume": 50,
        "taker_quote_volume": 70,
    }

    def _candles(volumes: list[int]) -> list[Candle]:
        return [
            Candle(
                volume=volume,
                **other_params,
            )
            for volume in volumes
        ]

    return _candles


def test_sanitize_candles(candles):
    """Remove invalid candles."""

    sanitized_candles = sanitize_candles(candles(volumes=[50, 60, 0, 100, 0]))

    assert [candle.volume for candle in sanitized_candles] == [50, 60, 100]


def test_sanitize_candles_empty():
    sanitized_candles = sanitize_candles([])

    assert sanitized_candles == []
