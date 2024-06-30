import pandas as pd


class IndexFilter:
    def __init__(self, ma_window: int = 200):
        self.ma_window = ma_window

    def is_bullish(self, index_data: pd.DataFrame) -> bool:
        if len(index_data) < self.ma_window:
            return False
        current_price = index_data["Adj Close"].iloc[-1]
        ma = index_data["Adj Close"].rolling(window=self.ma_window).mean().iloc[-1]
        return current_price > ma
