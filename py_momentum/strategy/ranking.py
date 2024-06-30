from typing import Dict, List, Protocol

import numpy as np
import pandas as pd
from scipy import stats


class FeatureCalculator:
    @staticmethod
    def calculate_momentum_score(prices: pd.Series, window: int = 90) -> float:
        if len(prices) < window:
            return 0

        y = np.log(prices.tail(window).to_numpy())
        x = np.arange(len(y))
        slope, _, r_value, _, _ = stats.linregress(x, y)

        annualized_slope = (np.exp(slope) - 1) * 252
        r_squared = r_value**2

        return annualized_slope * r_squared


class RankingStrategy(Protocol):
    def rank_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[str]:
        raise NotImplementedError

    def _is_eligible(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError


class MomentumRankingStrategy(RankingStrategy):
    def __init__(
        self,
        momentum_window: int = 90,
        ma_window: int = 100,
        max_gap: float = 0.15,
    ):
        self.feature_calculator = FeatureCalculator()
        self.momentum_window = momentum_window
        self.ma_window = ma_window
        self.max_gap = max_gap

    def rank_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[str]:
        rankings = []
        for ticker, df in stock_data.items():
            if self._is_eligible(df):
                score = self.feature_calculator.calculate_momentum_score(
                    df["Adj Close"], self.momentum_window
                )
                rankings.append((ticker, score))

        rankings.sort(key=lambda x: x[1], reverse=True)
        return [ticker for ticker, _ in rankings]

    def _is_eligible(self, df: pd.DataFrame) -> bool:
        if len(df) < max(self.momentum_window, self.ma_window):
            return False

        current_price = df["Adj Close"].iloc[-1]
        ma = df["Adj Close"].rolling(window=self.ma_window).mean().iloc[-1]
        max_gap = df["Adj Close"].pct_change().rolling(window=90).max().iloc[-1]

        is_eligible = current_price > ma and max_gap <= self.max_gap
        return is_eligible
