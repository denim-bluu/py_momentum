import os
from typing import Dict

import pandas as pd


def create_results_summary(
    portfolio_values: pd.Series,
    benchmark_values: pd.Series,
    positions: Dict[str, int],
    stock_data: Dict[str, pd.DataFrame],
    output_dir: str,
):
    # Calculate various metrics
    portfolio_returns = portfolio_values.pct_change()
    benchmark_returns = benchmark_values.pct_change()

    total_return = (
        float(portfolio_values.iloc[-1]) / float(portfolio_values.iloc[0]) - 1
    ) * 100
    benchmark_return = (benchmark_values.iloc[-1] / benchmark_values.iloc[0] - 1) * 100
    excess_return = total_return - benchmark_return

    sharpe_ratio = (portfolio_returns.mean() / portfolio_returns.std()) * (252 ** (0.5))
    sortino_ratio = (
        portfolio_returns.mean() / portfolio_returns[portfolio_returns < 0].std()
    ) * (252**0.5)

    beta = portfolio_returns.cov(benchmark_returns) / benchmark_returns.var()
    risk_free_rate = 0.02  # Assuming a risk-free rate of 2%
    alpha = (portfolio_returns.mean() - risk_free_rate) - beta * (
        benchmark_returns.mean() - risk_free_rate
    )

    max_drawdown = (portfolio_values / portfolio_values.cummax() - 1).min()

    # Create summary DataFrame
    summary = pd.DataFrame(
        {
            "Metric": [
                "Total Return (%)",
                "Benchmark Return (%)",
                "Excess Return (%)",
                "Sharpe Ratio",
                "Sortino Ratio",
                "Beta",
                "Alpha",
                "Max Drawdown (%)",
            ],
            "Value": [
                total_return,
                benchmark_return,
                excess_return,
                sharpe_ratio,
                sortino_ratio,
                beta,
                alpha,
                max_drawdown * 100,
            ],
        }
    )

    # Add final portfolio composition
    final_date = portfolio_values.index[-1]
    final_composition = {
        ticker: shares * stock_data[ticker].loc[final_date, "Adj Close"]
        for ticker, shares in positions.items()
    }
    total_value = sum(final_composition.values())
    final_composition = {
        ticker: value / total_value * 100 for ticker, value in final_composition.items()
    }

    composition_df = pd.DataFrame(
        list(final_composition.items()), columns=["Stock", "Weight (%)"]
    )

    # Save summary to CSV
    summary.to_csv(os.path.join(output_dir, "backtest_summary.csv"), index=False)
    composition_df.to_csv(
        os.path.join(output_dir, "final_portfolio_composition.csv"), index=False
    )

    # Create a DataFrame with daily values and returns
    daily_data = pd.DataFrame(
        {
            "Portfolio Value": portfolio_values,
            "Benchmark Value": benchmark_values,
            "Portfolio Return": portfolio_returns,
            "Benchmark Return": benchmark_returns,
        }
    )

    daily_data.to_csv(os.path.join(output_dir, "daily_performance.csv"))

    return summary, composition_df, daily_data
