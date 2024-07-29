from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StockData(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class TechnicalIndicators(BaseModel):
    sma_50: Optional[float]
    sma_200: Optional[float]
    rsi_14: Optional[float]


class StockDataWithIndicators(StockData):
    indicators: TechnicalIndicators
