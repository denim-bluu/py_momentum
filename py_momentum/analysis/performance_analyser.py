from typing import Dict, List

import numpy as np
import pandas as pd

from py_momentum.execution.trade_executor import Trade


class PerformanceAnalyser:
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def calculate_returns(self, portfolio_values: List[float]) -> pd.Series:
        returns = pd.Series(portfolio_values).pct_change()
        return returns.dropna()

    def calculate_total_return(self, portfolio_values: List[float]) -> float:
        return (portfolio_values[-1] / portfolio_values[0]) - 1

    def calculate_annualized_return(
        self, portfolio_values: List[float], days: int
    ) -> float:
        total_return = self.calculate_total_return(portfolio_values)
        return (1 + total_return) ** (365 / days) - 1

    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        excess_returns = returns - self.risk_free_rate / 252  # Assuming daily returns
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        peak = pd.Series(portfolio_values).cummax()
        drawdown = (pd.Series(portfolio_values) - peak) / peak
        return drawdown.min()

    def calculate_metrics(
        self, portfolio_values: List[float], trades: List[Trade]
    ) -> Dict[str, float]:
        returns = self.calculate_returns(portfolio_values)
        days = len(portfolio_values)

        total_trades = len(trades)
        winning_trades = sum(
            1
            for trade in trades
            if trade.action == "SELL" and trade.price > trade.price
        )  # Simplified win condition

        metrics = {
            "total_return": self.calculate_total_return(portfolio_values),
            "annualized_return": self.calculate_annualized_return(
                portfolio_values, days
            ),
            "sharpe_ratio": self.calculate_sharpe_ratio(returns),
            "max_drawdown": self.calculate_max_drawdown(portfolio_values),
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "total_trades": total_trades,
            "total_commissions": sum(trade.commission for trade in trades),
        }

        return metrics

    def generate_report(
        self, portfolio_values: List[float], trades: List[Trade]
    ) -> str:
        metrics = self.calculate_metrics(portfolio_values, trades)

        report = "Performance Report\n"
        report += "==================\n\n"
        report += f"Total Return: {metrics['total_return']:.2%}\n"
        report += f"Annualized Return: {metrics['annualized_return']:.2%}\n"
        report += f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n"
        report += f"Maximum Drawdown: {metrics['max_drawdown']:.2%}\n"
        report += f"Win Rate: {metrics['win_rate']:.2%}\n"
        report += f"Total Trades: {metrics['total_trades']}\n"
        report += f"Total Commissions: ${metrics['total_commissions']:.2f}\n"

        return report
