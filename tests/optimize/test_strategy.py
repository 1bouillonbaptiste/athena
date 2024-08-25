import pandas as pd

from athena.optimize import Strategy
from athena.core.types import Signal

import pytest


class StrategyBuyWeekSellFriday(Strategy):
    """"""

    def compute_signals(self, fluctuations: pd.DataFrame) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for _, row in fluctuations.iterrows():
            match row["open_time"].isoweekday():
                case 6 | 7:  # weekend
                    signals.append(Signal.WAIT)
                case 1 | 2 | 3 | 4:  # buy from monday to thursday
                    signals.append(Signal.BUY)
                case 5:  # panic sell on friday
                    signals.append(Signal.SELL)
        return signals


class InvalidStrategy(Strategy):
    """This strategy returns too many signals."""

    def compute_signals(self, fluctuations: pd.DataFrame) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for _, row in fluctuations.iterrows():
            match row["open_time"].isoweekday():
                case 6 | 7:  # weekend
                    signals.append(Signal.WAIT)
                case 1 | 2 | 3 | 4:  # buy from monday to thursday
                    signals.append(Signal.BUY)
                case 5:  # panic sell on friday
                    signals.append(Signal.SELL)
        return signals + [Signal.WAIT]


def test_strategy_name():
    strategy = StrategyBuyWeekSellFriday(
        position_size=0.33,
        take_profit_pct=0.01,
        stop_loss_pct=0.01,
    )
    assert strategy.name == "strategy_buy_week_sell_friday"


def test_strategy_get_signals():
    fluctuations = pd.DataFrame(
        {"open_time": pd.date_range("2024-08-19", "2024-08-25", freq="D")}
    )
    strategy = StrategyBuyWeekSellFriday()
    assert list(strategy.get_signals(fluctuations=fluctuations)) == [
        (date, signal)
        for date, signal in zip(
            fluctuations["open_time"],
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


def test_strategy_get_signals_raises():
    fluctuations = pd.DataFrame(
        {"open_time": pd.date_range("2024-08-19", "2024-08-25", freq="D")}
    )
    strategy = InvalidStrategy()

    with pytest.raises(ValueError):
        list(strategy.get_signals(fluctuations=fluctuations))


def test_strategy_compute_signals():
    fluctuations = pd.DataFrame(
        {"open_time": pd.date_range("2024-08-19", "2024-08-25", freq="D")}
    )
    strategy = StrategyBuyWeekSellFriday()
    assert strategy.compute_signals(fluctuations=fluctuations) == [
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.SELL,
        Signal.WAIT,
        Signal.WAIT,
    ]
