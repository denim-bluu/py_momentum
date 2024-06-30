import asyncio

import click
import pandas as pd
from loguru import logger

from py_momentum.analysis.results_summary import create_results_summary
from py_momentum.backtester.backtester import Backtester
from py_momentum.data.data_components import (
    ATRProcessor,
    CSVFetcher,
    CSVSaver,
    DataLoader,
    DataPipeline,
    MovingAverageProcessor,
)
from py_momentum.strategy.filters import IndexFilter
from py_momentum.strategy.portfolio import Portfolio
from py_momentum.strategy.position_sizing import PositionSizer
from py_momentum.strategy.ranking import MomentumRankingStrategy
from py_momentum.strategy.rebalance_threshold import ThresholdRebalanceStrategy
from py_momentum.strategy.rebalancer import PositionRebalancer
from py_momentum.utils.date_utils import align_data, get_trading_dates
from py_momentum.visualisation.plotter import (
    plot_portfolio_composition,
    plot_portfolio_performance,
    plot_rolling_metrics,
)


@click.command()
@click.option(
    "--start-date",
    "-s",
    default="2015-01-01",
    required=True,
    help="Start date (YYYY-MM-DD)",
)
@click.option(
    "--end-date",
    "-e",
    default="2024-01-01",
    required=True,
    help="End date (YYYY-MM-DD)",
)
@click.option(
    "--initial-capital", "-c", type=float, default=100000, help="Initial capital"
)
@click.option(
    "--raw-data-dir",
    "-r",
    default="data",
    help="Directory containing raw CSV files",
)
@click.option(
    "--processed-data-dir",
    "-p",
    default="processed_data",
    help="Directory to save processed CSV files",
)
@click.option(
    "--index-symbol", "-i", default="^GSPC", help="Index symbol for benchmark"
)
@click.option(
    "--output-dir",
    "-o",
    default="backtest_results",
    help="Directory to save backtest results",
)
def run_backtest(
    start_date,
    end_date,
    initial_capital,
    raw_data_dir,
    processed_data_dir,
    index_symbol,
    output_dir,
):
    asyncio.run(
        backtest(
            start_date,
            end_date,
            initial_capital,
            raw_data_dir,
            processed_data_dir,
            index_symbol,
            output_dir,
        )
    )


async def backtest(
    start_date,
    end_date,
    initial_capital,
    raw_data_dir,
    processed_data_dir,
    index_symbol,
    output_dir,
):
    # Set up data pipeline for preprocessing
    fetcher = CSVFetcher(raw_data_dir)
    processors = [
        MovingAverageProcessor(100),
        MovingAverageProcessor(200),
        ATRProcessor(),
    ]
    saver = CSVSaver()
    pipeline = DataPipeline(fetcher, processors, saver)
    data_loader = DataLoader(pipeline)

    # Load and preprocess data
    available_tickers = data_loader.get_available_tickers()
    logger.info(
        f"Loading and preprocessing data for {len(available_tickers)} stocks and index {index_symbol}"
    )
    stock_data = await data_loader.load_and_process_data(
        available_tickers, start_date, end_date, processed_data_dir
    )
    index_data = await data_loader.load_and_process_data(
        [index_symbol], start_date, end_date, processed_data_dir
    )
    index_data = (
        index_data[index_symbol] if index_symbol in index_data else pd.DataFrame()
    )

    if not stock_data:
        logger.error("No stock data available. Please download data first.")
        return

    if index_data.empty:
        logger.warning(
            f"No index data available for {index_symbol}. Proceeding without benchmark comparison."
        )
        return

    # Get trading dates and align data
    start_date_ts = pd.Timestamp(start_date)
    end_date_ts = pd.Timestamp(end_date)
    trading_dates = get_trading_dates(
        stock_data, index_data, start_date_ts, end_date_ts
    )
    stock_data, index_data = align_data(stock_data, index_data, trading_dates)

    # Initialize strategy components
    ranking_strategy = MomentumRankingStrategy()
    position_sizer = PositionSizer()
    rebalance_strategy = ThresholdRebalanceStrategy()
    index_filter = IndexFilter()
    portfolio = Portfolio(ranking_strategy, position_sizer, index_filter)
    rebalancer = PositionRebalancer(position_sizer, rebalance_strategy)

    # Run backtest
    logger.info("Running backtest...")
    backtester = Backtester(portfolio, rebalancer)
    portfolio_performance = backtester.run(
        stock_data, index_data, trading_dates, initial_capital
    )

    # Analyze and visualize results
    logger.info("Analyzing results and creating visualizations...")
    benchmark_performance = backtester.get_benchmark_performance(
        index_data, initial_capital
    )
    plot_portfolio_performance(portfolio_performance, benchmark_performance, output_dir)
    plot_portfolio_composition(
        portfolio.positions, stock_data, trading_dates[-1], output_dir
    )
    plot_rolling_metrics(
        portfolio_performance, benchmark_performance, window=252, output_dir=output_dir
    )

    summary, composition, daily_data = create_results_summary(
        portfolio_performance,
        benchmark_performance,
        portfolio.positions,
        stock_data,
        output_dir,
    )

    logger.info(f"Backtest results saved in: {output_dir}")
    logger.info("\nBacktest Summary:")
    logger.info(summary.to_string(index=False))


if __name__ == "__main__":
    run_backtest()
