from athena.optimize import Strategy, Trade
import pandas as pd


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
    # TODO: iterate over fluctuations
    #       1/ get entry signal
    #       2/ when buy, open a position at close price (= beginning of next candle)
    #       3/ check exit conditions (strategy sell, tp or sl)
    #       4/ close position & create new trade
    return []
