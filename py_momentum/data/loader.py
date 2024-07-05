from datetime import datetime
from typing import Dict, List

import pandas as pd
from sqlalchemy import create_engine, inspect
from loguru import logger


class DBDataLoader:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.inspector = inspect(self.engine)
        self.logger = logger.bind(context="DBDataLoader")

    def load_data(
        self, tickers: List[str], start_date: datetime, end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        data = {}
        for ticker in tickers:
            try:
                if not self.inspector.has_table(ticker):
                    self.logger.warning(
                        f"Table for ticker {ticker} does not exist in the database. Skipping."
                    )
                    continue

                query = f"""
                SELECT * FROM "{ticker}"
                WHERE Date >= '{start_date.date()}' AND Date <= '{end_date.date()}'
                ORDER BY Date
                """
                df = pd.read_sql(
                    query, self.engine, index_col="Date", parse_dates=["Date"]
                )

                if df.empty:
                    self.logger.warning(
                        f"No data found for ticker {ticker} in the specified date range. Skipping."
                    )
                    continue

                data[ticker] = df
                self.logger.info(f"Successfully loaded data for ticker {ticker}")
            except Exception as e:
                self.logger.error(f"Error loading data for ticker {ticker}: {str(e)}")
                continue

        if not data:
            self.logger.error("No data could be loaded for any ticker.")
            raise ValueError(
                "No data available for the specified tickers and date range."
            )

        return data
