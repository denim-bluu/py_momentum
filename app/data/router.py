from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from .models import BatchStockRequest, BatchStockResponse, StockData
from .service import DataService

router = APIRouter()


def get_data_service(db: Session = Depends(get_db)):
    return DataService(db)


@router.get("/stock/{symbol}", response_model=StockData)
async def get_stock_data(
    symbol: str,
    start_date: date,
    end_date: date,
    interval: str,
    data_service: DataService = Depends(get_data_service),
):
    try:
        return await data_service.get_stock_data(symbol, start_date, end_date, interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchStockResponse)
async def get_batch_stock_data(
    request: BatchStockRequest, data_service: DataService = Depends(get_data_service)
):
    try:
        return await data_service.get_batch_stock_data(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
