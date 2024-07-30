from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from app.data.router import get_data_service
from app.database import get_db
from sqlalchemy.orm import Session

from .models import SignalRequest, SignalResponse, StrategyParameters
from .service import StrategyService

router = APIRouter()


def get_strategy_service(db: Session = Depends(get_db)):
    data_service = get_data_service(db)
    return StrategyService(data_service)


@router.post("/generate_signals", response_model=SignalResponse)
async def generate_signals(
    request: SignalRequest,
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    return await strategy_service.generate_signals(request)


@router.post("/configure_strategy/{strategy_name}")
async def configure_strategy(
    strategy_name: str,
    params: StrategyParameters,
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    try:
        strategy_service.configure_strategy(strategy_name, params.model_dump())
        return {"message": "Strategy configured successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/strategy_parameters/{strategy_name}", response_model=Dict[str, Any])
async def get_strategy_parameters(
    strategy_name: str,
    strategy_service: StrategyService = Depends(get_strategy_service),
):
    try:
        return strategy_service.get_strategy_parameters(strategy_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
