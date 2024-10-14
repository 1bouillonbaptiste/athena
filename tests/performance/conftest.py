import pytest

from athena.configs import TradingSessionConfig
from athena.core.fluctuations import Fluctuations
from athena.core.types import Coin, Signal
from athena.performance.trading_session import TradingSession
from athena.tradingtools import Strategy


class StrategyBuyMondaySellFriday(Strategy):
    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for candle in fluctuations.candles:
            match candle.open_time.isoweekday():
                case 6 | 7:  # weekend
                    signals.append(Signal.WAIT)
                case 1:  # all-in on monday, typical crypto player
                    signals.append(Signal.BUY)
                case 2 | 3 | 4:  # no money left
                    signals.append(Signal.WAIT)
                case 5:  # panic sell on friday, typical crypto player
                    signals.append(Signal.SELL)
        return signals


@pytest.fixture
def trading_session() -> TradingSession:
    return TradingSession(
        coin=Coin.default_coin(),
        currency=Coin.default_currency(),
        strategy=StrategyBuyMondaySellFriday(),
        config=TradingSessionConfig.model_validate(
            {"position_size": 0.33, "stop_loss_pct": 1, "take_profit_pct": float("inf")}
        ),
    )
