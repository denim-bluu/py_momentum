from abc import ABC, abstractmethod
from datetime import date

from app.data.models import BatchStockResponse, StockData


class BaseDataRepository(ABC):
    @abstractmethod
    async def get_stock_data(
        self, symbol: str, start_date: date, end_date: date, interval: str
    ) -> StockData:
        pass

    @abstractmethod
    async def get_batch_stock_data(
        self, symbols: list[str], start_date: date, end_date: date, interval: str
    ) -> BatchStockResponse:
        pass

    @abstractmethod
    async def save_stock_data(self, stock_data: StockData) -> None:
        pass
