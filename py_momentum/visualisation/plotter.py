import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_portfolio_performance(
    portfolio_values: pd.Series, benchmark_values: pd.Series, output_dir: str
):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Portfolio vs Benchmark Performance", "Daily Returns"),
    )

    # Performance plot
    fig.add_trace(
        go.Scatter(x=portfolio_values.index, y=portfolio_values, name="Portfolio"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=benchmark_values.index, y=benchmark_values, name="Benchmark"),
        row=1,
        col=1,
    )

    # Daily returns plot
    portfolio_returns = portfolio_values.pct_change()
    benchmark_returns = benchmark_values.pct_change()
    fig.add_trace(
        go.Scatter(
            x=portfolio_returns.index, y=portfolio_returns, name="Portfolio Returns"
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=benchmark_returns.index, y=benchmark_returns, name="Benchmark Returns"
        ),
        row=2,
        col=1,
    )

    fig.update_layout(height=800, title_text="Portfolio Performance Analysis")
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.update_yaxes(title_text="Daily Return", row=2, col=1)

    # Save the plot
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    fig.write_html(os.path.join(output_dir, "portfolio_performance.html"))


def plot_portfolio_composition(
    positions: dict, stock_data: dict, date: pd.Timestamp, output_dir: str
):
    values = {
        ticker: shares * stock_data[ticker].loc[date, "Close"]
        for ticker, shares in positions.items()
    }
    total_value = sum(values.values())
    percentages = {
        ticker: value / total_value * 100 for ticker, value in values.items()
    }

    fig = go.Figure(
        data=[
            go.Pie(labels=list(percentages.keys()), values=list(percentages.values()))
        ]
    )
    fig.update_layout(title_text=f"Portfolio Composition on {date.date()}")

    # Save the plot
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    fig.write_html(os.path.join(output_dir, "portfolio_composition.html"))


def plot_rolling_metrics(
    portfolio_values: pd.Series,
    benchmark_values: pd.Series,
    window: int,
    output_dir: str,
):
    portfolio_returns = portfolio_values.pct_change()
    benchmark_returns = benchmark_values.pct_change()

    rolling_sharpe = (
        portfolio_returns.rolling(window).mean()
        / portfolio_returns.rolling(window).std()
    ) * (252**0.5)
    rolling_sortino = (
        portfolio_returns.rolling(window).mean()
        / portfolio_returns[portfolio_returns < 0].rolling(window).std()
    ) * (252**0.5)
    rolling_beta = (
        portfolio_returns.rolling(window).cov(benchmark_returns)
        / benchmark_returns.rolling(window).var()
    )

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            "Rolling Sharpe Ratio",
            "Rolling Sortino Ratio",
            "Rolling Beta",
        ),
    )

    fig.add_trace(
        go.Scatter(x=rolling_sharpe.index, y=rolling_sharpe, name="Sharpe Ratio"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=rolling_sortino.index, y=rolling_sortino, name="Sortino Ratio"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=rolling_beta.index, y=rolling_beta, name="Beta"), row=3, col=1
    )

    fig.update_layout(height=900, title_text=f"Rolling Metrics (Window: {window} days)")
    fig.update_xaxes(title_text="Date", row=3, col=1)

    # Save the plot
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    fig.write_html(os.path.join(output_dir, "rolling_metrics.html"))
