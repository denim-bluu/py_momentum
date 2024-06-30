# backtester.py
from typing import Dict, List, Tuple

import pandas as pd
from loguru import logger
from tqdm import tqdm

from py_momentum.logger.trade_logger import TradeLogger
from py_momentum.strategy.portfolio import Portfolio
from py_momentum.strategy.rebalancer import PositionRebalancer


class Backtester:
    def __init__(
        self,
        portfolio: Portfolio,
        rebalancer: PositionRebalancer,
        trade_logger: TradeLogger,
    ):
        self.portfolio = portfolio
        self.rebalancer = rebalancer
        self.trade_logger = trade_logger

    def run(
        self,
        stock_data: Dict[str, pd.DataFrame],
        index_data: pd.DataFrame,
        trading_dates: List[pd.Timestamp],
        initial_capital: float,
    ) -> Tuple[pd.Series, pd.DataFrame]:
        logger.info(f"Starting backtesting with initial capital: {initial_capital}")
        self.portfolio.cash = initial_capital
        self.portfolio.set_trade_logger(self.trade_logger)
        portfolio_values = []

        for date in tqdm(trading_dates, desc="Backtesting"):
            if date.weekday() == 2:  # Wednesday
                logger.info(f"--- Portfolio Update: {date.date()} ---")
                self.portfolio.update_portfolio_composition(
                    stock_data,
                    index_data,
                    date,
                )

            if date.day in [1, 15]:  # First and 15th of the month
                logger.info(f"--- Position Rebalance: {date.date()} ---")
                self.rebalancer.rebalance_positions(self.portfolio, stock_data, date)

            portfolio_value = self.portfolio.get_portfolio_value(stock_data, date)
            portfolio_values.append(portfolio_value)

            if date.day == 1:
                logger.info(f"Portfolio value on {date.date()}: {portfolio_value:.2f}")
                self._log_portfolio_summary(stock_data, date)

        logger.success("Backtesting completed.")
        return pd.Series(
            portfolio_values, index=trading_dates
        ), self.trade_logger.get_trade_history()

    def _log_portfolio_summary(
        self, stock_data: Dict[str, pd.DataFrame], date: pd.Timestamp
    ):
        total_value = self.portfolio.get_portfolio_value(stock_data, date)
        logger.info(
            f"Cash: {self.portfolio.cash:.2f} ({self.portfolio.cash / total_value * 100:.2f}%)"
        )
        logger.info("Top 5 positions:")
        sorted_positions = sorted(
            self.portfolio.positions.items(),
            key=lambda x: x[1] * stock_data[x[0]].loc[date]["Adj Close"].item(),
            reverse=True,
        )
        for ticker, shares in sorted_positions[:5]:
            value = shares * stock_data[ticker].loc[date]["Adj Close"]
            logger.info(
                f"  {ticker}: {shares} shares, ${value:.2f} ({value / total_value * 100:.2f}%)"
            )

    def get_benchmark_performance(
        self, index_data: pd.DataFrame, initial_capital: float
    ) -> pd.Series:
        return (
            index_data["Adj Close"] / index_data["Adj Close"].iloc[0]
        ) * initial_capital
