# backtester_cli.py
import asyncio
import sys

import click
import pandas as pd
from loguru import logger

from py_momentum.analysis.results_summary import create_results_summary
from py_momentum.backtester.backtester import Backtester
from py_momentum.data.data_components import CSVFetcher, DataLoader
from py_momentum.logger.trade_logger import TradeLogger
from py_momentum.strategy.filters import IndexFilter
from py_momentum.strategy.portfolio import Portfolio
from py_momentum.strategy.position_sizing import PositionSizer
from py_momentum.strategy.ranking import MomentumRankingStrategy
from py_momentum.strategy.rebalancer import (
    PositionRebalancer,
    ThresholdRebalanceStrategy,
)
from py_momentum.strategy.transaction_costs import TransactionCosts
from py_momentum.utils.config_util import load_config
from py_momentum.utils.date_utils import align_data, get_trading_dates


@click.command()
@click.option("--config", default="config.yaml", help="Path to configuration file")
def run_backtest(config):
    """Run the backtesting process using the specified configuration."""
    config_data = load_config(config)
    setup_logging(config_data["output"]["log_file"])
    asyncio.run(backtest(config_data))


def setup_logging(log_file):
    """Set up logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level="INFO")
    logger.add(log_file, rotation="10 MB", retention="1 week", level="DEBUG")


async def backtest(config):
    """Execute the backtesting process."""
    # Set up data loader
    fetcher = CSVFetcher(config["data"]["processed_data_dir"])
    data_loader = DataLoader(fetcher)

    # Load pre-processed data
    available_tickers = data_loader.get_available_tickers()
    logger.info(
        f"Loading pre-processed data for {len(available_tickers)} stocks and index {config['index']['symbol']}"
    )

    start_date = pd.Timestamp(config["backtesting"]["start_date"])
    end_date = pd.Timestamp(config["backtesting"]["end_date"])

    stock_data = await data_loader.load_data(
        available_tickers, str(start_date), str(end_date)
    )
    index_data = await data_loader.load_data(
        [config["index"]["symbol"]], str(start_date), str(end_date)
    )
    index_data = (
        index_data[config["index"]["symbol"]]
        if config["index"]["symbol"] in index_data
        else pd.DataFrame()
    )

    if not stock_data:
        logger.error("No stock data available. Please process data first.")
        return

    if index_data.empty:
        logger.warning(
            f"No index data available for {config['index']['symbol']}. Proceeding without benchmark comparison."
        )
        return

    # Verify that all required indicators are available
    required_columns = (
        ["Adj Close"]
        + [
            f"MA{config['indicator_configs'][key]['window']}"
            for key in config["indicator_configs"]
            if key.startswith("MA")
        ]
        + ["ATR"]
    )
    for ticker, data in stock_data.items():
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            logger.error(f"Missing required columns for {ticker}: {missing_columns}")
            return

    # Get trading dates and align data
    trading_dates = get_trading_dates(stock_data, index_data, start_date, end_date)
    stock_data, index_data = align_data(stock_data, index_data, trading_dates)

    # Initialize strategy components
    ranking_strategy = MomentumRankingStrategy(
        momentum_window=config["strategy"]["momentum_window"],
        ma_window=config["strategy"]["ma_window"],
        max_gap=config["strategy"]["max_gap"],
    )
    position_sizer = PositionSizer()
    rebalance_strategy = ThresholdRebalanceStrategy(
        threshold=config["strategy"]["rebalance_threshold"]
    )
    transaction_costs = TransactionCosts(
        commission_rate=config["transaction_costs"]["commission_rate"],
        slippage_rate=config["transaction_costs"]["slippage_rate"],
    )
    index_filter = IndexFilter()
    portfolio = Portfolio(
        ranking_strategy, position_sizer, index_filter, transaction_costs
    )
    rebalancer = PositionRebalancer(position_sizer, rebalance_strategy)
    trade_logger = TradeLogger()

    # Run backtest
    logger.info("Running backtest...")
    backtester = Backtester(portfolio, rebalancer, trade_logger)
    portfolio_performance, trade_history = backtester.run(
        stock_data, index_data, trading_dates, config["backtesting"]["initial_capital"]
    )

    # Analyze and visualize results
    logger.info("Analyzing results and creating visualizations...")
    benchmark_performance = backtester.get_benchmark_performance(
        index_data, config["backtesting"]["initial_capital"]
    )

    summary, composition_df, trade_analysis, _ = create_results_summary(
        portfolio_performance,
        benchmark_performance,
        portfolio.positions,
        stock_data,
        trade_history,
        config["output"]["dir"],
    )

    logger.info(f"Backtest results saved in: {config['output']['dir']}")
    logger.info("\nBacktest Summary:")
    logger.info(summary.to_string(index=False))

    logger.info("\nFinal Portfolio Composition:")
    logger.info(composition_df.to_string(index=False))

    logger.info("\nTrade Analysis:")
    logger.info(trade_analysis.to_string(index=False))


if __name__ == "__main__":
    run_backtest()
