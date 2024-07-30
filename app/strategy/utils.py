from typing import List

import numpy as np
import pandas as pd
from app.data.models import StockData, StockDataPoint
from sklearn.linear_model import LinearRegression


def calculate_momentum_score(prices: np.ndarray, lookback: int = 90) -> float:
    prices = prices[-lookback:]
    log_returns = np.diff(np.log(prices))
    model = LinearRegression().fit(
        np.arange(len(log_returns)).reshape(-1, 1), log_returns
    )
    r_value = model.score(np.arange(len(log_returns)).reshape(-1, 1), log_returns)
    slope = model.coef_[0]
    return slope * (r_value**2)


def calculate_moving_average(data_points: List[StockDataPoint], period: int) -> float:
    prices = [point.close for point in data_points[-period:]]
    return float(np.mean(prices))


def calculate_atr(stock_data: StockData, period: int = 14) -> float:
    high = [point.high for point in stock_data.data_points[-period - 1 :]]
    low = [point.low for point in stock_data.data_points[-period - 1 :]]
    close = [point.close for point in stock_data.data_points[-period - 1 :]]

    tr1 = pd.Series(high) - pd.Series(low)
    tr2 = abs(pd.Series(high) - pd.Series(close).shift())
    tr3 = abs(pd.Series(low) - pd.Series(close).shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean().iloc[-1]
    return atr


def has_recent_large_gap(
    data_points: List[StockDataPoint], lookback_period: int, threshold: float
) -> bool:
    for i in range(1, min(lookback_period, len(data_points))):
        prev_close = data_points[-i - 1].close
        current_open = data_points[-i].open
        if abs(current_open - prev_close) / prev_close > threshold:
            return True
    return False
