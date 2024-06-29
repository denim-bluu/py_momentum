import click
from rich.console import Console
from rich.table import Table
import plotly.io as pio

from py_momentum.criteria.moving_average import MovingAverageCriteria
from py_momentum.criteria.max_move import MaxMoveCriteria
from py_momentum.regression.exponential import ExponentialRegressionStrategy
from py_momentum.regression.relative_growth import RelativeGrowthRegressionStrategy
from py_momentum.metrics.atr import ATRMetric
from py_momentum.ranker.stock_ranker import StockRanker
from py_momentum.utils.data_loader import load_stock_data
from py_momentum.visualisation.stock_visualiser import visualise_stock

console = Console()


@click.command()
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(exists=True),
    required=True,
    help="Directory containing stock data CSV files",
)
@click.option("--top", "-t", default=10, help="Number of top stocks to display")
@click.option(
    "--visualise", "-v", is_flag=True, help="Generate interactive visualisations"
)
@click.option(
    "--regression",
    "-r",
    type=click.Choice(["exponential", "relative_growth"]),
    default="exponential",
    help="Regression strategy to use",
)
def main(data_dir: str, top: int, visualise: bool, regression: str):
    console.print("[bold green]Enhanced Stock Ranking System[/bold green]")

    stock_data = load_stock_data(data_dir)
    console.print(f"[cyan]Loaded data for {len(stock_data)} stocks[/cyan]")

    criteria = [
        MovingAverageCriteria(window=100),
        MaxMoveCriteria(days=90, threshold=0.15),
    ]

    if regression == "exponential":
        regression_strategy = ExponentialRegressionStrategy()
    else:
        regression_strategy = RelativeGrowthRegressionStrategy()

    ranker = StockRanker(criteria, regression_strategy, [ATRMetric()])
    rankings = ranker.rank_stocks(stock_data)

    table = Table(title=f"Top {top} Ranked Stocks with Detailed Statistics")
    table.add_column("Rank", style="cyan", no_wrap=True)
    table.add_column("Ticker", style="magenta")
    table.add_column("Score", justify="right", style="green")
    table.add_column("Slope", justify="right", style="blue")
    table.add_column("R-squared", justify="right", style="blue")
    table.add_column("Ann. Return", justify="right", style="yellow")
    table.add_column("Current Price", justify="right", style="green")
    table.add_column("100d MA", justify="right", style="yellow")
    table.add_column("Max 90d Move", justify="right", style="red")
    for metric in ranker.metrics:
        table.add_column(metric.get_name(), justify="right", style="purple")

    for i, (s, df) in enumerate(rankings[:top], 1):
        row = [
            str(i),
            s.ticker,
            f"{s.score:.4f}",
            f"{s.slope:.6f}",
            f"{s.r_squared:.4f}",
            f"{s.annualized_return:.2%}",
            f"${s.current_price:.2f}",
            f"${s.moving_average:.2f}",
            f"{s.max_move:.2%}",
        ]
        row.extend([f"{s.metrics[metric.get_name()]:.2f}" for metric in ranker.metrics])
        table.add_row(*row)

        if visualise:
            fig = visualise_stock(df, s.ticker, s)
            pio.write_html(fig, file=f"{s.ticker}_analysis.html", auto_open=False)

    console.print(table)


if __name__ == "__main__":
    main()
