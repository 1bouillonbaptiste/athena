import numpy as np

from athena.tradingtools.indicators import macd


def test_macd(input_fluctuations):
    macd_diff_1 = macd(
        fluctuations=input_fluctuations, window_fast=2, window_slow=2, window_signal=2
    )
    macd_diff_2 = macd(
        fluctuations=input_fluctuations, window_fast=2, window_slow=3, window_signal=2
    )

    assert not np.allclose(macd_diff_1.values, macd_diff_2.values)
