import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class StockVisualizer:
    def __init__(self, stock_data: pd.DataFrame, ticker: str, stats):
        self.stock_data = stock_data
        self.ticker = ticker
        self.stats = stats

    def create_plot(self):
        # Create subplot structure
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(
                f"{self.ticker} Stock Price and Regression",
                "Daily Returns",
            ),
            row_heights=[0.7, 0.3],
        )

        # Add stock price trace
        fig.add_trace(
            go.Scatter(
                x=self.stock_data.index,
                y=self.stock_data["Close"],
                mode="lines",
                name="Stock Price",
                line=dict(color="blue"),
            ),
            row=1,
            col=1,
        )

        # Add 100-day moving average
        ma_100 = self.stock_data["Close"].rolling(window=100).mean()
        fig.add_trace(
            go.Scatter(
                x=self.stock_data.index,
                y=ma_100,
                mode="lines",
                name="100-day MA",
                line=dict(color="red", dash="dash"),
            ),
            row=1,
            col=1,
        )

        # Calculate and add regression line
        last_90_days = self.stock_data.tail(90)
        x = np.arange(len(last_90_days))
        y = np.log(last_90_days["Close"])
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        line = np.exp(intercept + slope * x)
        fig.add_trace(
            go.Scatter(
                x=last_90_days.index,
                y=line,
                mode="lines",
                name="Regression Line",
                line=dict(color="green", dash="dash"),
            ),
            row=1,
            col=1,
        )

        # Add daily returns
        daily_returns = self.stock_data["Close"].pct_change()
        fig.add_trace(
            go.Bar(x=self.stock_data.index, y=daily_returns, name="Daily Returns"),
            row=2,
            col=1,
        )

        # Update layout
        fig.update_layout(
            height=800,
            title_text=f"{self.ticker} Stock Analysis",
            hovermode="x unified",
        )
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Returns", row=2, col=1)

        # Add annotations with key statistics
        annotations = [
            f"Annualized Return: {self.stats.annualized_return:.2%}",
            f"R-squared: {self.stats.r_squared:.4f}",
            f"Slope: {self.stats.slope:.6f}",
            f"Max 90d Move: {self.stats.max_move:.2%}",
        ]
        for i, annotation in enumerate(annotations):
            fig.add_annotation(
                xref="paper",
                yref="paper",
                x=1.02,
                y=0.95 - i * 0.05,
                text=annotation,
                showarrow=False,
                align="left",
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="black",
                borderwidth=1,
            )

        return fig


def visualise_stock(stock_data: pd.DataFrame, ticker: str, stats):
    visualizer = StockVisualizer(stock_data, ticker, stats)
    return visualizer.create_plot()
