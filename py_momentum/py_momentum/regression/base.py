from typing import Protocol
import pandas as pd


class RegressionStrategy(Protocol):
    def calculate_regression(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        raise NotImplementedError
