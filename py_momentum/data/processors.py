from typing import Dict

import pandas as pd
from .utils import calculate_atr


def process_data(data: Dict[str, pd.DataFrame], **kwargs) -> Dict[str, pd.DataFrame]:
    processed_data = {}
    for ticker, df in data.items():
        df["MA_100"] = df["Adj Close"].rolling(window=100).mean()
        df["ATR_20"] = calculate_atr(df, window=20)
        processed_data[ticker] = df
    return processed_data
