from datetime import datetime

import click
from loguru import logger

from py_momentum.backtester import Backtester
from py_momentum.config_handler import load_config, Config


@click.command()
@click.option("--config", default="config.yaml", help="Path to the configuration file")
@click.option(
    "--start-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Start date for backtesting (YYYY-MM-DD)",
)
@click.option(
    "--end-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="End date for backtesting (YYYY-MM-D)",
)
def run_backtest(config: str, start_date: datetime, end_date: datetime):
    """Run the Momentum Trading Strategy Backtester"""
    # Load configuration
    cfg: Config = load_config(config)

    # Override dates if provided
    if start_date:
        cfg.data.start_date = start_date
    if end_date:
        cfg.data.end_date = end_date

    # Initialize backtester
    backtester = Backtester(cfg)

    logger.info(f"Starting backtest from {cfg.data.start_date} to {cfg.data.end_date}")

    # Run backtest
    performance_report = backtester.run()

    logger.info("Backtest completed. Performance Report:")
    click.echo(performance_report)


if __name__ == "__main__":
    run_backtest()
