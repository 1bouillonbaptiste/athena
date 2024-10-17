from pathlib import Path

import click

from athena.configs import DataConfig, StrategyConfig, TradingSessionConfig, CCPVConfig
from athena.performance.backtesting import run_backtest
from athena.settings import Settings
from athena.entrypoints.utils import load_config


@click.command()
@click.option(
    "--config-path",
    "-c",
    required=True,
    type=Path,
    help="Path to the main configuration file.",
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
    default=Settings().raw_data_directory,
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
        config_path: path to configuration
        output_dir: directory to save the performance results
        root_dir: raw market data location
    """

    output_dir.mkdir(exist_ok=True, parents=True)
    config = load_config(config_path)

    data_config = DataConfig.model_validate(config.get("data"))
    strategy_config = StrategyConfig.model_validate(config.get("strategy"))
    session_config = TradingSessionConfig.model_validate(config.get("session"))
    ccpv_config = CCPVConfig.model_validate(config.get("ccpv"))

    run_backtest(
        data_config=data_config,
        strategy_config=strategy_config,
        session_config=session_config,
        ccpv_config=ccpv_config,
        dataset_directory=root_dir or Settings().raw_data_directory,
        output_path=output_dir / "performance_report.html",
    )
