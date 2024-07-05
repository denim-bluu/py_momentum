from dagster import ConfigurableResource
import yfinance as yf
import pandas as pd
from datetime import datetime


class YahooFinanceResource(ConfigurableResource):
    api_wait_time: int = 1  # seconds to wait between API calls

    def fetch_stock_data(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        return yf.download(ticker, start=start_date, end=end_date)
