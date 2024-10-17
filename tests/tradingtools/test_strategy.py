import pytest
from pydantic import BaseModel, Field

from athena.core.fluctuations import Fluctuations
from athena.core.types import Signal
from athena.tradingtools import Strategy


class StrategyBuyWeekSellFridayConfig(BaseModel):
    """Dummy config for strategy.BuyWeekSellFriday."""

    foo: int = Field(default=0)


class StrategyBuyWeekSellFriday(Strategy):
    """Dummy description"""

    def __init__(
        self,
        config: StrategyBuyWeekSellFridayConfig = Field(
            default_factory=StrategyBuyWeekSellFridayConfig
        ),
    ):
        super().__init__()
        self.config = config

    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for candle in fluctuations.candles:
            match candle.open_time.isoweekday():
                case 6 | 7:  # weekend
                    signals.append(Signal.WAIT)
                case 1 | 2 | 3 | 4:  # buy from monday to thursday
                    signals.append(Signal.BUY)
                case 5:  # panic sell on friday, typical crypto player
                    signals.append(Signal.SELL)
        return signals


class InvalidStrategy(StrategyBuyWeekSellFriday):
    """This strategy returns too many signals."""

    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Return dummy signals."""
        signals = super().compute_signals(fluctuations)
        return signals + [Signal.WAIT]


def test_strategy_name():
    strategy = StrategyBuyWeekSellFriday()
    assert strategy.name == "strategy_buy_week_sell_friday"


def test_strategy_get_signals(sample_fluctuations):
    strategy = StrategyBuyWeekSellFriday()
    assert list(
        strategy.get_signals(fluctuations=sample_fluctuations(timeframe="1d"))
    ) == [
        (candle, signal)
        for candle, signal in zip(
            sample_fluctuations(timeframe="1d").candles,
            [
                Signal.BUY,
                Signal.BUY,
                Signal.BUY,
                Signal.BUY,
                Signal.SELL,
                Signal.WAIT,
                Signal.WAIT,
            ],
        )
    ]


def test_strategy_get_signals_raises(sample_fluctuations):
    strategy = InvalidStrategy()
    with pytest.raises(ValueError):
        list(strategy.get_signals(fluctuations=sample_fluctuations()))


def test_strategy_compute_signals(sample_fluctuations):
    strategy = StrategyBuyWeekSellFriday()
    assert strategy.compute_signals(
        fluctuations=sample_fluctuations(timeframe="1d")
    ) == [
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.SELL,
        Signal.WAIT,
        Signal.WAIT,
    ]


def test_update_parameters():
    strategy = StrategyBuyWeekSellFriday(config=StrategyBuyWeekSellFridayConfig())

    assert strategy.config.foo == 0

    strategy.update_config({"foo": 1})

    assert strategy.config.foo == 1
