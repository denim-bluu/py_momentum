import os

import numpy as np
import pandas as pd
import plotly.express as px


def calculate_returns_metrics(portfolio_values, benchmark_values):
    """Calculate return-based metrics."""
    portfolio_returns = portfolio_values.pct_change()
    benchmark_returns = benchmark_values.pct_change()

    total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0] - 1) * 100
    benchmark_return = (benchmark_values.iloc[-1] / benchmark_values.iloc[0] - 1) * 100
    excess_return = total_return - benchmark_return

    cagr = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) ** (
        252 / len(portfolio_values)
    ) - 1
    cagr = cagr * 100  # Convert to percentage

    return {
        "Total Return (%)": total_return,
        "Benchmark Return (%)": benchmark_return,
        "Excess Return (%)": excess_return,
        "CAGR (%)": cagr,
        "Annualized Return (%)": portfolio_returns.mean() * 252 * 100,
        "Annualized Benchmark Return (%)": benchmark_returns.mean() * 252 * 100,
    }


def calculate_risk_metrics(portfolio_values, benchmark_values):
    """Calculate risk-based metrics."""
    portfolio_returns = portfolio_values.pct_change()
    benchmark_returns = benchmark_values.pct_change()

    excess_returns = portfolio_returns - benchmark_returns

    volatility = portfolio_returns.std() * np.sqrt(252) * 100
    sharpe_ratio = (portfolio_returns.mean() - 0.02 / 252) / (
        portfolio_returns.std() * np.sqrt(252)
    )
    sortino_ratio = (portfolio_returns.mean() - 0.02 / 252) / (
        portfolio_returns[portfolio_returns < 0].std() * np.sqrt(252)
    )

    beta = portfolio_returns.cov(benchmark_returns) / benchmark_returns.var()
    alpha = (portfolio_returns.mean() - 0.02 / 252) - beta * (
        benchmark_returns.mean() - 0.02 / 252
    )
    alpha = alpha * 252 * 100  # Annualize and convert to percentage

    max_drawdown = (portfolio_values / portfolio_values.cummax() - 1).min() * 100

    return {
        "Volatility (%)": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
        "Beta": beta,
        "Alpha (%)": alpha,
        "Max Drawdown (%)": max_drawdown,
        "Information Ratio": excess_returns.mean()
        / excess_returns.std()
        * np.sqrt(252),
    }


def create_cumulative_returns_chart(portfolio_values, benchmark_values):
    """Create an interactive cumulative returns chart."""
    df = pd.DataFrame(
        {
            "Date": portfolio_values.index,
            "Portfolio": (1 + portfolio_values.pct_change()).cumprod() - 1,
            "Benchmark": (1 + benchmark_values.pct_change()).cumprod() - 1,
        }
    )

    fig = px.line(
        df, x="Date", y=["Portfolio", "Benchmark"], title="Cumulative Returns"
    )
    return fig


def create_drawdown_chart(portfolio_values):
    """Create an interactive drawdown chart."""
    drawdowns = portfolio_values / portfolio_values.cummax() - 1
    fig = px.line(x=drawdowns.index, y=drawdowns.values, title="Portfolio Drawdowns")
    fig.update_yaxes(title="Drawdown")
    return fig


def create_monthly_returns_heatmap(portfolio_values):
    """Create an interactive monthly returns heatmap."""
    returns = portfolio_values.pct_change()
    monthly_returns = (
        returns.groupby([returns.index.year, returns.index.month]).sum().unstack()
    )
    fig = px.imshow(
        monthly_returns,
        labels=dict(x="Month", y="Year", color="Return"),
        x=monthly_returns.columns,
        y=monthly_returns.index,
        title="Monthly Returns Heatmap",
    )
    return fig


def create_results_summary(
    portfolio_values, benchmark_values, positions, stock_data, trades, output_dir
):
    """Generate and save backtest results summary and visualizations."""
    os.makedirs(output_dir, exist_ok=True)

    # Calculate metrics
    returns_metrics = calculate_returns_metrics(portfolio_values, benchmark_values)
    risk_metrics = calculate_risk_metrics(portfolio_values, benchmark_values)

    # Create summary DataFrame
    summary = pd.DataFrame(
        list(returns_metrics.items()) + list(risk_metrics.items()),
        columns=["Metric", "Value"],
    )

    # Create and save visualizations
    cumulative_returns_chart = create_cumulative_returns_chart(
        portfolio_values, benchmark_values
    )
    drawdown_chart = create_drawdown_chart(portfolio_values)
    monthly_returns_heatmap = create_monthly_returns_heatmap(portfolio_values)

    cumulative_returns_chart.write_html(f"{output_dir}/cumulative_returns.html")
    drawdown_chart.write_html(f"{output_dir}/drawdowns.html")
    monthly_returns_heatmap.write_html(f"{output_dir}/monthly_returns_heatmap.html")

    # Final portfolio composition
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

    # Create pie chart for final portfolio composition
    fig = px.pie(
        composition_df,
        values="Weight (%)",
        names="Stock",
        title="Final Portfolio Composition",
    )
    fig.write_html(f"{output_dir}/final_portfolio_composition.html")

    # Analyze trades
    trade_analysis = analyze_trades(
        trades, portfolio_values.index[0], portfolio_values.index[-1]
    )

    # Save data to CSV
    summary.to_csv(f"{output_dir}/backtest_summary.csv", index=False)
    composition_df.to_csv(f"{output_dir}/final_portfolio_composition.csv", index=False)
    trades.to_csv(f"{output_dir}/trade_history.csv", index=False)
    trade_analysis.to_csv(f"{output_dir}/trade_analysis.csv", index=False)

    # Save daily performance data
    daily_data = pd.DataFrame(
        {
            "Portfolio Value": portfolio_values,
            "Benchmark Value": benchmark_values,
            "Portfolio Return": portfolio_values.pct_change(),
            "Benchmark Return": benchmark_values.pct_change(),
        }
    )
    daily_data.to_csv(f"{output_dir}/daily_performance.csv")

    return summary, composition_df, trade_analysis, daily_data


def analyze_trades(trades, start_date, end_date):
    """Analyze trading activity and performance."""
    total_trades = len(trades)
    buy_trades = trades[trades["action"] == "BUY"]
    sell_trades = trades[trades["action"] == "SELL"]

    total_buy_volume = buy_trades["shares"].sum()
    total_sell_volume = sell_trades["shares"].sum()

    total_buy_value = (buy_trades["shares"] * buy_trades["price"]).sum()
    total_sell_value = (sell_trades["shares"] * sell_trades["price"]).sum()

    avg_holding_period = (
        (sell_trades["date"] - buy_trades["date"]).mean().days
        if not sell_trades.empty
        else None
    )

    turnover_rate = (
        (total_buy_value + total_sell_value) / 2 / (end_date - start_date).days * 365
    )

    return pd.DataFrame(
        {
            "Metric": [
                "Total Trades",
                "Buy Trades",
                "Sell Trades",
                "Total Buy Volume",
                "Total Sell Volume",
                "Total Buy Value",
                "Total Sell Value",
                "Avg Holding Period (days)",
                "Annual Turnover Rate",
            ],
            "Value": [
                total_trades,
                len(buy_trades),
                len(sell_trades),
                total_buy_volume,
                total_sell_volume,
                total_buy_value,
                total_sell_value,
                avg_holding_period,
                turnover_rate,
            ],
        }
    )
