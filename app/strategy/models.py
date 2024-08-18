from datetime import date
from enum import Enum

from pydantic import BaseModel


class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


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
    symbols: list[str]
    date: date
    interval: str
    market_index: str


class SignalResponse(BaseModel):
    signals: list[StockSignal]
