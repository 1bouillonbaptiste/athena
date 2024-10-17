import datetime

import pytest

from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import Portfolio
from athena.core.types import Signal, Period
from athena.testing.generate import generate_fluctuations
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


def test_reset_state(trading_session):
    session = trading_session()
    assert session.trades == []

    session.trades.append("foo")
    session.position = "bar"

    assert session.trades == ["foo"]
    assert session.position == "bar"

    session._reset_state()

    assert session.trades == []
    assert session.position is None


def test_remaining_portfolio(trading_session):
    session = trading_session()
    trades, portfolio = session.get_trades(
        fluctuations=generate_fluctuations(
            size=6,
            from_date=datetime.datetime(2024, 10, 14),  # monday
            period=Period(timeframe="1d"),
            include_high_time=False,
            include_low_time=False,
        ),
        strategy=StrategyBuyMondaySellFriday(),
    )

    assert len(trades) == 1
    assert portfolio.get_available(session.currency) == pytest.approx(
        Portfolio.default(session.currency).get_available(session.currency)
        + trades[0].total_profit
    )


def test_get_trades_fluctuations_with_sell_signal(sample_fluctuations, trading_session):
    session = trading_session()
    trades, _ = session.get_trades(
        fluctuations=sample_fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
        strategy=StrategyBuyMondaySellFriday(),
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


def test_get_trades_price_reach_tp(sample_fluctuations, trading_session):
    session = trading_session()
    session.config.take_profit_pct = 0.1
    trades, portfolio = session.get_trades(
        fluctuations=sample_fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
        strategy=StrategyBuyMondaySellFriday(),
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.take_profit == pytest.approx(110, abs=1e-3)
    assert trade.close_price == pytest.approx(110, abs=1e-3)


def test_get_trades_price_reach_sl(sample_fluctuations, trading_session):
    session = trading_session()
    session.config.stop_loss_pct = 0.1
    trades, _ = session.get_trades(
        fluctuations=sample_fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
        strategy=StrategyBuyMondaySellFriday(),
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.stop_loss == pytest.approx(90, abs=1e-3)
    assert trade.close_price == pytest.approx(90, abs=1e-3)
