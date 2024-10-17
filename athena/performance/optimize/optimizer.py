from dataclasses import dataclass
from typing import Any
import numpy as np

import optuna
from tqdm import tqdm
import logging

from athena.core.fluctuations import Fluctuations
from athena.performance.optimize.optuna import (
    pydantic_model_to_constraints,
    constraints_to_parameters,
)
from athena.performance.optimize.split import SplitGenerator
from athena.performance.trading_session import TradingSession
from athena.tradingtools import Strategy
from athena.tradingtools.metrics.metrics import TradingStatistics

logger = logging.getLogger()
optuna.logging.set_verbosity(optuna.logging.WARNING)


@dataclass
class SplitResult:
    """Store a cross-validation split results.

    Attributes:
        train_statistics: trading statistics from train fluctuations
        val_statistics: trading statistics from validation fluctuations
        parameters: strategy parameters to obtain the results
        train_score: objective function value for train split
        val_score: objective function value for validation split
    """

    train_statistics: TradingStatistics
    val_statistics: TradingStatistics
    parameters: dict[str, Any]
    train_score: float
    val_score: float


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
        all_splits_results: list[SplitResult] = []

        def _score(statistics: TradingStatistics):
            """"""
            return 1 / np.exp(statistics.calmar_ratio + statistics.sharpe_ratio)

        def _objective(trial: optuna.Trial):
            """Objective function to be minimized or maximized."""
            strategy_parameters = constraints_to_parameters(
                trial=trial, constraints=self.constraints
            )
            self.strategy.update_config(strategy_parameters)

            train_statistics = TradingStatistics.from_trades(
                trades=self.trading_session.get_trades(
                    fluctuations=train_fluctuations,
                    strategy=self.strategy,
                )[0]
            )
            val_statistics = TradingStatistics.from_trades(
                trades=self.trading_session.get_trades(
                    fluctuations=val_fluctuations,
                    strategy=self.strategy,
                )[0]
            )
            new_split_results = SplitResult(
                train_statistics=train_statistics,
                val_statistics=val_statistics,
                parameters=strategy_parameters,
                train_score=_score(train_statistics),
                val_score=_score(val_statistics),
            )
            all_splits_results.append(new_split_results)

            return new_split_results.train_score

        study = optuna.create_study()
        study.optimize(_objective, n_trials=self.n_trials)
        return min(all_splits_results, key=lambda results: results.val_score)

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
        logger.info("Running CCPV")
        for ii in tqdm(range(len(split_generator.splits))):
            train_fluctuations, val_fluctuations = split_generator.get_split(ii)
            best_parameters.append(self.optimize(train_fluctuations, val_fluctuations))
        return best_parameters
