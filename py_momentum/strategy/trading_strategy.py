from datetime import date
from typing import Dict

import pandas as pd

from py_momentum.portfolio.portfolio import Portfolio
from py_momentum.strategy.interfaces import RankingMethod, TrendFilter


class MomentumTradingStrategy:
    def __init__(
        self,
        lookback_period: int,
        trend_filter: TrendFilter,
        ranking_method: RankingMethod,
    ):
        self.lookback_period = lookback_period
        self.trend_filter = trend_filter
        self.ranking_method = ranking_method

    def generate_signals(
        self,
        current_date: date,
        market_data: Dict[str, pd.DataFrame],
        portfolio: Portfolio,
        index_data: pd.DataFrame,
    ) -> Dict[str, str]:
        signals = {}

        # Check if it's a Wednesday (trading day)
        if current_date.weekday() != 2:  # 2 represents Wednesday
            return {asset: "HOLD" for asset in market_data.keys()}

        # Check index filter, if below 200-day moving average, don't trade
        if not self.trend_filter.is_trend_positive(index_data, current_date):
            return {
                asset: "HOLD" if asset in portfolio.get_all_positions() else "SELL"
                for asset in market_data.keys()
            }

        ranked_assets = self.ranking_method.rank_assets(market_data, current_date)
        top_assets = ranked_assets[: int(len(ranked_assets) * 0.2)]  # Top 20%

        for asset, data in market_data.items():
            if asset in top_assets and self.trend_filter.is_trend_positive(
                data, current_date
            ):
                signals[asset] = "BUY"
            elif asset in portfolio.get_all_positions():
                if asset not in top_assets or not self.trend_filter.is_trend_positive(
                    data, current_date
                ):
                    signals[asset] = "SELL"
                else:
                    signals[asset] = "HOLD"
            else:
                signals[asset] = "HOLD"

        return signals
