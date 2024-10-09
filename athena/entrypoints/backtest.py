from pathlib import Path

import click

from athena.core.config import DataConfig, StrategyConfig
from athena.settings import ProjectContext
from athena.core.interfaces import DatasetLayout, Fluctuations
from athena.entrypoints.utils import load_config
from athena.performance.report import build_and_save_trading_report
from athena.performance.trading_session import TradingSession
from athena.tradingtools.strategies import init_strategy


@click.command()
@click.option(
    "--data-config-path",
    "-dc",
    required=True,
    type=Path,
    help="Path to the data configuration file.",
)
@click.option(
    "--strategy-config-path",
    "-sc",
    required=True,
    type=Path,
    help="Path to the strategy configuration file.",
)
@click.option(
    "--output-dir",
    "-o",
    required=True,
    type=Path,
    help="Directory to save backtesting results.",
)
@click.option(
    "--root-dir",
    "-r",
    default=ProjectContext().raw_data_directory,
    type=Path,
    help="Location of raw market data.",
)
def backtest(
    data_config_path: Path,
    strategy_config_path: Path,
    output_dir: Path,
    root_dir: Path,
):
    """Run a trading algorithm on a dataset and save its performance results.

    Args:
        data_config_path: path to data configuration
        strategy_config_path: path to strategy configuration,
        output_dir: directory to save the performance results
        root_dir: raw market data location
    """

    output_dir.mkdir(exist_ok=True, parents=True)
    data_config = DataConfig.model_validate(load_config(data_config_path))
    strategy_config = StrategyConfig.model_validate(load_config(strategy_config_path))

    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(root_dir=root_dir or ProjectContext().raw_data_directory),
        coin=data_config.coin,
        currency=data_config.currency,
        target_period=data_config.period,
        from_date=data_config.from_date,
        to_date=data_config.to_date,
    )
    strategy = init_strategy(
        strategy_name=strategy_config.name, strategy_params=strategy_config.parameters
    )

    trades, _ = TradingSession.from_config_and_strategy(
        config=data_config, strategy=strategy
    ).get_trades_from_fluctuations(fluctuations=fluctuations)

    build_and_save_trading_report(
        trades=trades,
        fluctuations=fluctuations,
        output_path=output_dir / "performance_report.html",
    )
