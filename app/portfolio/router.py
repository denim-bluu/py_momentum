from datetime import date

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.orm import Session

from app.data.router import get_data_service
from app.database import get_db
from app.portfolio_state.service import PortfolioStateService
from app.strategy.router import StrategyServiceProvider
from app.trade_execution.router import get_trade_execution_service

from .models import (
    PortfolioPerformance,
    PortfolioSummary,
    RebalanceRequest,
    RebalanceResponse,
)
from .service import PortfolioService

router = APIRouter()


def get_portfolio_service(db: Session = Depends(get_db)):
    strategy_service = StrategyServiceProvider().get_strategy_service(db)
    portfolio_state_service = PortfolioStateService(db)
    data_service = get_data_service(db)
    trade_execution_service = get_trade_execution_service(db)
    return PortfolioService(
        strategy_service=strategy_service,
        portfolio_state_service=portfolio_state_service,
        data_service=data_service,
        trade_execution_service=trade_execution_service,
    )


@router.post("/rebalance", response_model=RebalanceResponse)
async def rebalance_portfolio(
    request: RebalanceRequest,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    logger.info(f"Rebalancing portfolio: {request}")
    return await portfolio_service.rebalance(request)


@router.get("/summary/{date}", response_model=PortfolioSummary)
async def get_portfolio_summary(
    date: date, portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    return await portfolio_service.get_portfolio_summary(date)


@router.get("/performance", response_model=PortfolioPerformance)
async def get_portfolio_performance(
    start_date: date,
    end_date: date,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    return await portfolio_service.get_portfolio_performance(start_date, end_date)
