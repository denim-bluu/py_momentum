import pandas as pd
import yfinance as yf
from typing import List
from datetime import date
from .base import BaseDataRepository
from ..models import StockData, StockDataPoint, BatchStockResponse


class YahooFinanceRepository(BaseDataRepository):
    async def get_stock_data(
        self, symbol: str, start_date: date, end_date: date, interval: str
    ) -> StockData:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date, interval=interval)

        data_points = [
            StockDataPoint(
                date=pd.to_datetime(index).date(),  # type: ignore
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
            )
            for index, row in df.iterrows()
        ]

        return StockData(symbol=symbol, data_points=data_points)

    async def get_batch_stock_data(
        self, symbols: List[str], start_date: date, end_date: date, interval: str
    ) -> BatchStockResponse:
        stock_data = {}
        errors = {}

        for symbol in symbols:
            try:
                stock_data[symbol] = await self.get_stock_data(
                    symbol, start_date, end_date, interval
                )
            except Exception as e:
                errors[symbol] = str(e)

        return BatchStockResponse(stock_data=stock_data, errors=errors)

    async def save_stock_data(self, stock_data: StockData) -> None:
        raise NotImplementedError("YahooFinanceRepository does not support saving data")
