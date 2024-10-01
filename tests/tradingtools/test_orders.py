import datetime

import pytest

from athena.core.interfaces import Candle
from athena.core.types import Coin
from athena.tradingtools import Portfolio
from athena.tradingtools.orders import Position


@pytest.fixture
def position():
    return Position.open(
        open_date=datetime.datetime(2024, 8, 20),
        open_price=100,
        money_to_invest=50,
    )


@pytest.fixture
def candle():
    return Candle.model_validate(
        {
            "coin": Coin.default_coin(),
            "currency": Coin.default_currency(),
            "period": "1h",
            "open_time": datetime.datetime(2024, 8, 25),
            "close_time": datetime.datetime(2024, 8, 26),
            "open": 130,
            "high": 140,
            "low": 120,
            "close": 130,
            "volume": 100,
            "quote_volume": 140,
            "nb_trades": 100,
            "taker_volume": 50,
            "taker_quote_volume": 70,
        }
    )


def test_open_position(position):
    assert position.initial_investment == 50
    assert position.open_fees == 0.05
    assert position.amount == pytest.approx(0.4995, abs=1e-5)
    assert position.amount * position.open_price + position.open_fees == 50


def test_close_position(position):
    trade = position.close(close_date=datetime.datetime(2024, 8, 25), close_price=125)

    assert trade.close_fees == 125 * position.amount * 0.001
    assert trade.total_fees == 125 * position.amount * 0.001 + position.open_fees
    assert (
        pytest.approx(trade.total_profit)
        == position.amount * 125 - 50 - trade.total_fees
    )
    assert trade.trade_duration == datetime.timedelta(days=5)


def test_check_exit_signals_take_profit(position, candle):
    """Price reached take_profit at high_time."""

    position.take_profit = 150
    position.stop_loss = 50

    candle.high = 151
    candle.high_time = datetime.datetime(2024, 8, 25, hour=12)

    close_price, close_date = position.check_exit_signals(candle=candle)

    assert close_price == position.take_profit
    assert close_date == candle.high_time


def test_check_exit_signals_stop_loss(position, candle):
    """Price reached stop_loss, low_time is undefined, take close_time."""

    position.take_profit = 150
    position.stop_loss = 50

    candle.high = 140
    candle.low = 40

    close_price, close_date = position.check_exit_signals(candle=candle)

    assert close_price == position.stop_loss
    assert close_date == candle.close_time


def test_check_exit_signals_low_before_high(position, candle):
    """Price reached stop_loss before take_profit."""

    position.take_profit = 150
    position.stop_loss = 50

    candle.high = 160
    candle.low = 40

    candle.high_time = datetime.datetime(2024, 8, 25, hour=12)
    candle.low_time = datetime.datetime(2024, 8, 25, hour=3)

    close_price, close_date = position.check_exit_signals(candle=candle)

    assert close_price == position.stop_loss
    assert close_date == candle.low_time


def test_check_exit_signals_high_before_low(position, candle):
    """Price reached take_profit before stop_loss."""

    position.take_profit = 150
    position.stop_loss = 50

    candle.high = 160
    candle.low = 40

    candle.high_time = datetime.datetime(2024, 8, 25, hour=1)
    candle.low_time = datetime.datetime(2024, 8, 25, hour=3)

    close_price, close_date = position.check_exit_signals(candle=candle)

    assert close_price == position.take_profit
    assert close_date == candle.high_time


def test_check_exit_signals_undefined_winner(position, candle):
    """Price reached take_profit and stop_loss, but high and low times are not known."""
    position.take_profit = 150
    position.stop_loss = 50

    candle.high = 160
    candle.low = 40

    close_price, close_date = position.check_exit_signals(candle=candle)

    assert close_price == candle.close
    assert close_date == candle.close_time


def test_portfolio_update_from_position(position):
    portfolio = Portfolio.default(position.currency)
    initial_money = portfolio.get_available(position.currency)

    portfolio.update_from_position(position=position)

    assert (
        portfolio.get_available(position.currency)
        == initial_money - position.initial_investment
    )
    assert portfolio.get_available(position.coin) == position.amount


def test_portfolio_update_from_position_fails(position):
    portfolio = Portfolio.default(position.currency)
    position.initial_investment = 150

    with pytest.raises(ValueError, match="Trying to set a negative amount"):
        portfolio.update_from_position(position=position)


def test_portfolio_update_from_trade(position):
    portfolio = Portfolio.default(position.currency)
    initial_money = portfolio.get_available(position.currency)
    portfolio.update_from_position(position=position)

    trade = position.close(
        close_date=position.open_date + datetime.timedelta(days=1),
        close_price=position.open_price,
    )

    portfolio.update_from_trade(trade=trade)

    assert portfolio.get_available(trade.coin) == 0
    assert portfolio.get_available(trade.currency) == pytest.approx(
        initial_money + trade.total_profit, abs=1e-5
    )


def test_portfolio_update_from_trade_fails(position):
    portfolio = Portfolio.default(position.currency)
    portfolio.update_from_position(position=position)
    portfolio.update_coin_amount(
        coin=position.coin, amount_to_add=-position.amount / 2
    )  # remove some coin for update to fail

    trade = position.close(
        close_date=position.open_date + datetime.timedelta(days=1),
        close_price=position.open_price,
    )
    with pytest.raises(ValueError, match="Trying to set a negative amount"):
        portfolio.update_from_trade(trade=trade)
