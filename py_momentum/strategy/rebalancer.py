from typing import Dict, Protocol

import pandas as pd
from loguru import logger

from py_momentum.strategy.portfolio import Portfolio
from py_momentum.strategy.position_sizing import PositionSizer


class RebalanceStrategy(Protocol):
    def should_rebalance(self, current_shares: int, target_shares: int) -> bool: ...


class ThresholdRebalanceStrategy:
    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold

    def should_rebalance(self, current_shares: int, target_shares: int) -> bool:
        if current_shares == 0:
            return target_shares > 0
        else:
            return abs(current_shares - target_shares) / current_shares > self.threshold


class PositionRebalancer:
    def __init__(
        self, position_sizer: PositionSizer, rebalance_strategy: RebalanceStrategy
    ):
        self.position_sizer = position_sizer
        self.rebalance_strategy = rebalance_strategy

    def rebalance_positions(
        self,
        portfolio: Portfolio,
        stock_data: Dict[str, pd.DataFrame],
        current_date: pd.Timestamp,
    ):
        logger.info(f"Rebalancing positions on {current_date.date()}")
        account_value = portfolio.get_portfolio_value(stock_data, current_date)
        for ticker, current_shares in list(portfolio.positions.items()):
            self._rebalance_position(
                portfolio,
                ticker,
                current_shares,
                account_value,
                stock_data,
                current_date,
            )
        logger.info("Position rebalancing completed")

    def _rebalance_position(
        self,
        portfolio: Portfolio,
        ticker: str,
        current_shares: int,
        account_value: float,
        stock_data: Dict[str, pd.DataFrame],
        current_date: pd.Timestamp,
    ):
        target_shares = self.position_sizer.calculate_position_size(
            account_value, stock_data[ticker]["ATR"].loc[current_date]
        )
        if self.rebalance_strategy.should_rebalance(current_shares, target_shares):
            price = float(stock_data[ticker].loc[current_date]["Adj Close"].item())
            cost = (target_shares - current_shares) * price
            if cost > 0 and cost <= portfolio.cash:
                portfolio.positions[ticker] = target_shares
                portfolio.cash -= cost
                logger.info(
                    f"Increased position in {ticker}: from {current_shares} to {target_shares} shares"
                )
            elif cost < 0:
                portfolio.positions[ticker] = target_shares
                portfolio.cash -= cost  # Adding to cash because cost is negative
                logger.info(
                    f"Decreased position in {ticker}: from {current_shares} to {target_shares} shares"
                )
            else:
                logger.warning(f"Insufficient cash to increase position in {ticker}")
