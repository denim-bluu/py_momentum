import aiohttp
import pandas as pd
import io
from datetime import datetime
from abc import ABC, abstractmethod
from aiolimiter import AsyncLimiter
import asyncio

class DataFetcher(ABC):
    @abstractmethod
    async def fetch(self, ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        pass

class YahooFinanceFetcher(DataFetcher):
    def __init__(self, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore, limiter: AsyncLimiter):
        self.session = session
        self.semaphore = semaphore
        self.limiter = limiter

    async def fetch(self, ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}"
        params = {
            "period1": int(start_date.timestamp()),
            "period2": int(end_date.timestamp()),
            "interval": "1d",
            "events": "history",
        }

        async with self.semaphore, self.limiter:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    csv_data = await response.text()
                    return pd.read_csv(io.StringIO(csv_data), parse_dates=["Date"], index_col="Date")
                else:
                    raise Exception(f"Failed to fetch {ticker}, status: {response.status}")