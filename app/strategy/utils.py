from typing import List, Optional
import numpy as np
from app.data.models import StockData, StockDataPoint
from sklearn.linear_model import LinearRegression
from functools import lru_cache


def calculate_momentum_score(prices: np.ndarray, lookback: int = 90) -> float:
    if len(prices) < lookback:
        raise ValueError(
            f"Insufficient data points. Expected at least {lookback}, got {len(prices)}"
        )

    prices = prices[-lookback:]
    log_returns = np.diff(np.log(prices))
    x = np.arange(len(log_returns)).reshape(-1, 1)

    model = LinearRegression().fit(x, log_returns)
    r_value = model.score(x, log_returns)
    slope = model.coef_[0]

    return float(slope * (r_value**2))


@lru_cache(maxsize=128)
def calculate_moving_average(prices: tuple[float, ...], period: int) -> float:
    if len(prices) < period:
        raise ValueError(
            f"Insufficient data points. Expected at least {period}, got {len(prices)}"
        )

    return float(np.mean(prices[-period:]))


def calculate_atr(stock_data: StockData, period: int = 14) -> Optional[float]:
    if len(stock_data.data_points) < period + 1:
        return None

    high = np.array([point.high for point in stock_data.data_points[-period - 1 :]])
    low = np.array([point.low for point in stock_data.data_points[-period - 1 :]])
    close = np.array([point.close for point in stock_data.data_points[-period - 1 :]])

    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])

    tr = np.max(np.stack([tr1, tr2, tr3]), axis=0)
    atr = np.mean(tr)

    return float(atr)


def has_recent_large_gap(
    data_points: List[StockDataPoint], lookback_period: int, threshold: float
) -> np.bool:
    if len(data_points) < 2:
        return np.bool(False)

    closes = np.array([point.close for point in data_points[-lookback_period - 1 : -1]])
    opens = np.array([point.open for point in data_points[-lookback_period:]])

    gaps = np.abs(opens - closes) / closes
    return np.any(gaps > threshold)
