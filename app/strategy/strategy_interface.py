from abc import ABC, abstractmethod
from typing import Any

from app.data.models import StockData

from .models import MarketRegime, StockSignal


class Strategy(ABC):
    @abstractmethod
    def generate_signals(
        self, stock_data: dict[str, StockData], index_data: StockData
    ) -> list[StockSignal]:
        pass

    @abstractmethod
    def calculate_risk(self, stock_data: StockData) -> float:
        pass

    @abstractmethod
    def get_parameters(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def set_parameters(self, params: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def detect_market_regime(self, market_index_data: StockData) -> MarketRegime:
        pass
