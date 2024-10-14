import pytest

from athena.configs import TradingSessionConfig
from athena.core.types import Coin
from athena.performance.trading_session import TradingSession
from athena.tradingtools import Strategy


@pytest.fixture
def trading_session():
    def _trading_session(strategy: Strategy) -> TradingSession:
        return TradingSession(
            coin=Coin.default_coin(),
            currency=Coin.default_currency(),
            strategy=strategy,
            config=TradingSessionConfig.model_validate(
                {
                    "position_size": 0.33,
                    "stop_loss_pct": 1,
                    "take_profit_pct": float("inf"),
                }
            ),
        )

    return _trading_session
