import numpy as np
import yfinance as yf
import pandas as pd
from typing import List, Optional
from datetime import datetime
from .base import BaseDataRepository
from ..models import StockDataWithIndicators, TechnicalIndicators


class YahooFinanceRepository(BaseDataRepository):
    async def get_stock_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> List[StockDataWithIndicators]:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date, auto_adjust=True)

        # Calculate indicators
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["SMA_200"] = df["Close"].rolling(window=200).mean()
        df["RSI_14"] = self._calculate_rsi(df["Close"], window=14)

        return [
            StockDataWithIndicators(
                date=index.to_pydatetime(),  # type: ignore
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
                indicators=TechnicalIndicators(
                    sma_50=self._safe_float(row["SMA_50"]),
                    sma_200=self._safe_float(row["SMA_200"]),
                    rsi_14=self._safe_float(row["RSI_14"]),
                ),
            )
            for index, row in df.iterrows()
        ]

    def _calculate_rsi(self, data: pd.Series, window: int = 14) -> pd.Series:
        delta = data.diff()
        gain = (delta.where(delta.to_numpy() > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta.to_numpy() < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _safe_float(self, value: float) -> Optional[float]:
        return float(value) if not np.isnan(value) else None
