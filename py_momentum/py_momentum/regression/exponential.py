import pandas as pd
import numpy as np
from scipy import stats


class ExponentialRegressionStrategy:
    def calculate_regression(self, df: pd.DataFrame, window: int) -> pd.DataFrame:
        log_prices = pd.Series(np.log(df["Adj Close"]))

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
                "slope": slopes,
                "r_squared": r_squared_values,
                "score": slopes * r_squared_values,
                "annualized_return": np.exp(slopes * 252) - 1,
            }
        )

        return rolling_stats
