import click
from rich.console import Console
from rich.panel import Panel
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
from datetime import datetime, timedelta
import time
import os

from py_momentum.downloader.fetcher import YahooFinanceFetcher
from py_momentum.downloader.saver import CSVSaver
from py_momentum.downloader.downloader import StockDownloader

console = Console()


@click.command()
@click.option("--tickers", "-t", help="Comma-separated list of stock tickers")
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="File containing stock tickers (one per line)",
)
@click.option(
    "--days", "-d", default=365, help="Number of days of historical data to fetch"
)
@click.option(
    "--output", "-o", default="stock_data", help="Output directory for CSV files"
)
def main(tickers, file, days, output):
    if tickers:
        ticker_list = [t.strip() for t in tickers.split(",")]
    elif file:
        with open(file, "r") as f:
            ticker_list = [line.strip() for line in f if line.strip()]
    else:
        console.print(
            "[bold red]Error: Please provide either --tickers or --file option.[/bold red]"
        )
        return

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    async def run_downloader():
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(5)
            limiter = AsyncLimiter(30, 60)
            fetcher = YahooFinanceFetcher(session, semaphore, limiter)
            saver = CSVSaver(output)
            downloader = StockDownloader(fetcher, saver)

            return await downloader.download_all(ticker_list, start_date, end_date)

    console.print(Panel.fit("[bold green]Stock Data Downloader[/bold green]"))
    console.print(
        f"[cyan]Downloading data for {len(ticker_list)} stocks from {start_date.date()} to {end_date.date()}[/cyan]"
    )

    start_time = time.time()
    stock_data = asyncio.run(run_downloader())
    end_time = time.time()

    console.print(
        f"\n[green]Download completed in {end_time - start_time:.2f} seconds[/green]"
    )
    console.print(
        f"[green]Successfully downloaded data for {len(stock_data)} stocks[/green]"
    )
    console.print(f"[cyan]Data saved in: {os.path.abspath(output)}[/cyan]")


if __name__ == "__main__":
    main()
