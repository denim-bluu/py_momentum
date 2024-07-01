from abc import ABC, abstractmethod

import pandas as pd

from py_momentum.utils.calculations import calculate_atr


class DataProcessor(ABC):
    @abstractmethod
    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        pass


class MovingAverageProcessor(DataProcessor):
    def __init__(self, window: int):
        self.window = window

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data[f"MA{self.window}"] = data["Adj Close"].rolling(window=self.window).mean()
        return data


class ATRProcessor(DataProcessor):
    def __init__(self, window: int = 14):
        self.window = window

    def process(self, data: pd.DataFrame) -> pd.DataFrame:
        data["ATR"] = calculate_atr(data, self.window)
        return data
