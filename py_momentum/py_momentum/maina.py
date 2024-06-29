import yfinance as yf
import numpy as np
from scipy import stats
import pandas as pd


df = yf.download("GOOGL", start="2010-01-01", end="2015-01-01")
log_prices = np.log(df["Adj Close"])
window = 90


def slope(y):
    x = np.arange(len(y))
    return stats.linregress(x, y)[0]


def r_squared(y):
    x = np.arange(len(y))
    return stats.linregress(x, y)[2] ** 2


slopes = log_prices.rolling(window=window).apply(slope, raw=True)
r_squared_values = log_prices.rolling(window=window).apply(r_squared, raw=True)

rolling_stats = pd.DataFrame(
    {
        "price": df["Adj Close"],
        "slope": slopes,
        "r_squared": r_squared_values,
        "score": slopes * r_squared_values,
        "annualized_return": np.exp(slopes * 252) - 1,
    }
)
