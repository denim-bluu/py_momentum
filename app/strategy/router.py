from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.router import get_data_service
from app.database import get_db

from .models import SignalRequest, SignalResponse, StrategyParameters
from .service import StrategyService

router = APIRouter()


class StrategyServiceProvider:
    def __init__(self):
        self.strategy_service = None

    def get_strategy_service(self, db: Session = Depends(get_db)):
        if self.strategy_service is None:
            data_service = get_data_service(db)
            self.strategy_service = StrategyService(data_service)
        return self.strategy_service


strategy_service_provider = StrategyServiceProvider()


@router.post("/generate_signals", response_model=SignalResponse)
async def generate_signals(
    request: SignalRequest,
    strategy_service: StrategyService = Depends(
        strategy_service_provider.get_strategy_service
    ),
):
    return await strategy_service.generate_signals(request)


@router.post("/configure_strategy")
async def configure_strategy(
    params: StrategyParameters,
    strategy_service: StrategyService = Depends(
        strategy_service_provider.get_strategy_service
    ),
):
    try:
        strategy_service.configure_strategy(params.model_dump())
        return {
            "message": f"Strategy configured successfully: {strategy_service.strategy.params}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/strategy_parameters", response_model=dict[str, Any])
async def get_strategy_parameters(
    strategy_service: StrategyService = Depends(
        strategy_service_provider.get_strategy_service
    ),
):
    try:
        return strategy_service.get_strategy_parameters()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
