from dataclasses import asdict

import pytest

from athena.core.market_entities import Candle


def assert_candles_equal(candle_a: Candle, candle_b: Candle):
    assert candle_a.coin == candle_b.coin
    assert candle_a.currency == candle_b.currency
    assert candle_a.period == candle_b.period

    a_dict = asdict(candle_a)
    b_dict = asdict(candle_b)
    for key in ["coin", "currency", "period"]:
        a_dict.pop(key)
        b_dict.pop(key)

    assert a_dict == pytest.approx(b_dict)
