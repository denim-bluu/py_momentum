import pandas as pd


def get_snp500_symbols():
    snp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[
        0
    ]
    return snp500["Symbol"].tolist()


def calculate_atr(data: pd.DataFrame, window: int = 20) -> pd.Series:
    high_low = data["High"] - data["Low"]
    high_close = abs(data["High"] - data["Close"].shift())
    low_close = abs(data["Low"] - data["Close"].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=window).mean()
