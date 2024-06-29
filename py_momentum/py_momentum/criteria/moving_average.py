import pandas as pd


class MovingAverageCriteria:
    def __init__(self, window: int = 100):
        self.window = window

    def apply(self, df: pd.DataFrame) -> bool:
        if len(df) < self.window:
            return False
        ma = df["Adj Close"].rolling(window=self.window).mean()
        return df["Adj Close"].iloc[-1] > ma.iloc[-1]
