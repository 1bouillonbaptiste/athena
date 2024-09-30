import datetime

import pytest

from athena.core.interfaces import Fluctuations
from athena.core.types import Coin, Side, Signal
from athena.tradingtools import Portfolio, Strategy
from athena.tradingtools.backtesting import get_trades_from_strategy_and_fluctuations


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


def test_get_trades_from_strategy_and_fluctuations_with_sell_signal(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": Coin.default_coin(),
        "currency": Coin.default_currency(),
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
        "amount": pytest.approx(0.32967, abs=1e-5),
        "stop_loss": 0,
        "take_profit": float("inf"),
        "open_fees": 0.033,
        "close_fees": pytest.approx(0.0989, abs=1e-5),
        "total_fees": 0.131901,
        "total_profit": pytest.approx(65.7691, abs=1e-5),
        "profit_pct": pytest.approx(65.7691 / 33, abs=1e-5),
        "is_win": True,
        "side": Side.LONG,
    }


def test_get_trades_from_strategy_and_fluctuations_price_reach_tp(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, take_profit_pct=0.1)
    trades, portfolio = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": Coin.default_coin(),
        "currency": Coin.default_currency(),
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "close_date": datetime.datetime.fromisoformat(
            "2024-08-21 00:00:00"  # "high_time" is missing, so we take close_time
        ),  # close next day = saturday
        "trade_duration": datetime.timedelta(days=1),
        "initial_investment": 33.0,
        "open_price": 100.0,
        "close_price": pytest.approx(110, abs=1e-5),
        "amount": pytest.approx(0.32967, abs=1e-5),
        "stop_loss": 0,
        "take_profit": pytest.approx(110, abs=1e-5),
        "open_fees": 0.033,
        "close_fees": 0.0362637,
        "total_fees": pytest.approx(0.0692637, abs=1e-5),
        "total_profit": 3.1944363,
        "profit_pct": pytest.approx(3.1944363 / 33, abs=1e-5),
        "is_win": True,
        "side": Side.LONG,
    }
    assert (
        portfolio.get_available(Coin.default_currency())
        == Portfolio.default().get_available(Coin.default_currency())
        + trades[0].total_profit
    )


def test_get_trades_from_strategy_and_fluctuations_price_reach_sl(fluctuations):
    strategy = StrategyBuyMondaySellFriday(position_size=0.33, stop_loss_pct=0.1)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_buy_monday_sell_friday",
        "coin": Coin.default_coin(),
        "currency": Coin.default_currency(),
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
        "amount": pytest.approx(0.32967, abs=1e-5),
        "stop_loss": 90.0,
        "take_profit": float("inf"),
        "open_fees": 0.033,
        "close_fees": pytest.approx(0.0989, abs=1e-5),
        "total_fees": 0.131901,
        "total_profit": pytest.approx(65.7691, abs=1e-5),
        "profit_pct": pytest.approx(65.7691 / 33, abs=1e-5),
        "is_win": True,
        "side": Side.LONG,
    }


def test_get_trades_from_strategy_and_fluctuations_position_not_closed(fluctuations):
    strategy = StrategyMondayDCA(position_size=0.33)
    trades, _ = get_trades_from_strategy_and_fluctuations(
        strategy=strategy,
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )
    assert len(trades) == 1
    assert not trades[0].is_closed
    assert trades[0].model_dump() == {
        "strategy_name": "strategy_monday_dca",
        "coin": Coin.default_coin(),
        "currency": Coin.default_currency(),
        "open_date": datetime.datetime.fromisoformat(
            "2024-08-20 00:00:00"
        ),  # open next day = tuesday
        "initial_investment": 33.0,
        "open_price": 100.0,
        "open_fees": 0.033,
        "amount": pytest.approx(0.32967, abs=1e-5),
        "side": Side.LONG,
        "stop_loss": 0,
        "take_profit": float("inf"),
        "close_date": None,
        "close_fees": None,
        "close_price": None,
        "is_win": None,
        "total_fees": None,
        "total_profit": None,
        "profit_pct": None,
        "trade_duration": None,
    }
