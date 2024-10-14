import datetime

import pytest

from athena.core.market_entities import Portfolio


def test_reset_state(trading_session):
    assert trading_session.trades == []

    trading_session.trades.append("foo")
    trading_session.position = "bar"

    assert trading_session.trades == ["foo"]
    assert trading_session.position == "bar"

    trading_session._reset_state()

    assert trading_session.trades == []
    assert trading_session.position is None


def test_remaining_portfolio(fluctuations, trading_session):
    trades, portfolio = trading_session.get_trades_from_fluctuations(
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1
    assert (
        portfolio.get_available(trading_session.currency)
        == Portfolio.default(trading_session.currency).get_available(
            trading_session.currency
        )
        + trades[0].total_profit
    )


def test_get_trades_fluctuations_with_sell_signal(fluctuations, trading_session):
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


def test_get_trades_from_fluctuations_price_reach_tp(fluctuations, trading_session):
    trading_session.config.take_profit_pct = 0.1
    trades, portfolio = trading_session.get_trades_from_fluctuations(
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.take_profit == pytest.approx(110, abs=1e-3)
    assert trade.close_price == pytest.approx(110, abs=1e-3)


def test_get_trades_from_fluctuations_price_reach_sl(fluctuations, trading_session):
    trading_session.config.stop_loss_pct = 0.1
    trades, _ = trading_session.get_trades_from_fluctuations(
        fluctuations=fluctuations(
            timeframe="1d", include_high_time=False, include_low_time=False
        ),
    )

    assert len(trades) == 1

    trade = trades[0]

    assert trade.stop_loss == pytest.approx(90, abs=1e-3)
    assert trade.close_price == pytest.approx(90, abs=1e-3)
