import asyncio
import sys

import click
import pandas as pd
from loguru import logger

from py_momentum.analysis.results_summary import create_results_summary
from py_momentum.backtesting.backtester import Backtester
from py_momentum.data.fetchers import CSVFetcher
from py_momentum.data.pipeline import DataLoader
from py_momentum.logging.trade_logger import TradeLogger
from py_momentum.portfolio.portfolio_manager import Portfolio, PortfolioManager
from py_momentum.strategy.factory import StrategyFactory
from py_momentum.trading.trade_executor import TradeExecutor
from py_momentum.trading.transaction_costs import TransactionCosts
from py_momentum.utils.config_util import load_config
from py_momentum.utils.date_utils import align_data, get_trading_dates


@click.command()
@click.option(
    "--config", default="config/config.yaml", help="Path to configuration file"
)
def run_backtest(config):
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

    start_date = pd.Timestamp(config["backtesting"]["start_date"])
    end_date = pd.Timestamp(config["backtesting"]["end_date"])

    # Load pre-processed data
    available_tickers = data_loader.get_available_tickers()
    if available_tickers is None:
        logger.error("This data fetcher doesn't support getting available tickers.")
        raise NotImplementedError
    else:
        logger.info(
            f"Loading pre-processed data for {len(available_tickers)} stocks and index {config['index']['symbol']}"
        )
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

    # Initialize strategy components using the factory
    ranking_strategy = StrategyFactory.create_ranking_strategy(
        config["strategy"]["ranking_strategy"]
    )
    position_sizer = StrategyFactory.create_position_sizer(
        config["strategy"]["position_sizer"]
    )
    market_filter = StrategyFactory.create_market_filter(
        config["strategy"]["market_filter"]
    )
    rebalance_strategy = StrategyFactory.create_rebalance_strategy(
        config["strategy"]["rebalance_strategy"]
    )

    transaction_costs = TransactionCosts(
        commission_rate=config["transaction_costs"]["commission_rate"],
        slippage_rate=config["transaction_costs"]["slippage_rate"],
    )

    trade_logger = TradeLogger()
    trade_executor = TradeExecutor(transaction_costs, trade_logger)
    portfolio_manager = PortfolioManager(
        ranking_strategy, position_sizer, market_filter, trade_executor
    )

    # Run backtest
    logger.info("Running backtest...")
    initial_portfolio = Portfolio(initial_cash=config["backtesting"]["initial_capital"])
    backtester = Backtester(portfolio_manager, rebalance_strategy, trade_logger)
    final_portfolio, portfolio_performance, trade_history = backtester.run(
        stock_data, index_data, trading_dates, initial_portfolio
    )

    # Analyze and visualize results
    logger.info("Analyzing results and creating visualizations...")
    benchmark_performance = backtester.get_benchmark_performance(
        index_data, config["backtesting"]["initial_capital"]
    )

    summary, composition_df, trade_analysis, daily_data = create_results_summary(
        portfolio_performance,
        benchmark_performance,
        final_portfolio.positions,
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
