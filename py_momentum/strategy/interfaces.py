from datetime import date
from typing import Dict, List, Protocol

import pandas as pd


class TrendFilter(Protocol):
    def is_trend_positive(self, data: pd.DataFrame, current_date: date) -> bool: ...


class RankingMethod(Protocol):
    def rank_assets(
        self, data: Dict[str, pd.DataFrame], current_date: date
    ) -> List[str]: ...


class TradingStrategy(Protocol):
    def generate_signals(
        self,
        current_date: date,
        market_data: Dict[str, pd.DataFrame],
        portfolio: Dict[str, float],
        index_data: pd.DataFrame,
    ) -> Dict[str, str]: ...
