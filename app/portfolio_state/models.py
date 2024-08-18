from datetime import date, datetime

from pydantic import BaseModel, Field
from sqlalchemy import JSON, BigInteger, Column, Date, DateTime, Float, func

from app.database import Base


class Position(BaseModel):
    symbol: str
    quantity: float = Field(...)
    price: float = Field(..., gt=0)
    value: float = Field(...)


class GetPortfolioStateRequest(BaseModel):
    date: date


class PortfolioState(BaseModel):
    date: date
    timestamp: datetime
    positions: list[Position]
    cash_balance: float = Field(..., ge=0)
    total_value: float = Field(..., ge=0)


class UpdatePortfolioStateRequest(BaseModel):
    date: date
    positions: list[Position]
    cash_balance: float = Field(...)
    total_value: float = Field(...)


class InitiatePortfolioStateRequest(BaseModel):
    initial_cash_balance: float = Field(..., gt=0)


class GetPortfolioStateResponse(BaseModel):
    success: bool
    message: str
    data: PortfolioState


class UpdatePortfolioStateResponse(BaseModel):
    success: bool
    message: str


class PortfolioStateDB(Base):
    __tablename__ = "portfolio_state_data"
    __description__ = "Portfolio state data"

    id = Column(BigInteger, primary_key=True, index=True)
    date = Column(Date, default=func.now(), index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    positions = Column(JSON)
    cash_balance = Column(Float)
    total_value = Column(Float)
