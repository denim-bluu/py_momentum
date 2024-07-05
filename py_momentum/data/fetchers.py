from datetime import timedelta
from typing import List, Dict

import pandas as pd
import yfinance as yf


def fetch_data(tickers: List[str], **kwargs) -> Dict[str, pd.DataFrame]:
    execution_date = kwargs["execution_date"]
    end_date = execution_date
    start_date = end_date - timedelta(days=1)  # Fetch only one day of data

    data = {}
    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date)
        if not df.empty:
            data[ticker] = df

    return data
