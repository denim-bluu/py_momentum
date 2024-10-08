from datetime import date

from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, Date, Float, String

from app.database import Base


class StockDataPoint(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockData(BaseModel):
    symbol: str
    data_points: list[StockDataPoint]


class BatchStockRequest(BaseModel):
    symbols: list[str]
    start_date: date
    end_date: date
    interval: str


class BatchStockResponse(BaseModel):
    stock_data: dict[str, StockData]
    errors: dict[str, str] | None = None


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
