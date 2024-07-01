import asyncio
import io
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import aiohttp
import pandas as pd
from aiolimiter import AsyncLimiter
from loguru import logger


class DataFetcher(ABC):
    @abstractmethod
    async def fetch(
        self, tickers: List[str], start_date: pd.Timestamp, end_date: pd.Timestamp
    ) -> Dict[str, pd.DataFrame]:
        pass

    def get_available_tickers(self) -> Optional[List[str]]:
        return None


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
        self, tickers: List[str], start_date: pd.Timestamp, end_date: pd.Timestamp
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
                            return ticker, df if not df.empty else None
                        else:
                            logger.error(
                                f"Failed to fetch {ticker}, status: {response.status}, reason: {response.reason}"
                            )
                            return ticker, None
                except Exception as e:
                    logger.error(f"Error fetching {ticker}: {str(e)}")
                    return ticker, None

        results = await asyncio.gather(*[fetch_single(ticker) for ticker in tickers])
        return {ticker: df for ticker, df in results if df is not None}


class CSVFetcher(DataFetcher):
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    async def fetch(
        self, tickers: List[str], start_date: pd.Timestamp, end_date: pd.Timestamp
    ) -> Dict[str, pd.DataFrame]:
        stock_data = {}
        for ticker in tickers:
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
