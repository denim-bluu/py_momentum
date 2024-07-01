from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd


class RankingStrategy(ABC):
    @abstractmethod
    def rank_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[str]:
        pass

    @abstractmethod
    def is_eligible(self, df: pd.DataFrame) -> bool:
        pass


class PositionSizer(ABC):
    @abstractmethod
    def calculate_position_size(self, account_value: float, atr: float) -> int:
        pass


class MarketFilter(ABC):
    @abstractmethod
    def is_bullish(self, index_data: pd.DataFrame) -> bool:
        pass


class RebalanceStrategy(ABC):
    @abstractmethod
    def should_rebalance(self, current_shares: int, target_shares: int) -> bool:
        pass
