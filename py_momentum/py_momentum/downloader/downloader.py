import asyncio
import random
from typing import List, Tuple, Dict
import pandas as pd
from datetime import datetime
from rich.progress import Progress, TaskID
from rich.console import Console

from .fetcher import DataFetcher
from .saver import DataSaver

console = Console()


class StockDownloader:
    def __init__(self, fetcher: DataFetcher, saver: DataSaver, max_retries: int = 3):
        self.fetcher = fetcher
        self.saver = saver
        self.max_retries = max_retries

    async def download_stock(
        self,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
        progress: Progress,
        task: TaskID,
    ) -> Tuple[str, pd.DataFrame]:
        for attempt in range(self.max_retries):
            try:
                df = await self.fetcher.fetch(ticker, start_date, end_date)
                self.saver.save(ticker, df)
                progress.update(task, advance=1)
                return ticker, df
            except Exception as e:
                console.print(f"[bold red]Error fetching {ticker}: {str(e)}[/bold red]")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep((2**attempt) + random.uniform(0, 1))

        console.print(
            f"[bold red]Failed to fetch {ticker} after {self.max_retries} attempts[/bold red]"
        )
        progress.update(task, advance=1)
        return ticker, df

    async def download_all(
        self, tickers: List[str], start_date: datetime, end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        with Progress() as progress:
            task = progress.add_task("[cyan]Downloading...", total=len(tickers))
            tasks = [
                self.download_stock(ticker, start_date, end_date, progress, task)
                for ticker in tickers
            ]
            results = await asyncio.gather(*tasks)
        return {ticker: df for ticker, df in results if df is not None}
