from pydantic import BaseModel, Field
import pytest

from athena.configs import CCPVConfig
from athena.core.candle import convert_candles_to_period
from athena.core.fluctuations import Fluctuations
from athena.core.types import Signal, Period

from athena.performance.optimize.optimizer import Optimizer
from athena.performance.optimize.split import create_ccpv_splits
from athena.testing.generate import generate_candles
from athena.tradingtools import Strategy


pytestmark = [
    # Optuna optimization algorithm sometimes fails to iter
    pytest.mark.filterwarnings("ignore::RuntimeWarning:numpy._core._methods"),
]


class NewStrategyModel(BaseModel):
    """Parameters' configuration model."""

    parameter_a: int = Field(ge=0, le=10, default=0)
    parameter_b: int = Field(gt=10, lt=20, default=15)


class NewStrategy(Strategy):
    """A new strategy."""

    def __init__(
        self,
        config: NewStrategyModel,
    ):
        super().__init__()
        self.config = config

    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Buy if hour is even, sell if hour is odd."""
        signals = []
        for open_time in fluctuations.get_series("open_time"):
            if open_time.hour % 2 == 0:
                signals.append(Signal.BUY)
            else:
                signals.append(Signal.SELL)
        return signals


def test_optimizer(trading_session):
    optimizer = Optimizer(
        trading_session=trading_session(),
        strategy=NewStrategy(config=NewStrategyModel()),
        n_trials=2,
    )
    split_results = optimizer.optimize(
        train_fluctuations=Fluctuations.from_candles(
            convert_candles_to_period(
                generate_candles(size=1000, period=Period(timeframe="1m")),
                target_period=Period(timeframe="1h"),
            ),
        ),
        val_fluctuations=Fluctuations.from_candles(
            convert_candles_to_period(
                generate_candles(size=1000, period=Period(timeframe="1m")),
                target_period=Period(timeframe="1h"),
            ),
        ),
    )

    #
    assert split_results.parameters.keys() == {"parameter_a", "parameter_b"}

    # score is defined in ] 0 ; inf [
    assert split_results.train_score > 0
    assert split_results.val_score > 0


def test_get_results(trading_session):
    optimizer = Optimizer(
        trading_session=trading_session(),
        strategy=NewStrategy(config=NewStrategyModel()),
        n_trials=2,
    )
    split_generator = create_ccpv_splits(
        fluctuations=Fluctuations.from_candles(
            convert_candles_to_period(
                generate_candles(size=1000, period=Period(timeframe="1m")),
                target_period=Period(timeframe="1h"),
            ),
        ),
        config=CCPVConfig.model_validate({"test_size": 0.2, "test_samples": 1}),
    )

    best_parameters = optimizer.get_results(split_generator=split_generator)

    assert (
        len(best_parameters) == len(split_generator.splits) == 5
    )  # 5 test splits of size 20%
