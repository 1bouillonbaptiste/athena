from pathlib import Path

from athena.configs import DataConfig, StrategyConfig, TradingSessionConfig, CCPVConfig
from athena.core.dataset_layout import DatasetLayout
from athena.core.fluctuations import Fluctuations
from athena.performance.optimize.optimizer import Optimizer
from athena.performance.optimize.split import create_ccpv_splits
from athena.performance.report import build_and_save_trading_report
from athena.performance.trading_session import TradingSession
from athena.tradingtools.strategies import init_strategy


def run_backtest(
    data_config: DataConfig,
    strategy_config: StrategyConfig,
    session_config: TradingSessionConfig,
    ccpv_config: CCPVConfig,
    dataset_directory: Path,
    output_path: Path,
):
    """Run an end-to-end backtest.

    1. load the dataset
    2. load the strategy
    3. run CCPV to find the optimal parameters for the strategy
    4. run the ultimate backtest on the optimal parameters
    5. save the performance report

    Args:
        data_config: configuration related to dataset creation
        strategy_config: configuration related to strategy creation
        session_config: congiguration for a trading session
        ccpv_config: configuration related to CCPV
        dataset_directory: where to find market data
        output_path: where to save the html report
    """
    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(root_dir=dataset_directory),
        coin=data_config.coin,
        currency=data_config.currency,
        target_period=data_config.period,
        from_date=data_config.from_date,
        to_date=data_config.to_date,
    )
    strategy = init_strategy(
        strategy_name=strategy_config.name, strategy_params=strategy_config.parameters
    )
    trading_session = TradingSession(
        coin=data_config.coin,
        currency=data_config.currency,
        strategy_name=strategy.name,
        config=session_config,
    )

    optimizer = Optimizer(
        trading_session=trading_session, strategy=strategy, n_trials=100
    )

    split_generator = create_ccpv_splits(
        fluctuations=fluctuations,
        config=ccpv_config,
    )

    ccpv_results = optimizer.get_results(split_generator)

    best_parameters = min(ccpv_results, key=lambda x: x.val_score).parameters

    strategy.update_config(best_parameters)

    trades, _ = trading_session.get_trades(fluctuations=fluctuations, strategy=strategy)

    build_and_save_trading_report(
        trades=trades,
        fluctuations=fluctuations,
        output_path=output_path,
    )
