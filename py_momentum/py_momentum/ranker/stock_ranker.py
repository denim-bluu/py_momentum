from typing import List, Tuple, Dict
import pandas as pd
from py_momentum.criteria.base import RankingCriteria
from py_momentum.regression.base import RegressionStrategy
from py_momentum.metrics.base import Metric
from py_momentum.models.stock_statistics import StockStatistics


class StockRanker:
    def __init__(
        self,
        criteria: List[RankingCriteria],
        regression_strategy: RegressionStrategy,
        metrics: List[Metric],
    ):
        self.criteria = criteria
        self.regression_strategy = regression_strategy
        self.metrics = metrics

    def calculate_statistics(self, df: pd.DataFrame) -> StockStatistics | None:
        if len(df) < 90:
            return None

        rolling_stats = self.regression_strategy.calculate_regression(df, window=90)

        # Use the last values from rolling regression for the overall statistics
        last_stats = rolling_stats.iloc[-1]

        current_price = df["Adj Close"].iloc[-1]
        moving_average = df["Adj Close"].rolling(window=100).mean().iloc[-1]
        max_move = abs(df["Adj Close"].pct_change().tail(90)).max()

        metrics = {metric.get_name(): metric.calculate(df) for metric in self.metrics}

        return StockStatistics(
            ticker=df.index.name,
            score=last_stats["score"],
            slope=last_stats["slope"],
            annualized_return=last_stats["annualized_return"],
            r_squared=last_stats["r_squared"],
            current_price=current_price,
            moving_average=moving_average,
            max_move=max_move,
            metrics=metrics,
            rolling_data=rolling_stats,
        )

    def rank_stocks(
        self, stock_data: Dict[str, pd.DataFrame]
    ) -> List[Tuple[StockStatistics, pd.DataFrame]]:
        rankings = []
        for ticker, df in stock_data.items():
            df.index.name = ticker  # Set the ticker as the index name
            if all(criterion.apply(df) for criterion in self.criteria):
                stats = self.calculate_statistics(df)
                if stats:
                    rankings.append((stats, df))

        return sorted(rankings, key=lambda x: x[0].score, reverse=True)
