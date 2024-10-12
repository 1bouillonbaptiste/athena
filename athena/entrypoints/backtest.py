from pathlib import Path

import click

from athena.configs import DataConfig, StrategyConfig, TradingSessionConfig
from athena.settings import Settings
from athena.core.fluctuations import Fluctuations
from athena.core.dataset_layout import DatasetLayout
from athena.entrypoints.utils import load_config
from athena.performance.report import build_and_save_trading_report
from athena.performance.trading_session import TradingSession
from athena.tradingtools.strategies import init_strategy


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

    fluctuations = Fluctuations.load_from_dataset(
        dataset=DatasetLayout(root_dir=root_dir or Settings().raw_data_directory),
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
        strategy=strategy,
        config=session_config,
    )

    trades, _ = trading_session.get_trades_from_fluctuations(fluctuations=fluctuations)

    build_and_save_trading_report(
        trades=trades,
        fluctuations=fluctuations,
        output_path=output_dir / "performance_report.html",
    )
