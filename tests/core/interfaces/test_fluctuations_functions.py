import datetime

import pytest

from athena.core.interfaces import Candle
from athena.core.interfaces.fluctuations import (
    convert_candles_to_period,
    load_candles_from_file,
    merge_candles,
    sanitize_candles,
)
from athena.core.types import Coin, Period


def test_load_candles_from_file(sample_candles, sample_fluctuations, tmp_path):
    sample_fluctuations().to_csv(tmp_path / "fluctuations.csv", index=False)
    assert load_candles_from_file(tmp_path / "fluctuations.csv") == sample_candles()


def test_merge_candles(generate_candles):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 1, hour=1)
    candles = generate_candles(timeframe="1m", from_date=from_date, to_date=to_date)

    merged_candle = merge_candles(candles)

    for candle in candles:
        assert candle.open_time >= merged_candle.open_time
        assert candle.close_time <= merged_candle.close_time
        assert candle.high <= merged_candle.high
        assert candle.low >= merged_candle.low

    assert (merged_candle.close_time - merged_candle.open_time) == (to_date - from_date)


def test_convert_candles_to_same_period(generate_candles):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 2)

    candles = generate_candles(timeframe="1m", from_date=from_date, to_date=to_date)
    target_period = Period(timeframe="1m")

    merged_candles = convert_candles_to_period(candles, target_period)

    assert len(merged_candles) == len(candles)


def test_convert_candles_to_period(generate_candles):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 2)

    candles = generate_candles(timeframe="1m", from_date=from_date, to_date=to_date)
    target_period = Period(timeframe="4h")

    merged_candles = convert_candles_to_period(candles, target_period)

    assert len(merged_candles) == 6


def test_convert_candles_to_period_missing_data(generate_candles, caplog):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 2, hour=3)

    candles = generate_candles(timeframe="1m", from_date=from_date, to_date=to_date)
    target_period = Period(timeframe="4h")

    merged_candles = convert_candles_to_period(candles, target_period)

    assert len(merged_candles) == 6
    assert "Last candle could not be closed, won't be kept." in caplog.text


def test_convert_candles_to_period_wrong_timeframe(generate_candles):
    from_date = datetime.datetime(2020, 1, 1)
    to_date = datetime.datetime(2020, 1, 2, hour=3)

    candles = generate_candles(timeframe="4m", from_date=from_date, to_date=to_date)
    target_period = Period(timeframe="1m")

    with pytest.raises(ValueError, match="Cannot convert candles to lower timeframe"):
        convert_candles_to_period(candles, target_period)


@pytest.fixture
def raw_candles():
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

    def _raw_candles(volumes: list[int]) -> list[Candle]:
        return [
            Candle(
                volume=volume,
                **other_params,
            )
            for volume in volumes
        ]

    return _raw_candles


def test_sanitize_candles(generate_candles):
    """Remove invalid candles."""

    candles = generate_candles(size=5)
    candles[2].volume = 0
    candles[4].volume = 0
    sanitized_candles = sanitize_candles(candles)

    assert len(sanitized_candles) == 3
    assert all([candle.volume != 0 for candle in sanitized_candles])


def test_sanitize_candles_empty():
    sanitized_candles = sanitize_candles([])

    assert sanitized_candles == []
