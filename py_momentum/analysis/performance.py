import pandas as pd


def calculate_returns(
    portfolio_values: pd.Series, benchmark_values: pd.Series, initial_capital: float
) -> dict:
    total_return = (portfolio_values.iloc[-1] / initial_capital - 1) * 100
    benchmark_return = (benchmark_values.iloc[-1] / initial_capital - 1) * 100
    outperformance = total_return - benchmark_return

    return {
        "total_return": total_return,
        "benchmark_return": benchmark_return,
        "outperformance": outperformance,
    }
