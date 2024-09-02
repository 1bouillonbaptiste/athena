from athena.core.interfaces.fluctuations import (
    Fluctuations,
    get_high_time,
    get_low_time,
)


def test_get_high_time(generate_candles):
    candles = generate_candles(size=100, timeframe="1m")
    fluctuations = Fluctuations.from_candles(candles)
    highest_candle = fluctuations.get_candle(get_high_time(candles))
    for candle in candles:
        assert candle.high <= highest_candle.high


def test_get_low_time(generate_candles):
    candles = generate_candles(size=100, timeframe="1m")
    fluctuations = Fluctuations.from_candles(candles)
    lowest_candle = fluctuations.get_candle(get_low_time(candles))
    for candle in candles:
        assert candle.low >= lowest_candle.low
