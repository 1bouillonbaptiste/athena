from athena.core.interfaces.fluctuations import (
    merge_candles,
    convert_candles_to_period,
)
from athena.core.types import Period

import datetime

import pytest


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

    # FIXME : converting from 1m to 1m, last candle is not taken, so add -1
    assert len(merged_candles) == len(candles) - 1


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
