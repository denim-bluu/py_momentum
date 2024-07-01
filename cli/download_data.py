import asyncio
from datetime import datetime
from typing import List

import aiohttp
import click
import pandas as pd
from aiolimiter import AsyncLimiter
from loguru import logger

from py_momentum.data.fetchers import YahooFinanceFetcher
from py_momentum.data.savers import CSVSaver
from py_momentum.utils.config_util import load_config


@click.command()
@click.option(
    "--config", default="config/config.yaml", help="Path to configuration file"
)
@click.option("--tickers", "-t", help="Comma-separated list of stock tickers")
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="File containing stock tickers (one per line)",
)
def download_data(config, tickers, file):
    config_data = load_config(config)

    output = config_data["data"]["raw_data_dir"]
    start_date = pd.to_datetime(config_data["download"]["start_date"])
    end_date = pd.to_datetime(config_data["download"]["end_date"])
    concurrent_limit = config_data["download"]["concurrent_limit"]
    rate_limit = config_data["download"]["rate_limit"]

    if tickers:
        ticker_list = [t.strip() for t in tickers.split(",")]
    elif file:
        with open(file, "r") as f:
            ticker_list = [line.strip() for line in f if line.strip()]
    else:
        logger.error("Please provide either --tickers or --file option.")
        return

    # Adjust start_date to include lookback period
    adjusted_start_date = start_date - pd.Timedelta(
        days=config_data["max_lookback_days"]
    )

    asyncio.run(
        run_downloader(
            ticker_list,
            adjusted_start_date,
            end_date,
            output,
            concurrent_limit,
            rate_limit,
        )
    )


async def fetch_and_save_stock(
    ticker: str,
    start_date: datetime,
    end_date: datetime,
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    limiter: AsyncLimiter,
    saver: CSVSaver,
    output_dir: str,
):
    fetcher = YahooFinanceFetcher(session, semaphore, limiter)
    try:
        data = await fetcher.fetch(
            [ticker], pd.to_datetime(start_date), pd.to_datetime(end_date)
        )
        if ticker in data and not data[ticker].empty:
            saver.save(ticker, data[ticker], output_dir)
            logger.info(f"Successfully downloaded and saved data for {ticker}")
        else:
            logger.warning(f"No data available for {ticker}")
    except Exception as e:
        logger.error(f"Error processing {ticker}: {str(e)}")


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
        saver = CSVSaver()

        logger.info(
            f"Downloading raw data for {len(tickers)} stocks from {start_date.date()} to {end_date.date()}"
        )

        tasks = []
        for ticker in tickers:
            task = fetch_and_save_stock(
                ticker,
                start_date,
                end_date,
                session,
                semaphore,
                limiter,
                saver,
                output_dir,
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        logger.info(f"Download completed. Raw data saved in: {output_dir}")


if __name__ == "__main__":
    download_data()
