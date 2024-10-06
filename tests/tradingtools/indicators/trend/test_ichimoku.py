import numpy as np

from athena.tradingtools.indicators.trend.ichimoku import ichimoky


def test_ichimoku(input_high, input_low):
    """We assume ta is tested enough, we check that indicators produces different signals for different parameters."""
    span_a_left, span_b_left, conversion_line_left, base_line_left = ichimoky(
        highs=input_high, lows=input_low, window_a=1, window_b=1, window_c=1
    )

    span_a_right, span_b_right, conversion_line_right, base_line_right = ichimoky(
        highs=input_high, lows=input_low, window_a=2, window_b=3, window_c=2
    )

    assert not np.allclose(span_a_left, span_a_right)
    assert not np.allclose(span_b_left, span_b_right)
    assert not np.allclose(conversion_line_left, conversion_line_right)
    assert not np.allclose(base_line_left, base_line_right)
