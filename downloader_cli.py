import asyncio
from datetime import datetime
from typing import List

import aiohttp
import click
from aiolimiter import AsyncLimiter
from loguru import logger

from py_momentum.data.data_components import CSVSaver, YahooFinanceFetcher


@click.command()
@click.option("--tickers", "-t", help="Comma-separated list of stock tickers")
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="File containing stock tickers (one per line)",
)
@click.option(
    "--start-date",
    "-s",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Start date (YYYY-MM-D)",
)
@click.option(
    "--end-date",
    "-e",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="End date (YYYY-MM-DD)",
)
@click.option(
    "--output", "-o", default="raw_data", help="Output directory for raw CSV files"
)
@click.option(
    "--concurrent-limit", "-c", default=5, help="Number of concurrent downloads"
)
@click.option("--rate-limit", "-r", default=30, help="Number of requests per minute")
def download_data(
    tickers, file, start_date, end_date, output, concurrent_limit, rate_limit
):
    if tickers:
        ticker_list = [t.strip() for t in tickers.split(",")]
    elif file:
        with open(file, "r") as f:
            ticker_list = [line.strip() for line in f if line.strip()]
    else:
        logger.error("Please provide either --tickers or --file option.")
        return

    asyncio.run(
        run_downloader(
            ticker_list, start_date, end_date, output, concurrent_limit, rate_limit
        )
    )


async def run_downloader(
    tickers: List[str],
    start_date: datetime,
    end_date: datetime,
    output_dir: str,
    concurrent_limit: int,
    rate_limit: int,
):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(concurrent_limit)
        limiter = AsyncLimiter(rate_limit, 60)  # rate_limit requests per minute

        fetcher = YahooFinanceFetcher(session, semaphore, limiter)
        saver = CSVSaver()

        logger.info(
            f"Downloading raw data for {len(tickers)} stocks from {start_date.date()} to {end_date.date()}"
        )

        stock_data = await fetcher.fetch(tickers, start_date, end_date)

        for ticker, data in stock_data.items():
            saver.save(ticker, data, output_dir)

        logger.info(f"Download completed. Raw data saved in: {output_dir}")
        logger.info(
            f"Successfully downloaded raw data for {len(stock_data)} out of {len(tickers)} tickers"
        )


if __name__ == "__main__":
    download_data()
