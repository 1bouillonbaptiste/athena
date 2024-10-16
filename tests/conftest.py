import datetime

import pytest

from athena.core.fluctuations import Fluctuations
from athena.core.market_entities import Candle, Position
from athena.core.types import Coin, Period


@pytest.fixture(autouse=True)
def patch_client(mocker):
    mocker.patch("athena.client.binance.get_credentials", return_value=(None, None))


@pytest.fixture
def sample_fluctuations():
    def _sample_fluctuations(
        coin=Coin.BTC,
        currency=Coin.USDT,
        timeframe="4h",
        include_high_time: bool = True,
        include_low_time: bool = True,
    ) -> Fluctuations:
        period = Period(timeframe=timeframe)
        return Fluctuations.from_candles(
            candles=[
                Candle(
                    coin=coin,
                    currency=currency,
                    open_time=open_time,
                    period=period.timeframe,
                    close_time=open_time + period.to_timedelta(),
                    high_time=(open_time + datetime.timedelta(hours=12))
                    if include_high_time
                    else None,
                    low_time=(open_time + datetime.timedelta(hours=3))
                    if include_low_time
                    else None,
                    open=open,
                    high=high,
                    low=low,
                    close=close,
                    volume=100,
                    quote_volume=(open + high) / 2 * 100,
                    nb_trades=100,
                    taker_volume=50,
                    taker_quote_volume=(open + high) / 2 * 100 / 2,
                )
                for open_time, open, high, low, close in zip(
                    [
                        datetime.datetime(2024, 8, 19) + ii * period.to_timedelta()
                        for ii in range(7)
                    ],
                    [50, 100, 150, 200, 250, 300, 350],
                    [125, 175, 225, 275, 325, 375, 425],
                    [40, 90, 140, 190, 240, 290, 340],
                    [100, 150, 200, 250, 300, 350, 400],
                )
            ]
        )

    return _sample_fluctuations


@pytest.fixture
def sample_trades():
    """Returns 3 closed positions.

    trade 1 : sell at higher price, it's a win
    trade 2 : sell at same price, it's a loss due to fees
    trade 3 : sell at lower price, it's a loss

    Overall we should make money

    Returns:
        trades as list of closed positions
    """
    trade1 = Position.open(
        open_date=datetime.datetime(2024, 8, 1),
        open_price=100,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 8, 6), close_price=120)

    trade2 = Position.open(
        open_date=datetime.datetime(2024, 9, 1),
        open_price=130,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 9, 6), close_price=130)

    trade3 = Position.open(
        open_date=datetime.datetime(2024, 10, 1),
        open_price=130,
        money_to_invest=50,
    ).close(close_date=datetime.datetime(2024, 10, 6), close_price=120)
    return [trade1, trade2, trade3]
