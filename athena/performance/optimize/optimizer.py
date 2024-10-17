from optuna import Trial, create_study

from athena.core.fluctuations import Fluctuations
from athena.performance.optimize.optuna import (
    pydantic_model_to_constraints,
    constraints_to_parameters,
)
from athena.performance.optimize.split import SplitGenerator
from athena.performance.trading_session import TradingSession
from athena.tradingtools import Strategy
from athena.tradingtools.metrics.metrics import TradingStatistics


class Optimizer:
    """Find the parameters that maximizes the trading performances of a strategy on fluctuations.

    Args:
        trading_session: the session that will be used to get trades from fluctuations
        strategy: a strategy to be optimized
        n_trials: the number of parameter search trials to run
    """

    def __init__(
        self, trading_session: TradingSession, strategy: Strategy, n_trials: int = 100
    ):
        self.trading_session = trading_session
        self.strategy = strategy
        self.n_trials = n_trials

        self.constraints = pydantic_model_to_constraints(self.strategy.config)

    def optimize(
        self,
        train_fluctuations: Fluctuations,
        val_fluctuations: Fluctuations,
    ):
        """Find the parameters that maximizes the trading performances of the strategy on fluctuations.

        Args:
            train_fluctuations: market data used to optimize the strategy
            val_fluctuations: market data used to stop the optimization when strategy overfits the training data

        Returns:
            best parameters as a dict
        """
        objective_scores: list[dict[str : float | int]] = []

        def _objective(trial: Trial):
            """Objective function to be minimized or maximized."""
            strategy_parameters = constraints_to_parameters(
                trial=trial, constraints=self.constraints
            )
            self.strategy.config = self.strategy.config.model_copy(
                update=strategy_parameters
            )

            train_metrics = TradingStatistics.from_trades(
                trades=self.trading_session.get_trades(
                    fluctuations=train_fluctuations,
                    strategy=self.strategy,
                )[0]
            )
            val_metrics = TradingStatistics.from_trades(
                trades=self.trading_session.get_trades(
                    fluctuations=val_fluctuations,
                    strategy=self.strategy,
                )[0]
            )
            objective_scores.append(
                strategy_parameters
                | {"train": train_metrics.sharpe_ratio, "val": val_metrics.sharpe_ratio}
            )
            return train_metrics.sharpe_ratio

        study = create_study()
        study.optimize(_objective, n_trials=self.n_trials)
        return min(objective_scores, key=lambda d: d["val"])

    def find_ccpv_best_parameters(
        self,
        split_generator: SplitGenerator,
    ):
        """Store best parameters for each split.

        Args:
            split_generator: a split generator

        Returns:
            best parameters for each split as a list of dict
        """
        best_parameters = []
        for ii in range(len(split_generator.splits)):
            train_fluctuations, val_fluctuations = split_generator.get_split(ii)
            best_parameters.append(self.optimize(train_fluctuations, val_fluctuations))
        return best_parameters
