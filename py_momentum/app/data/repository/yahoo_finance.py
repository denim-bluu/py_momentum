import numpy as np
import yfinance as yf
import pandas as pd
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from .base import BaseDataRepository
from ..models import StockDataWithIndicators, TechnicalIndicators, StockDataDB
from ...cache import get_cache, set_cache
import json
import logging

logger = logging.getLogger(__name__)


class YahooFinanceRepository(BaseDataRepository):
    async def get_stock_data(
        self, symbol: str, start_date: date, end_date: date, db: Session
    ) -> List[StockDataWithIndicators]:
        cache_key = f"{symbol}_{start_date.isoformat()}_{end_date.isoformat()}"
        cached_data = get_cache(cache_key)

        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return [
                StockDataWithIndicators.model_validate_json(item)
                for item in json.loads(cached_data)  # type: ignore
            ]

        logger.info(f"Cache miss for {cache_key}, fetching from database")
        db_data = (
            db.query(StockDataDB)
            .filter(
                StockDataDB.symbol == symbol,
                StockDataDB.date >= start_date,
                StockDataDB.date <= end_date,
            )
            .all()
        )

        if db_data:
            result = [self._db_to_model(item) for item in db_data]
        else:
            logger.info(
                f"Data not found in database for {symbol}, fetching from Yahoo Finance"
            )
            result = await self._fetch_from_yahoo(symbol, start_date, end_date, db)

        set_cache(cache_key, json.dumps([item.model_dump_json() for item in result]))
        return result

    async def _fetch_from_yahoo(
        self, symbol: str, start_date: date, end_date: date, db: Session
    ) -> List[StockDataWithIndicators]:
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date, interval="1d")

            df = df.set_index(pd.to_datetime(df.index).date)
            df["SMA_50"] = df["Close"].rolling(window=50).mean()
            df["SMA_200"] = df["Close"].rolling(window=200).mean()
            df["RSI_14"] = self._calculate_rsi(df["Close"], window=14)

            result = []
            for index, row in df.iterrows():
                stock_data = StockDataWithIndicators(
                    date=index, # type: ignore
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
                result.append(stock_data)

                db_item = StockDataDB(
                    symbol=symbol,
                    date=stock_data.date,
                    open=stock_data.open,
                    high=stock_data.high,
                    low=stock_data.low,
                    close=stock_data.close,
                    volume=stock_data.volume,
                    sma_50=stock_data.indicators.sma_50,
                    sma_200=stock_data.indicators.sma_200,
                    rsi_14=stock_data.indicators.rsi_14,
                )
                db.add(db_item)

            db.commit()
            return result
        except Exception as e:
            logger.error(f"Error fetching data from Yahoo Finance: {str(e)}")
            raise

    def _safe_float(self, value: float) -> Optional[float]:
        return float(value) if not np.isnan(value) else None

    def _calculate_rsi(self, data: pd.Series, window: int = 14) -> pd.Series:
        delta = data.diff()
        gain = (delta.where(delta.to_numpy() > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta.to_numpy() < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _db_to_model(self, db_item: StockDataDB) -> StockDataWithIndicators:
        return StockDataWithIndicators(
            date=db_item.date,  # type: ignore
            open=db_item.open,  # type: ignore
            high=db_item.high,  # type: ignore
            low=db_item.low,  # type: ignore
            close=db_item.close,  # type: ignore
            volume=db_item.volume,  # type: ignore
            indicators=TechnicalIndicators(
                sma_50=db_item.sma_50,  # type: ignore
                sma_200=db_item.sma_200,  # type: ignore
                rsi_14=db_item.rsi_14,  # type: ignore
            ),
        )
