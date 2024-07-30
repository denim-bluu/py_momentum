from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from sqlalchemy import BigInteger, Column, String, Date, Float
from py_momentum.app.database import Base


class StockDataPoint(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockData(BaseModel):
    symbol: str
    data_points: List[StockDataPoint]


class BatchStockRequest(BaseModel):
    symbols: List[str]
    start_date: date
    end_date: date
    interval: str


class BatchStockResponse(BaseModel):
    stock_data: dict[str, StockData]
    errors: Optional[dict[str, str]] = None


# SQLAlchemy model for database
class StockDataDB(Base):
    __tablename__ = "stock_data"
    __description__ = "Stock data for a symbol"

    id = Column(BigInteger, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
