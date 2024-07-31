from datetime import date

from sqlalchemy.orm import Session

from app.data.models import BatchStockResponse, StockData, StockDataDB, StockDataPoint

from .base import BaseDataRepository


class DatabaseRepository(BaseDataRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_stock_data(
        self, symbol: str, start_date: date, end_date: date, interval: str
    ) -> StockData:
        db_data = (
            self.db.query(StockDataDB)
            .filter(
                StockDataDB.symbol == symbol,
                StockDataDB.date >= start_date,
                StockDataDB.date <= end_date,
            )
            .all()
        )
        data_points = [
            StockDataPoint(
                date=row.date,  # type: ignore
                open=row.open,  # type: ignore
                high=row.high,  # type: ignore
                low=row.low,  # type: ignore
                close=row.close,  # type: ignore
                volume=row.volume,  # type: ignore
            )
            for row in db_data
        ]

        return StockData(symbol=symbol, data_points=data_points)

    async def get_batch_stock_data(
        self, symbols: list[str], start_date: date, end_date: date, interval: str
    ) -> BatchStockResponse:
        stock_data = {}
        errors = {}

        for symbol in symbols:
            try:
                stock_data[symbol] = await self.get_stock_data(
                    symbol, start_date, end_date, interval
                )
            except Exception as e:
                errors[symbol] = str(e)

        return BatchStockResponse(stock_data=stock_data, errors=errors)

    async def save_stock_data(self, stock_data: StockData) -> None:
        for point in stock_data.data_points:
            db_item = StockDataDB(
                symbol=stock_data.symbol,
                date=point.date,
                open=point.open,
                high=point.high,
                low=point.low,
                close=point.close,
                volume=point.volume,
            )
            self.db.add(db_item)
        self.db.commit()
