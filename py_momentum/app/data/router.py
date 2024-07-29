from fastapi import APIRouter, Depends, Query
from typing import List
from datetime import datetime
from .models import StockDataWithIndicators
from .service import DataService
from loguru import logger

router = APIRouter()


@router.get("/data/{symbol}", response_model=List[StockDataWithIndicators])
async def get_stock_data(
    symbol: str,
    start_date: datetime = Query(..., description="Start date for stock data"),
    end_date: datetime = Query(..., description="End date for stock data"),
    data_service: DataService = Depends(),
):
    output = await data_service.get_stock_data(symbol, start_date, end_date)
    logger.info(f"Retrieved {len(output)} records for {symbol}")
    return output
