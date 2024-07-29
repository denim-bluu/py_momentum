from sqlalchemy import Column, Date, Integer, String, Float
from pydantic import BaseModel
from datetime import date
from typing import Optional
from ..database import Base


# SQLAlchemy models
class StockDataDB(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    rsi_14 = Column(Float)


# Pydantic models (for API)
class StockData(BaseModel):
    date: date
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

    class Config:
        from_attributes = True
