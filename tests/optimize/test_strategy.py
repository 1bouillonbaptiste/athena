import pandas as pd

from athena.optimize import Strategy
from athena.types import Signal


class DummyStrategy(Strategy):
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


def test_strategy_params():
    strategy = DummyStrategy(
        position_size=0.33,
        take_profit_pct=0.01,
        stop_loss_pct=0.01,
    )
    assert strategy.name == "dummy_strategy"
    assert strategy.position_size == 0.33
    assert strategy.take_profit_pct == 0.01
    assert strategy.stop_loss_pct == 0.01


def test_strategy_get_signals():
    fluctuations = pd.DataFrame(
        {"open_time": pd.date_range("2024-08-19", "2024-08-25", freq="D")}
    )
    strategy = DummyStrategy()
    assert strategy.get_signals(fluctuations=fluctuations) == {
        date: signal
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
    }


def test_strategy_compute_signals():
    fluctuations = pd.DataFrame(
        {"open_time": pd.date_range("2024-08-19", "2024-08-25", freq="D")}
    )
    strategy = DummyStrategy()
    assert strategy.compute_signals(fluctuations=fluctuations) == [
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.SELL,
        Signal.WAIT,
        Signal.WAIT,
    ]
