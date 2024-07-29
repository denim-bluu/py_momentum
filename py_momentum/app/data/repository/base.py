from abc import ABC, abstractmethod
from typing import List
from datetime import date
from ..models import StockDataWithIndicators
from sqlalchemy.orm import Session


class BaseDataRepository(ABC):
    @abstractmethod
    async def get_stock_data(
        self, symbol: str, start_date: date, end_date: date, db: Session
    ) -> List[StockDataWithIndicators]:
        pass
