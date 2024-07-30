from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel


class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"


class OrderSignal(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class StockSignal(BaseModel):
    symbol: str
    signal: str
    risk_unit: float
    momentum_score: float
    current_price: float


class StrategyParameters(BaseModel):
    lookback_period: int = 90
    top_percentage: float = 0.2
    risk_factor: float = 0.001
    market_regime_period: int = 200


class SignalRequest(BaseModel):
    symbols: List[str]
    start_date: date
    end_date: date
    interval: str
    market_index: str


class SignalResponse(BaseModel):
    signals: List[StockSignal]
