from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats

from py_momentum.strategy.interfaces import RankingStrategy


class MomentumRankingStrategy(RankingStrategy):
    def __init__(
        self,
        momentum_window: int = 90,
        ma_window_filter: int = 100,
        max_gap_filter: float = 0.15,
        pct_rank: float = 0.2,
    ):
        self.momentum_window = momentum_window
        self.ma_window_filter = ma_window_filter
        self.max_gap_filter = max_gap_filter
        self.pct_rank = pct_rank

    def rank_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[str]:
        rankings = []
        for ticker, df in stock_data.items():
            if self.is_eligible(df):
                score = self._calculate_momentum_score(
                    df["Adj Close"], self.momentum_window
                )
                rankings.append((ticker, score))

        rankings.sort(key=lambda x: x[1], reverse=True)
        rankings = rankings[: int(len(rankings) * self.pct_rank)]
        return [ticker for ticker, _ in rankings]

    def is_eligible(self, df: pd.DataFrame) -> bool:
        if len(df) < max(self.momentum_window, self.ma_window_filter):
            return False

        current_price = df["Adj Close"].iloc[-1]
        ma = df["Adj Close"].rolling(window=self.ma_window_filter).mean().iloc[-1]
        max_gap = df["Adj Close"].pct_change().rolling(window=90).max().iloc[-1]

        return current_price > ma and max_gap <= self.max_gap_filter

    @staticmethod
    def _calculate_momentum_score(prices: pd.Series, window: int = 90) -> float:
        if len(prices) < window:
            return 0

        y = np.log(prices.tail(window).to_numpy())
        x = np.arange(len(y))
        slope, _, r_value, _, _ = stats.linregress(x, y)

        annualized_slope = (np.exp(slope) - 1) * 252
        r_squared = r_value**2

        return annualized_slope * r_squared
