from datetime import timedelta

from loguru import logger
import pandas as pd

from py_momentum.analysis.performance_analyser import PerformanceAnalyser
from py_momentum.config_handler import Config
from py_momentum.execution.trade_executor import TradeExecutor
from py_momentum.portfolio.portfolio import Portfolio
from py_momentum.portfolio.portfolio_manager import PortfolioManager
from py_momentum.portfolio.position_sizers import ATRPositionSizer
from py_momentum.strategy.ranking_methods import MomentumRankingMethod
from py_momentum.strategy.trading_strategy import MomentumTradingStrategy
from py_momentum.strategy.trend_filters import MovingAverageTrendFilter
from py_momentum.data.loader import DBDataLoader
from py_momentum.data.utils import get_snp500_symbols


class Backtester:
    def __init__(self, config: Config):
        self.config = config
        self.trading_strategy = self._setup_trading_strategy()
        self.portfolio_manager = self._setup_portfolio_manager()
        self.trade_executor = TradeExecutor(
            commission_rate=config.execution.commission_rate
        )
        self.performance_analyser = PerformanceAnalyser()
        self.portfolio = Portfolio(config.portfolio.initial_capital)
        self.data_pipeline = DBDataLoader("sqlite:///data.db")

    def _setup_trading_strategy(self) -> MomentumTradingStrategy:
        trend_filter = MovingAverageTrendFilter(
            window=self.config.strategy.trend_ma_window
        )
        ranking_method = MomentumRankingMethod(
            lookback_period=self.config.strategy.lookback_period
        )
        return MomentumTradingStrategy(
            lookback_period=self.config.strategy.lookback_period,
            trend_filter=trend_filter,
            ranking_method=ranking_method,
        )

    def _setup_portfolio_manager(self) -> PortfolioManager:
        position_sizer = ATRPositionSizer(
            risk_per_trade=self.config.portfolio.risk_per_trade
        )
        return PortfolioManager(position_sizer=position_sizer)

    def run(self):
        logger.info("Starting backtest")

        tickers = get_snp500_symbols()
        index_symbol = "^GSPC"
        tickers = [t for t in tickers if t != index_symbol]
        market_data = self.data_pipeline.load_data(
            tickers,
            pd.to_datetime(self.config.data.start_date),
            pd.to_datetime(self.config.data.end_date),
        )
        index_data = self.data_pipeline.load_data(
            [index_symbol],
            pd.to_datetime(self.config.data.start_date),
            pd.to_datetime(self.config.data.end_date),
        )
        index_data = index_data[self.config.data.index_symbol]

        # Run backtest
        portfolio_values = []
        all_trades = []
        current_date = self.config.data.start_date
        days_since_rebalance = 0

        while current_date <= self.config.data.end_date:
            # Update portfolio value
            portfolio_values.append(
                self.portfolio.calculate_total_value(
                    {
                        symbol: data["Adj Close"].loc[current_date]
                        for symbol, data in market_data.items()
                    }
                )
            )

            # Generate trading signals
            signals = self.trading_strategy.generate_signals(
                current_date, market_data, self.portfolio, index_data
            )

            # Calculate target positions
            target_positions = self.portfolio_manager.calculate_target_positions(
                current_date, signals, market_data, self.portfolio
            )

            # Execute trades
            self.portfolio, trades = self.trade_executor.execute_trades(
                current_date, target_positions, market_data, self.portfolio
            )
            all_trades.extend(trades)

            # Rebalance if necessary
            days_since_rebalance += 1
            if days_since_rebalance >= self.config.backtest.rebalance_frequency:
                rebalanced_positions = self.portfolio_manager.rebalance_portfolio(
                    current_date, market_data, self.portfolio
                )
                self.portfolio, rebalance_trades = self.trade_executor.execute_trades(
                    current_date, rebalanced_positions, market_data, self.portfolio
                )
                all_trades.extend(rebalance_trades)
                days_since_rebalance = 0

            # Move to next date
            current_date += timedelta(days=1)
            while current_date.weekday() >= 5:  # Skip weekends
                current_date += timedelta(days=1)

        # Analyze performance
        performance_report = self.performance_analyser.generate_report(
            portfolio_values, all_trades
        )

        logger.info("Backtest completed")
        return performance_report
