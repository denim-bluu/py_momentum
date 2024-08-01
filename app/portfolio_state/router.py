from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.portfolio_state.exceptions import PortfolioStateNotFoundError
from app.portfolio_state.models import (
    GetPortfolioStateRequest,
    GetPortfolioStateResponse,
    InitiatePortfolioStateRequest,
    UpdatePortfolioStateRequest,
    UpdatePortfolioStateResponse,
)
from app.portfolio_state.service import PortfolioStateService

router = APIRouter()


async def get_portfolio_state_service(db: Session = Depends(get_db)):
    service = PortfolioStateService(db)
    return service


@router.get("/get_latest_portfolio_state", response_model=GetPortfolioStateResponse)
async def get_latest_portfolio_state(
    portfolio_state_service: PortfolioStateService = Depends(
        get_portfolio_state_service
    ),
):
    try:
        portfolio_state = await portfolio_state_service.get_latest_portfolio_state()
        return GetPortfolioStateResponse(
            success=True,
            message="Latest portfolio state retrieved successfully",
            data=portfolio_state,
        )
    except PortfolioStateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_portfolio_state", response_model=GetPortfolioStateResponse)
async def get_portfolio_state(
    request: GetPortfolioStateRequest,
    portfolio_state_service: PortfolioStateService = Depends(
        get_portfolio_state_service
    ),
):
    try:
        portfolio_state = await portfolio_state_service.get_portfolio_state(request)
        return GetPortfolioStateResponse(
            success=True,
            message="Portfolio state retrieved successfully",
            data=portfolio_state,
        )
    except PortfolioStateNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update_portfolio_state", response_model=UpdatePortfolioStateResponse)
async def update_portfolio_state(
    request: UpdatePortfolioStateRequest,
    portfolio_state_service: PortfolioStateService = Depends(
        get_portfolio_state_service
    ),
):
    try:
        await portfolio_state_service.update_portfolio_state(request)
        return UpdatePortfolioStateResponse(
            success=True,
            message="Portfolio state updated successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initiate_portfolio_state", response_model=GetPortfolioStateResponse)
async def initiate_portfolio_state(
    request: InitiatePortfolioStateRequest,
    portfolio_state_service: PortfolioStateService = Depends(
        get_portfolio_state_service
    ),
):
    try:
        portfolio_state = await portfolio_state_service.initiate_portfolio_state(
            request
        )
        return GetPortfolioStateResponse(
            success=True,
            message="Portfolio state initiated successfully",
            data=portfolio_state,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
