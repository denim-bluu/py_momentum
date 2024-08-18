from datetime import date
from enum import Enum

from pydantic import BaseModel

from app.strategy.models import SignalType


class OrderType(str, Enum):
    MARKET = "MARKET"


class Order(BaseModel):
    symbol: str
    order_type: OrderType
    quantity: float
    price: float


class RebalanceRequest(BaseModel):
    date: date
    symbols: list[str]
    interval: str
    market_index: str


class RebalanceResponse(BaseModel):
    success: bool
    message: str


class Position(BaseModel):
    symbol: str
    quantity: int
    price: float
    value: float


class PortfolioSummary(BaseModel):
    date: date
    total_value: float
    cash_balance: float
    positions: dict[str, float]
    allocation: dict[str, float]


class PortfolioPerformance(BaseModel):
    start_date: date
    end_date: date
    total_return: float
    annualized_return: float
    sharpe_ratio: float | None = None
    max_drawdown: float


class StockSignal(BaseModel):
    symbol: str
    signal: SignalType
    risk_unit: float
    momentum_score: float
    current_price: float


class PortfolioState(BaseModel):
    date: date
    positions: list[Position]
    cash_balance: float
    total_value: float


class ExecuteTradesRequest(BaseModel):
    date: date
    orders: list[Order]


class ExecuteTradesResponse(BaseModel):
    success: bool
    message: str
    updated_portfolio_state: PortfolioState
