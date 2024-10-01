from pathlib import Path

import click
import yaml

from athena.core.context import ProjectContext
from athena.core.interfaces import DatasetLayout, Fluctuations
from athena.tradingtools.backtesting import (
    TradingSession,
)
from athena.performance.config import BacktestConfig
from athena.performance.report import build_and_save_trading_report
from athena.tradingtools.strategies import init_strategy


def load_config(filename: Path):
    """Load YAML file."""
    with open(filename, "r") as f:
        return yaml.safe_load(f)


@click.command()
@click.option(
    "--config-path",
    "-c",
    required=True,
    type=Path,
    help="Path to the backtesting configuration file.",
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
    config_path: Path,
    output_dir: Path,
    root_dir: Path,
):
    """Run a trading algorithm on a dataset and save its performance results.

    Args:
        config_path: path to backtesting configuration
        output_dir: directory to save the performance results
        root_dir: raw market data location
    """

    output_dir.mkdir(exist_ok=True, parents=True)
    config = BacktestConfig.model_validate(load_config(config_path))

    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(root_dir=root_dir or ProjectContext().raw_data_directory),
        coin=config.data.coin,
        currency=config.data.currency,
        target_period=config.data.period,
        from_date=config.data.from_date,
        to_date=config.data.to_date,
    )
    strategy = init_strategy(
        strategy_name=config.strategy.name, strategy_params=config.strategy.parameters
    )

    trades, _ = TradingSession.from_config_and_strategy(
        config=config.data, strategy=strategy
    ).get_trades_from_fluctuations(fluctuations=fluctuations)

    build_and_save_trading_report(
        trades=trades,
        fluctuations=fluctuations,
        output_path=output_dir / "performance_report.html",
    )
