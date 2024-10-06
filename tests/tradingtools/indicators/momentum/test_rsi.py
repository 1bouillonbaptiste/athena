import numpy as np

from athena.tradingtools.indicators.momentum.rsi import rsi, stochastic_rsi


def test_rsi(input_data):
    rsi_line = rsi(input_data, window_size=3)

    assert np.allclose(
        rsi_line.values, [40.0, 40.0, 40.0, 68.42105263, 81.53846154, 36.30136986]
    )


def test_stochastic_rsi(input_data):
    stochastic_rsi_line, rsi_k, rsi_d = stochastic_rsi(
        input_data, window_size=2, smooth_k=1, smooth_d=1
    )

    assert np.allclose(stochastic_rsi_line.values, rsi_k.values)  # because smooth_k = 1
    assert np.allclose(stochastic_rsi_line.values, rsi_d.values)  # because smooth_d = 1

    stochastic_rsi_line, rsi_k, rsi_d = stochastic_rsi(
        input_data, window_size=2, smooth_k=2, smooth_d=3
    )

    assert not np.allclose(stochastic_rsi_line.values, rsi_k.values)
    assert not np.allclose(stochastic_rsi_line.values, rsi_d.values)
    assert not np.allclose(rsi_k.values, rsi_d.values)
