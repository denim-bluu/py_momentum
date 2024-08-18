from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.portfolio_state.service import PortfolioStateService

from .exceptions import InsufficientFundsError, InvalidOrderError, OrderNotFoundError
from .models import CreateOrderRequest, ExecuteOrdersRequest, OrderResponse
from .service import TradeExecutionService

router = APIRouter()


def get_trade_execution_service(db: Session = Depends(get_db)):
    portfolio_state_service = PortfolioStateService(db)
    return TradeExecutionService(portfolio_state_service)


@router.post("/orders", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    trade_execution_service: TradeExecutionService = Depends(
        get_trade_execution_service
    ),
):
    try:
        order = await trade_execution_service.create_order(
            request.symbol, request.quantity, request.order_type
        )
        return OrderResponse(order=order, message="Order created successfully")
    except (InsufficientFundsError, InvalidOrderError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/execute", response_model=list[OrderResponse])
async def execute_orders(
    request: ExecuteOrdersRequest,
    trade_execution_service: TradeExecutionService = Depends(
        get_trade_execution_service
    ),
):
    executed_orders = await trade_execution_service.execute_orders(request)
    return [
        OrderResponse(order=order, message="Order executed successfully")
        for order in executed_orders
    ]


@router.get("/orders/open", response_model=list[OrderResponse])
async def get_open_orders(
    trade_execution_service: TradeExecutionService = Depends(
        get_trade_execution_service
    ),
):
    open_orders = await trade_execution_service.get_open_orders()
    return [OrderResponse(order=order, message="Open order") for order in open_orders]


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    trade_execution_service: TradeExecutionService = Depends(
        get_trade_execution_service
    ),
):
    try:
        cancelled_order = await trade_execution_service.cancel_order(order_id)
        return OrderResponse(
            order=cancelled_order, message="Order cancelled successfully"
        )
    except (OrderNotFoundError, InvalidOrderError) as e:
        raise HTTPException(status_code=400, detail=str(e))
