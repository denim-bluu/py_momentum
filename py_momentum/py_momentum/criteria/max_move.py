import pandas as pd


class MaxMoveCriteria:
    def __init__(self, days: int = 90, threshold: float = 0.15):
        self.days = days
        self.threshold = threshold

    def apply(self, df: pd.DataFrame) -> bool:
        if len(df) < self.days:
            return False
        returns = df["Adj Close"].pct_change()
        return abs(returns.tail(self.days)).max() <= self.threshold
