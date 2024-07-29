from typing import List
from datetime import datetime
from .models import StockDataWithIndicators
from .repository.base import BaseDataRepository
from .repository.yahoo_finance import YahooFinanceRepository
from ..config import settings


class DataService:
    def __init__(self):
        if settings.data_source == "yahoo_finance":
            self.repository: BaseDataRepository = YahooFinanceRepository()
        else:
            raise ValueError(f"Unsupported data source: {settings.data_source}")

    async def get_stock_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[StockDataWithIndicators]:
        return await self.repository.get_stock_data(symbol, start_date, end_date)
