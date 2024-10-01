import datetime

import pytest

from athena.core.interfaces import Fluctuations
from athena.core.types import Side, Signal
from athena.tradingtools import Strategy
from athena.tradingtools.backtesting import (
    get_trades_from_strategy_and_fluctuations,
    DataConfig,
)


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


class StrategyMondayDCA(Strategy):
    def compute_signals(self, fluctuations: Fluctuations) -> list[Signal]:
        """Return dummy signals."""
        signals = []
        for candle in fluctuations.candles:
            match candle.open_time.isoweekday():
                case 1:  # dca on monday
                    signals.append(Signal.BUY)
                case _:
                    signals.append(Signal.WAIT)
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


def test_get_trades_from_strategy_and_fluctuations_with_sell_signal(
    fluctuations, data_config
):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        config=data_config,
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": data_config.coin,
        "currency": data_config.currency,
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "close_date": datetime.datetime.fromisoformat(
            "2024-08-24 00:00:00"
        ),  # close next day = saturday
        "trade_duration": datetime.timedelta(days=4),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "close_price": 300.0,
        "amount": pytest.approx(0.32967, abs=1e-3),
        "stop_loss": 0,
        "take_profit": float("inf"),
        "open_fees": 0.033,
        "close_fees": pytest.approx(0.0989, abs=1e-3),
        "total_fees": 0.131901,
        "total_profit": pytest.approx(65.7691, abs=1e-3),
        "profit_pct": pytest.approx(65.7691 / 33, abs=1e-3),
        "is_win": True,
        "side": Side.LONG,
    }


def test_get_trades_from_strategy_and_fluctuations_price_reach_tp(
    fluctuations, data_config
):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, take_profit_pct=0.1)
    trades, portfolio = get_trades_from_strategy_and_fluctuations(
        config=data_config,
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": data_config.coin,
        "currency": data_config.currency,
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "close_date": datetime.datetime.fromisoformat(
            "2024-08-21 00:00:00"  # "high_time" is missing, so we take close_time
        ),  # close next day = saturday
        "trade_duration": datetime.timedelta(days=1),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "close_price": pytest.approx(110, abs=1e-3),
        "amount": pytest.approx(0.32967, abs=1e-3),
        "stop_loss": 0,
        "take_profit": pytest.approx(110, abs=1e-3),
        "open_fees": 0.033,
        "close_fees": 0.0362637,
        "total_fees": pytest.approx(0.0692637, abs=1e-3),
        "total_profit": 3.1944363,
        "profit_pct": pytest.approx(3.1944363 / 33, abs=1e-3),
        "is_win": True,
        "side": Side.LONG,
    }
    assert portfolio.get_available(data_config.currency) == 100 + trades[0].total_profit


def test_get_trades_from_strategy_and_fluctuations_price_reach_sl(
    fluctuations, data_config
):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, stop_loss_pct=0.1)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        config=data_config,
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": data_config.coin,
        "currency": data_config.currency,
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "close_date": datetime.datetime.fromisoformat(
            "2024-08-24 00:00:00"
        ),  # close next day = saturday
        "trade_duration": datetime.timedelta(days=4),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "close_price": 300.0,
        "amount": pytest.approx(0.32967, abs=1e-3),
        "stop_loss": 90.0,
        "take_profit": float("inf"),
        "open_fees": 0.033,
        "close_fees": pytest.approx(0.0989, abs=1e-3),
        "total_fees": 0.131901,
        "total_profit": pytest.approx(65.7691, abs=1e-3),
        "profit_pct": pytest.approx(65.7691 / 33, abs=1e-3),
        "is_win": True,
        "side": Side.LONG,
    }
