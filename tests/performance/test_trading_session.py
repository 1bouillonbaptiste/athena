import datetime

import pytest

from athena.core.interfaces import Fluctuations
from athena.core.types import Signal
from athena.tradingtools import Strategy
from athena.core.market_entities import Portfolio
from athena.performance.config import DataConfig
from athena.performance.trading_session import TradingSession


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
def data_config() -> DataConfig:
    return DataConfig.model_validate(
        {
            "coin": "BTC",
            "currency": "USDT",
            "period": "1h",
            "from_date": "2020-01-01",
            "to_date": "2020-01-07",
        }
    )


@pytest.fixture
def trading_session() -> TradingSession:
    return TradingSession.from_config_and_strategy(
        config=data_config, strategy=StrategyBuyMondaySellFriday(position_size=0.33)
    )


def test_remaining_portfolio(fluctuations, data_config):
    trading_session = TradingSession.from_config_and_strategy(
        config=data_config, strategy=StrategyBuyMondaySellFriday(position_size=0.33)
    )
    trades, portfolio = trading_session.get_trades_from_fluctuations(
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert (
        portfolio.get_available(trading_session.config.currency)
        == Portfolio.default(trading_session.config.currency).get_available(
            trading_session.config.currency
        )
        + trades[0].total_profit
    )


def test_get_trades_fluctuations_with_sell_signal(fluctuations, data_config):
    trading_session = TradingSession.from_config_and_strategy(
        config=data_config, strategy=StrategyBuyMondaySellFriday(position_size=0.33)
    )
    trades, _ = trading_session.get_trades_from_fluctuations(
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1

    trade = trades[0]
    assert trade.open_date == datetime.datetime.fromisoformat(
        "2024-08-20 00:00:00"
    )  # open monday midnight is tuesday
    assert trade.close_date == datetime.datetime.fromisoformat(
        "2024-08-24 00:00:00"
    )  # close friday midnight is saturday
    assert trade.initial_investment == 33

    assert trade.open_price == 100
    assert trade.close_price == 300
    assert trade.amount == pytest.approx(0.32967, abs=1e-3)

    assert trade.stop_loss == 0
    assert trade.take_profit == float("inf")

    assert trade.open_fees == 0.033
    assert trade.close_fees == pytest.approx(0.0989, abs=1e-3)
    assert trade.total_fees == 0.131901
    assert trade.total_profit == pytest.approx(65.7691, abs=1e-3)

    assert trade.is_win


def test_get_trades_from_fluctuations_price_reach_tp(fluctuations, data_config):
    trading_session = TradingSession.from_config_and_strategy(
        config=data_config,
        strategy=StrategyBuyMondaySellFriday(position_size=0.33, take_profit_pct=0.1),
    )
    trades, portfolio = trading_session.get_trades_from_fluctuations(
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.take_profit == pytest.approx(110, abs=1e-3)
    assert trade.close_price == pytest.approx(110, abs=1e-3)


def test_get_trades_from_fluctuations_price_reach_sl(fluctuations, data_config):
    trading_session = TradingSession.from_config_and_strategy(
        config=data_config,
        strategy=StrategyBuyMondaySellFriday(position_size=0.33, stop_loss_pct=0.1),
    )
    trades, _ = trading_session.get_trades_from_fluctuations(
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.stop_loss == pytest.approx(90, abs=1e-3)
    assert trade.close_price == pytest.approx(90, abs=1e-3)
