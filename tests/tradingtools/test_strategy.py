import pytest

from athena.core.interfaces import Fluctuations
from athena.core.types import Signal
from athena.tradingtools import Strategy


class StrategyBuyWeekSellFriday(Strategy):
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


class InvalidStrategy(Strategy):
    """This strategy returns too many signals."""

    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for candle in fluctuations.candles:
            match candle.open_time.isoweekday():
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


def test_strategy_get_signals(fluctuations):
    strategy = StrategyBuyWeekSellFriday()
    assert list(strategy.get_signals(fluctuations=fluctuations(timeframe="1d"))) == [
        (candle, signal)
        for candle, signal in zip(
            fluctuations(timeframe="1d").candles,
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


def test_strategy_get_signals_raises(fluctuations):
    strategy = InvalidStrategy()
    with pytest.raises(ValueError):
        list(strategy.get_signals(fluctuations=fluctuations()))


def test_strategy_compute_signals(fluctuations):
    strategy = StrategyBuyWeekSellFriday()
    assert strategy.compute_signals(fluctuations=fluctuations(timeframe="1d")) == [
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.BUY,
        Signal.SELL,
        Signal.WAIT,
        Signal.WAIT,
    ]
