import datetime
import pytest

from athena.core.interfaces import Candle
from athena.core.types import Coin
from athena.core.interfaces.fluctuations import sanitize_candles


@pytest.fixture
def candle():
    return [
        Candle(
            volume=0,
            open=100,
            close=100,
            high=150,
            low=70,
            coin=Coin.BTC,
            currency=Coin.USDT,
            period="1h",
            open_time=datetime.datetime(2024, 1, 1),
            close_time=datetime.datetime(2024, 1, 2),
            quote_volume=150,
            nb_trades=100,
            taker_volume=50,
            taker_quote_volume=70,
        ),
        # volume at 100
        Candle(
            volume=100,
            open=100,
            close=100,
            high=150,
            low=70,
            coin=Coin.BTC,
            currency=Coin.USDT,
            period="1h",
            open_time=datetime.datetime(2024, 1, 1),
            close_time=datetime.datetime(2024, 1, 2),
            quote_volume=150,
            nb_trades=100,
            taker_volume=50,
            taker_quote_volume=70,
        ),
    ]


def test_sanitize_candles(candle):
    """all candle's volume not > 0."""

    sanitized_candles = sanitize_candles(candle)

    assert len(sanitized_candles) == 1
    assert sanitized_candles[0].volume == 100
