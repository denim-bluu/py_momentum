from typing import List
from datetime import date
from sqlalchemy.orm import Session
from .models import StockDataWithIndicators
from .repository.base import BaseDataRepository
from .repository.yahoo_finance import YahooFinanceRepository
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class DataService:
    def __init__(self):
        if settings.data_source == "yahoo_finance":
            self.repository: BaseDataRepository = YahooFinanceRepository()
        else:
            raise ValueError(f"Unsupported data source: {settings.data_source}")

    async def get_stock_data(
        self, symbol: str, start_date: date, end_date: date, db: Session
    ) -> List[StockDataWithIndicators]:
        try:
            return await self.repository.get_stock_data(
                symbol, start_date, end_date, db
            )
        except Exception as e:
            logger.error(f"Error getting stock data: {str(e)}")
            raise
