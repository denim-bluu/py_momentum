from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import date
from sqlalchemy.orm import Session
from .models import StockDataWithIndicators
from .service import DataService
from ..database import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/data/{symbol}", response_model=List[StockDataWithIndicators])
async def get_stock_data(
    symbol: str,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    data_service: DataService = Depends(),
):
    try:
        return await data_service.get_stock_data(symbol, start_date, end_date, db)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
