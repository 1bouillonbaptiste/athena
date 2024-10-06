import numpy as np

from athena.tradingtools.indicators.trend.ichimoku import ichimoku


def test_ichimoku(input_high, input_low):
    """We assume ta is tested enough, we check that indicators produces different signals for different parameters."""
    span_a_left, span_b_left, conversion_line_left, base_line_left = ichimoku(
        highs=input_high, lows=input_low, window_a=1, window_b=1, window_c=1
    )

    span_a_right, span_b_right, conversion_line_right, base_line_right = ichimoku(
        highs=input_high, lows=input_low, window_a=2, window_b=3, window_c=2
    )

    assert not np.allclose(span_a_left.values, span_a_right.values)
    assert not np.allclose(span_b_left.values, span_b_right.values)
    assert not np.allclose(conversion_line_left.values, conversion_line_right.values)
    assert not np.allclose(base_line_left.values, base_line_right.values)
