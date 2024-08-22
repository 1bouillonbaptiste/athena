from athena.optimize import Strategy, Trade
import pandas as pd

from athena.types import Signal


def get_trades_from_strategy_and_fluctuations(
    strategy: Strategy, fluctuations: pd.DataFrame
) -> list[Trade]:
    """Compute the trades that a strategy would have made given fluctuations.

    Args:
        strategy: the strategy to get entry signals
        fluctuations: financial data

    Returns:
        market movement as a list of trades
    """
    trades = []
    for open_time, signal in strategy.get_signals(fluctuations):
        match signal:
            case Signal.WAIT:
                continue
            case Signal.BUY:
                # TODO : check if an open position already exists
                #        if not, open a position at close price
                continue
            case Signal.SELL:
                # TODO : check if an open position already exists
                #        if yes, close it at close price and create a new trade
                continue
        # TODO : check if a position needs to be closed (price reaches tp, sl, limit date)
        #        if yes, close it at price and create a new trade
    return trades
