# File: portfolio.py

from typing import Dict, List

import pandas as pd
from loguru import logger

from py_momentum.strategy.filters import IndexFilter
from py_momentum.strategy.position_sizing import PositionSizer
from py_momentum.strategy.ranking import RankingStrategy


class Portfolio:
    def __init__(
        self,
        ranking_strategy: RankingStrategy,
        position_sizer: PositionSizer,
        index_filter: IndexFilter,
    ):
        self.ranking_strategy = ranking_strategy
        self.position_sizer = position_sizer
        self.index_filter = index_filter
        self.positions: Dict[str, int] = {}
        self.cash: float = 0

    def update_portfolio_composition(
        self,
        stock_data: Dict[str, pd.DataFrame],
        index_data: pd.DataFrame,
        current_date: pd.Timestamp,
    ):
        logger.info(f"Updating portfolio composition on {current_date.date()}")
        ranked_stocks = self.ranking_strategy.rank_stocks(
            {ticker: df.loc[:current_date] for ticker, df in stock_data.items()}
        )
        if not ranked_stocks:
            logger.warning("No stocks ranked. Skipping portfolio update.")
            return

        top_20_percent = ranked_stocks[: int(len(ranked_stocks) * 0.2)]
        logger.info(f"Top 20% stocks: {', '.join(top_20_percent)}")

        self._sell_positions(top_20_percent, stock_data, current_date)

        if self.index_filter.is_bullish(index_data.loc[:current_date]):
            self._buy_positions(top_20_percent, stock_data, current_date)
        else:
            logger.info("Bearish market conditions. Not buying new positions.")

        logger.info(f"Portfolio update completed. Cash remaining: {self.cash:.2f}")

    def _sell_positions(
        self,
        top_stocks: List[str],
        stock_data: Dict[str, pd.DataFrame],
        current_date: pd.Timestamp,
    ):
        for ticker in list(self.positions.keys()):
            if ticker not in top_stocks or not self.ranking_strategy._is_eligible(
                stock_data[ticker].loc[:current_date]
            ):
                sale_amount = (
                    self.positions[ticker]
                    * stock_data[ticker]["Adj Close"].loc[current_date]
                )
                self.cash += sale_amount
                logger.info(
                    f"Sold {ticker}: {self.positions[ticker]} shares for {sale_amount:.2f}"
                )
                del self.positions[ticker]

    def _buy_positions(
        self,
        top_stocks: List[str],
        stock_data: Dict[str, pd.DataFrame],
        current_date: pd.Timestamp,
    ):
        for ticker in top_stocks:
            if ticker not in self.positions:
                atr = stock_data[ticker]["ATR"].loc[current_date]
                shares = self.position_sizer.calculate_position_size(
                    float(self.cash), float(atr)
                )
                cost = shares * stock_data[ticker]["Adj Close"].loc[current_date]
                if cost <= self.cash:
                    self.positions[ticker] = shares
                    self.cash -= cost
                    logger.info(f"Bought {ticker}: {shares} shares for {cost:.2f}")
                else:
                    logger.warning(
                        f"Insufficient cash to buy {ticker}. Required: {cost:.2f}, Available: {self.cash:.2f}"
                    )

    def get_portfolio_value(
        self, stock_data: Dict[str, pd.DataFrame], current_date: pd.Timestamp
    ) -> float:
        portfolio_value = self.cash + sum(
            self.positions[ticker]
            * stock_data[ticker].loc[current_date]["Adj Close"].item()
            for ticker in self.positions
        )
        return float(portfolio_value)

    def get_position_values(
        self, stock_data: Dict[str, pd.DataFrame], current_date: pd.Timestamp
    ) -> Dict[str, float]:
        return {
            ticker: shares * stock_data[ticker].loc[current_date]["Adj Close"].item()
            for ticker, shares in self.positions.items()
        }
