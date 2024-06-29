from typing import Dict
import pandas as pd


class StockStatistics:
    def __init__(
        self,
        ticker: str,
        score: float,
        slope: float,
        annualized_return: float,
        r_squared: float,
        current_price: float,
        moving_average: float,
        max_move: float,
        metrics: Dict[str, float],
        rolling_data: pd.DataFrame,
    ):
        self.ticker = ticker
        self.score = score
        self.slope = slope
        self.annualized_return = annualized_return
        self.r_squared = r_squared
        self.current_price = current_price
        self.moving_average = moving_average
        self.max_move = max_move
        self.metrics = metrics
        self.rolling_data = rolling_data
