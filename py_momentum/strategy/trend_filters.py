from datetime import date

import pandas as pd


class MovingAverageTrendFilter:
    def __init__(self, window: int = 100):
        self.window = window

    def is_trend_positive(self, data: pd.DataFrame, current_date: date) -> bool:
        if len(data) < self.window:
            return False

        ma = data["close"].rolling(window=self.window).mean().loc[current_date]
        current_price = data["close"].loc[current_date]

        return current_price > ma


class PriceAboveMovingAverageTrendFilter:
    def __init__(self, window: int = 200):
        self.window = window

    def is_trend_positive(self, data: pd.DataFrame, current_date: date) -> bool:
        if len(data) < self.window:
            return False

        ma = data["close"].rolling(window=self.window).mean().loc[current_date]
        current_price = data["close"].loc[current_date]

        return current_price > ma
