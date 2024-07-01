import pandas as pd
from loguru import logger

from py_momentum.logging.trade_logger import TradeLogger
from py_momentum.trading.transaction_costs import TransactionCosts


class TradeExecutor:
    def __init__(
        self,
        transaction_costs: TransactionCosts,
        trade_logger: TradeLogger | None = None,
    ):
        self.transaction_costs = transaction_costs
        self.trade_logger = trade_logger

    def execute_buy(
        self, portfolio, ticker: str, shares: int, price: float, date: pd.Timestamp
    ) -> bool:
        total_cost = shares * price
        costs = self.transaction_costs.calculate_costs(price, shares)
        total_cost += costs

        if total_cost <= portfolio.cash:
            portfolio.positions[ticker] = portfolio.positions.get(ticker, 0) + shares
            portfolio.cash -= total_cost
            if self.trade_logger:
                self.trade_logger.log_trade(date, ticker, "BUY", shares, price, costs)
            logger.info(
                f"Bought {ticker}: {shares} shares for {total_cost:.2f}, transaction costs: {costs:.2f}"
            )
            return True
        else:
            logger.warning(
                f"Insufficient cash to buy {ticker}. Required: {total_cost:.2f}, Available: {portfolio.cash:.2f}"
            )
            return False

    def execute_sell(
        self, portfolio, ticker: str, shares: int, price: float, date: pd.Timestamp
    ) -> bool:
        if ticker in portfolio.positions and portfolio.positions[ticker] >= shares:
            sale_amount = shares * price
            costs = self.transaction_costs.calculate_costs(price, shares)
            portfolio.positions[ticker] -= shares
            if portfolio.positions[ticker] == 0:
                del portfolio.positions[ticker]
            portfolio.cash += sale_amount - costs
            if self.trade_logger:
                self.trade_logger.log_trade(date, ticker, "SELL", shares, price, costs)
            logger.info(
                f"Sold {ticker}: {shares} shares for {sale_amount:.2f}, transaction costs: {costs:.2f}"
            )
            return True
        else:
            logger.warning(
                f"Insufficient shares to sell {ticker}. Required: {shares}, Available: {portfolio.positions.get(ticker, 0)}"
            )
            return False
