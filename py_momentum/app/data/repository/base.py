from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from ..models import StockDataWithIndicators

class BaseDataRepository(ABC):
    @abstractmethod
    async def get_stock_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[StockDataWithIndicators]:
        pass