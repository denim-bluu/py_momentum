import json
from datetime import date

from loguru import logger
from sqlalchemy.orm import Session

from app.cache import get_cache, set_cache

from .models import BatchStockRequest, BatchStockResponse, StockData
from .repository.base import BaseDataRepository
from .repository.database import DatabaseRepository
from .repository.yahoo_finance import YahooFinanceRepository


class DataService:
    def __init__(self, db: Session):
        self.yahoo_repo: BaseDataRepository = YahooFinanceRepository()
        self.db_repo: BaseDataRepository = DatabaseRepository(db)

    async def get_stock_data(
        self, symbol: str, start_date: date, end_date: date, interval: str
    ) -> StockData:
        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}"
        cached_data = get_cache(cache_key)

        logger.info(f"🔎 Checking cache for {cache_key}")
        if cached_data:
            logger.info(f"✅ Cache hit for {cache_key}")
            return StockData.model_validate(json.loads(cached_data))  # type: ignore
        logger.info(f"❌ Cache miss for {cache_key}")

        logger.info(f"🔎 Querying data for {symbol} from {start_date} to {end_date}")
        db_data = await self.db_repo.get_stock_data(
            symbol, start_date, end_date, interval
        )

        if not db_data.data_points:
            logger.info(f"❌ Data not found in database for {symbol}")
            logger.info(f"🔎 Fetching data from Yahoo Finance for {symbol}")
            yahoo_data = await self.yahoo_repo.get_stock_data(
                symbol, start_date, end_date, interval
            )
            logger.info(f"📥 Saving data for {symbol} to database")
            await self.db_repo.save_stock_data(yahoo_data)
            db_data = yahoo_data

        set_cache(cache_key, db_data.model_dump_json())
        return db_data

    async def get_batch_stock_data(
        self, request: BatchStockRequest
    ) -> BatchStockResponse:
        stock_data = {}
        errors = {}

        for symbol in request.symbols:
            try:
                stock_data[symbol] = await self.get_stock_data(
                    symbol, request.start_date, request.end_date, request.interval
                )
            except Exception as e:
                errors[symbol] = str(e)

        return BatchStockResponse(stock_data=stock_data, errors=errors)
