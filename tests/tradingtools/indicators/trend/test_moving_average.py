import numpy as np
import pytest

from athena.tradingtools.indicators.trend.moving_average import (
    exponential_moving_average,
    simple_moving_average,
)


def test_simple_moving_average(input_fluctuations):
    assert np.allclose(
        simple_moving_average(input_fluctuations, window_size=1).values,
        input_fluctuations.get_series("close"),
    )
    assert np.allclose(
        simple_moving_average(input_fluctuations, window_size=2).values,
        [150, 150, 150, 150, 250, 200],
    )
    assert np.allclose(
        simple_moving_average(
            input_fluctuations, window_size=len(input_fluctuations)
        ).values,
        np.repeat(
            np.mean(input_fluctuations.get_series("close").values),
            len(input_fluctuations),
        ),
    )


def test_simple_moving_average_fails(input_fluctuations):
    with pytest.raises(ValueError):
        assert simple_moving_average(input_fluctuations, window_size=0).values


def test_exponential_moving_average(input_fluctuations):
    assert np.allclose(
        exponential_moving_average(input_fluctuations, window_size=1).values,
        input_fluctuations.get_series("close"),
    )
    assert np.allclose(
        exponential_moving_average(input_fluctuations, window_size=3).values,
        [125, 125, 125, 162.5, 231.25, 165.625],
    )
    assert np.allclose(
        exponential_moving_average(
            input_fluctuations, window_size=len(input_fluctuations)
        ).values,
        np.repeat(162.830963, len(input_fluctuations)),
    )


def test_exponential_moving_average_fails(input_fluctuations):
    with pytest.raises(ValueError):
        assert exponential_moving_average(input_fluctuations, window_size=0)
