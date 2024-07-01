from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from py_momentum.data.fetchers import DataFetcher
from py_momentum.data.processors import DataProcessor
from py_momentum.data.savers import DataSaver


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
        start_date: pd.Timestamp,
        end_date: pd.Timestamp,
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

        logger.info("Data pipeline run completed.")
        return data


class DataLoader:
    def __init__(self, fetcher: DataFetcher):
        self.fetcher = fetcher

    async def load_data(
        self, tickers: List[str], start_date: str, end_date: str
    ) -> Dict[str, pd.DataFrame]:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        return await self.fetcher.fetch(tickers, start, end)

    def get_available_tickers(self) -> Optional[List[str]]:
        return self.fetcher.get_available_tickers()
