import pandas as pd


def calculate_atr(data: pd.DataFrame, window: int = 20) -> pd.Series:
    high_low = data["High"] - data["Low"]
    high_close = abs(data["High"] - data["Adj Close"].shift())
    low_close = abs(data["Low"] - data["Adj Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=window).mean()