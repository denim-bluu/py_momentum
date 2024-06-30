import asyncio
import io
import os
from datetime import datetime
from typing import Dict, List, Protocol

import aiohttp
import pandas as pd
from aiolimiter import AsyncLimiter
from loguru import logger
from tqdm.asyncio import tqdm

from py_momentum.utils.calculations import calculate_atr


# Protocols
class DataFetcher(Protocol):
    async def fetch(
        self, tickers: List[str], start_date: datetime, end_date: datetime
    ) -> Dict[str, pd.DataFrame]: ...


class DataProcessor(Protocol):
    def process(self, data: pd.DataFrame) -> pd.DataFrame: ...


class DataSaver(Protocol):
    def save(self, ticker: str, data: pd.DataFrame, directory: str) -> None: ...


# Fetchers
class YahooFinanceFetcher(DataFetcher):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        limiter: AsyncLimiter,
    ):
        self.session = session
        self.semaphore = semaphore
        self.limiter = limiter

    async def fetch(
        self, tickers: List[str], start_date: datetime, end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        async def fetch_single(ticker):
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
            params = {
                "period1": int(start_date.timestamp()),
                "period2": int(end_date.timestamp()),
                "interval": "1d",
                "events": "history",
            }

            async with self.semaphore:
                await self.limiter.acquire()
                try:
                    async with self.session.get(url, params=params) as response:
                        if response.status == 200:
                            csv_data = await response.text()
                            df = pd.read_csv(
                                io.StringIO(csv_data),
                                parse_dates=["Date"],
                                index_col="Date",
                            )
                            if df.empty:
                                logger.warning(
                                    f"No data available for {ticker} in the specified date range."
                                )
                                return ticker, None
                            return ticker, df
                        else:
                            logger.error(
                                f"Failed to fetch {ticker}, status: {response.status}, reason: {response.reason}, url: {response.url}"
                            )
                            return ticker, None
                except Exception as e:
                    logger.error(f"Error fetching {ticker}: {str(e)}")
                    return ticker, None

        results = await tqdm.gather(
            *[fetch_single(ticker) for ticker in tickers], desc="Fetching data"
        )
        return {ticker: df for ticker, df in results if df is not None}


class CSVFetcher(DataFetcher):
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    async def fetch(
        self, tickers: List[str], start_date: datetime, end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        stock_data = {}
        for ticker in tqdm(tickers, desc="Loading stocks"):
            file_path = os.path.join(self.data_dir, f"{ticker}.csv")
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, index_col="Date", parse_dates=["Date"])
                df = df[(df.index >= start_date) & (df.index <= end_date)]
                if not df.empty:
                    stock_data[ticker] = df
        return stock_data

    def get_available_tickers(self) -> List[str]:
        return [
            f.split(".")[0] for f in os.listdir(self.data_dir) if f.endswith(".csv")
        ]


# Processors
class MovingAverageProcessor(DataProcessor):
    def __init__(self, window: int):
        self.window = window

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data[f"MA_{self.window}"] = data["Adj Close"].rolling(window=self.window).mean()
        return data


class ATRProcessor(DataProcessor):
    def __init__(self, window: int = 14):
        self.window = window

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data["ATR"] = calculate_atr(data, self.window)
        return data


# Savers
class CSVSaver(DataSaver):
    def save(self, ticker: str, data: pd.DataFrame, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        data.to_csv(os.path.join(directory, f"{ticker}.csv"))


# Pipeline
class DataPipeline:
    def __init__(
        self, fetcher: DataFetcher, processors: List[DataProcessor], saver: DataSaver
    ):
        self.fetcher = fetcher
        self.processors = processors
        self.saver = saver

    async def run(
        self,
        tickers: List[str],
        start_date: datetime,
        end_date: datetime,
        save_dir: str,
    ) -> Dict[str, pd.DataFrame]:
        data = await self.fetcher.fetch(tickers, start_date, end_date)
        logger.info(f"Data fetched for {len(data)} tickers.")

        for ticker, df in data.items():
            logger.info(f"Processing data for {ticker}")
            for processor in self.processors:
                df = processor.process(df)
            data[ticker] = df
            logger.info(f"Saving processed data for {ticker}")
            self.saver.save(ticker, df, save_dir)
            logger.info(f"Data saved for {ticker}")

        logger.info("Data pipeline run completed.")
        return data


# DataLoader
class DataLoader:
    def __init__(self, pipeline: DataPipeline):
        self.pipeline = pipeline

    async def load_and_process_data(
        self, tickers: List[str], start_date: str, end_date: str, save_dir: str
    ) -> Dict[str, pd.DataFrame]:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return await self.pipeline.run(tickers, start, end, save_dir)

    def get_available_tickers(self) -> List[str]:
        if isinstance(self.pipeline.fetcher, CSVFetcher):
            return self.pipeline.fetcher.get_available_tickers()
        else:
            raise NotImplementedError(
                "Getting available tickers is only supported for CSVFetcher"
            )
