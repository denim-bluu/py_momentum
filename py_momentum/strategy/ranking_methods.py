from datetime import date
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats


class MomentumRankingMethod:
    def __init__(self, lookback_period: int = 90):
        self.lookback_period = lookback_period

    def rank_assets(
        self, data: Dict[str, pd.DataFrame], current_date: date
    ) -> List[str]:
        momentum_scores = {}
        for asset, df in data.items():
            if len(df) >= self.lookback_period:
                prices = df["close"].loc[:current_date].iloc[-self.lookback_period :]
                momentum_scores[asset] = self._calculate_momentum_score(prices)

        ranked_assets = sorted(
            momentum_scores.items(), key=lambda x: x[1], reverse=True
        )
        return [asset for asset, _ in ranked_assets]

    @staticmethod
    def _calculate_momentum_score(prices: pd.Series) -> float:
        y = np.log(prices.to_numpy())
        x = np.arange(len(y))
        slope, _, r_value, _, _ = stats.linregress(x, y)

        annualized_slope = (np.exp(slope) - 1) * 252
        r_squared = r_value**2

        return annualized_slope * r_squared
