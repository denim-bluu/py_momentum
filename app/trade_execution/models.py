from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from app.portfolio.models import OrderType


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class Order(BaseModel):
    id: int = Field(default_factory=lambda: uuid4().int)
    symbol: str
    order_type: OrderType
    quantity: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    filled_at: datetime | None = None
    filled_price: float | None = None


class CreateOrderRequest(BaseModel):
    symbol: str
    quantity: float
    order_type: OrderType = OrderType.MARKET


class ExecuteOrdersRequest(BaseModel):
    date: datetime
    market_data: dict[str, float]  # symbol: price


class OrderResponse(BaseModel):
    order: Order
    message: str
