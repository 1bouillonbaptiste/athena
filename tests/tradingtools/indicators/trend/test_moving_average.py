import numpy as np
import pytest

from athena.tradingtools.indicators.trend.moving_average import (
    exponential_moving_average,
    simple_moving_average,
)


def test_simple_moving_average(input_data):
    assert np.allclose(
        simple_moving_average(input_data, window_size=1).values, input_data
    )
    assert np.allclose(
        simple_moving_average(input_data, window_size=2).values,
        [1.5, 1.5, 1.5, 1.5, 2.5, 2],
    )
    assert np.allclose(
        simple_moving_average(input_data, window_size=len(input_data)).values,
        np.repeat(np.mean(input_data), len(input_data)),
    )


def test_simple_moving_average_fails(input_data):
    with pytest.raises(ValueError):
        assert simple_moving_average(input_data, window_size=0).values


def test_exponential_moving_average(input_data):
    assert np.allclose(
        exponential_moving_average(input_data, window_size=1).values, input_data
    )
    assert np.allclose(
        exponential_moving_average(input_data, window_size=3).values,
        [1.25, 1.25, 1.25, 1.625, 2.3125, 1.65625],
    )
    assert np.allclose(
        exponential_moving_average(input_data, window_size=len(input_data)).values,
        np.repeat(1.62830963, len(input_data)),
    )


def test_exponential_moving_average_fails(input_data):
    with pytest.raises(ValueError):
        assert exponential_moving_average(input_data, window_size=0)
