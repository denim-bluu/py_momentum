import pandas as pd
import numpy as np

class ATRMetric:
    def __init__(self, window: int = 14):
        self.window = window

    def calculate(self, df: pd.DataFrame) -> float:
        high_low = df["High"] - df["Low"]
        high_close = np.abs(df["High"] - df["Close"].shift())
        low_close = np.abs(df["Low"] - df["Close"].shift())
        ranges = pd.concat(
            [pd.Series(high_low), pd.Series(high_close), pd.Series(low_close)], axis=1
        )
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window=self.window).mean().iloc[-1]
        return atr

    def get_name(self) -> str:
        return f"ATR ({self.window}-day)"