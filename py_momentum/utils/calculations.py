import numpy as np
import pandas as pd


def calculate_atr(df: pd.DataFrame, window: int = 20) -> pd.Series:
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Adj Close"].shift())
    low_close = np.abs(df["Low"] - df["Adj Close"].shift())
    ranges = pd.concat([high_low, pd.Series(high_close), pd.Series(low_close)], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(window=window).mean()
