from abc import ABC, abstractmethod
from .models import MarketRegime, StockSignal
from typing import Any, Dict, List
from ..data.models import StockData


class Strategy(ABC):
    @abstractmethod
    def generate_signals(
        self, stock_data: Dict[str, StockData], index_data: StockData
    ) -> List[StockSignal]:
        pass

    @abstractmethod
    def calculate_risk(self, stock_data: StockData) -> float:
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def set_parameters(self, params: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def detect_market_regime(self, market_index_data: StockData) -> MarketRegime:
        pass
