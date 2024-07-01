from typing import Dict, List

import pandas as pd
from loguru import logger

from py_momentum.strategy.interfaces import MarketFilter, PositionSizer, RankingStrategy
from py_momentum.trading.trade_executor import TradeExecutor


class Portfolio:
    def __init__(self, initial_cash: float = 0):
        self.positions: Dict[str, int] = {}
        self.cash: float = initial_cash

    def get_value(
        self, stock_data: Dict[str, pd.DataFrame], current_date: pd.Timestamp
    ) -> float:
        return self.cash + sum(
            self.positions[ticker]
            * stock_data[ticker].loc[current_date]["Adj Close"].item()
            for ticker in self.positions
        )

    def get_portfolio_value(
        self, stock_data: Dict[str, pd.DataFrame], current_date: pd.Timestamp
    ) -> float:
        return self.cash + sum(
            self.positions[ticker]
            * stock_data[ticker].loc[current_date]["Adj Close"].item()
            for ticker in self.positions
        )


class PortfolioManager:
    def __init__(
        self,
        ranking_strategy: RankingStrategy,
        position_sizer: PositionSizer,
        market_filter: MarketFilter,
        trade_executor: TradeExecutor,
    ):
        self.ranking_strategy = ranking_strategy
        self.position_sizer = position_sizer
        self.market_filter = market_filter
        self.trade_executor = trade_executor

    def update_portfolio(
        self,
        portfolio: Portfolio,
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

        self._sell_positions(portfolio, ranked_stocks, stock_data, current_date)

        if self.market_filter.is_bullish(index_data.loc[:current_date]):
            self._buy_positions(portfolio, ranked_stocks, stock_data, current_date)
        else:
            logger.info("Bearish market conditions. Not buying new positions.")

        logger.info(f"Portfolio update completed. Cash remaining: {portfolio.cash:.2f}")

    def _sell_positions(
        self,
        portfolio: Portfolio,
        top_stocks: List[str],
        stock_data: Dict[str, pd.DataFrame],
        current_date: pd.Timestamp,
    ):
        for ticker in list(portfolio.positions.keys()):
            if ticker not in top_stocks or not self.ranking_strategy.is_eligible(
                stock_data[ticker].loc[:current_date]
            ):
                shares = portfolio.positions[ticker]
                price = stock_data[ticker]["Adj Close"].loc[current_date]
                self.trade_executor.execute_sell(
                    portfolio, ticker, shares, price, current_date
                )

    def _buy_positions(
        self,
        portfolio: Portfolio,
        top_stocks: List[str],
        stock_data: Dict[str, pd.DataFrame],
        current_date: pd.Timestamp,
    ):
        for ticker in top_stocks:
            if ticker not in portfolio.positions:
                atr = stock_data[ticker]["ATR"].loc[current_date]
                price = stock_data[ticker]["Adj Close"].loc[current_date]
                shares = self.position_sizer.calculate_position_size(
                    float(portfolio.cash), float(atr)
                )
                self.trade_executor.execute_buy(
                    portfolio, ticker, shares, price, current_date
                )

    def rebalance_positions(
        self,
        portfolio: Portfolio,
        stock_data: Dict[str, pd.DataFrame],
        current_date: pd.Timestamp,
        rebalance_strategy,
    ):
        logger.info(f"Rebalancing positions on {current_date.date()}")
        account_value = portfolio.get_value(stock_data, current_date)
        for ticker, current_shares in list(portfolio.positions.items()):
            target_shares = self.position_sizer.calculate_position_size(
                account_value, stock_data[ticker]["ATR"].loc[current_date]
            )
            if rebalance_strategy.should_rebalance(current_shares, target_shares):
                price = float(stock_data[ticker].loc[current_date]["Adj Close"].item())
                if target_shares > current_shares:
                    shares_to_buy = target_shares - current_shares
                    self.trade_executor.execute_buy(
                        portfolio, ticker, shares_to_buy, price, current_date
                    )
                elif target_shares < current_shares:
                    shares_to_sell = current_shares - target_shares
                    self.trade_executor.execute_sell(
                        portfolio, ticker, shares_to_sell, price, current_date
                    )

        logger.info("Position rebalancing completed")
