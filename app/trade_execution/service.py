from loguru import logger

from app.portfolio_state.models import Position, UpdatePortfolioStateRequest
from app.portfolio_state.service import PortfolioStateService

from .exceptions import InsufficientFundsError, InvalidOrderError, OrderNotFoundError
from .models import ExecuteOrdersRequest, Order, OrderStatus, OrderType


class TradeExecutionService:
    def __init__(self, portfolio_state_service: PortfolioStateService):
        self.portfolio_state_service = portfolio_state_service
        self.orders: list[Order] = []

    async def create_order(
        self, symbol: str, quantity: float, order_type: OrderType
    ) -> Order:
        portfolio_state = (
            await self.portfolio_state_service.get_latest_portfolio_state()
        )

        if order_type == OrderType.MARKET:
            # Check if there's enough cash for a buy order
            if quantity > 0:
                position = next(
                    (p for p in portfolio_state.positions if p.symbol == symbol), None
                )
                if (
                    position is None
                    or position.price * quantity > portfolio_state.cash_balance
                ):
                    raise InsufficientFundsError(
                        "Insufficient funds to place this order"
                    )
            # Check if there's enough quantity for a sell order
            elif quantity < 0:
                position = next(
                    (p for p in portfolio_state.positions if p.symbol == symbol), None
                )
                if position is None or abs(quantity) > position.quantity:
                    raise InvalidOrderError(
                        "Insufficient quantity to place this sell order"
                    )

        order = Order(symbol=symbol, quantity=quantity, order_type=order_type)
        self.orders.append(order)
        logger.info(f"Created order: {order}")
        return order

    async def execute_orders(self, request: ExecuteOrdersRequest) -> list[Order]:
        executed_orders = []
        # Simulate market orders execution, immediately fill orders at current market price
        for order in self.orders:
            if (
                order.status == OrderStatus.PENDING
                and order.symbol in request.market_data
            ):
                order.status = OrderStatus.FILLED
                order.filled_at = request.date
                order.filled_price = request.market_data[order.symbol]
                executed_orders.append(order)
                await self._update_portfolio_state(order)

        return executed_orders

    async def get_open_orders(self) -> list[Order]:
        return [order for order in self.orders if order.status == OrderStatus.PENDING]

    async def cancel_order(self, order_id: int) -> Order:
        order = next((o for o in self.orders if o.id == order_id), None)
        if order is None:
            raise OrderNotFoundError(f"Order with id {order_id} not found")
        if order.status != OrderStatus.PENDING:
            raise InvalidOrderError(f"Cannot cancel order with status {order.status}")

        order.status = OrderStatus.CANCELLED
        logger.info(f"Cancelled order: {order}")
        return order

    async def _update_portfolio_state(self, executed_order: Order):
        portfolio_state = (
            await self.portfolio_state_service.get_latest_portfolio_state()
        )

        if executed_order.filled_price is None:
            raise InvalidOrderError("Order has not been filled")
        # Update cash balance
        cash_change = -executed_order.quantity * executed_order.filled_price
        new_cash_balance = portfolio_state.cash_balance + cash_change

        # Update positions
        new_positions = portfolio_state.positions.copy()
        position = next(
            (p for p in new_positions if p.symbol == executed_order.symbol), None
        )
        if position:
            position.quantity += executed_order.quantity
            position.value = position.quantity * executed_order.filled_price
            if position.quantity == 0:
                new_positions.remove(position)
        elif executed_order.quantity > 0:
            new_positions.append(
                Position(
                    symbol=executed_order.symbol,
                    quantity=executed_order.quantity,
                    price=executed_order.filled_price,
                    value=executed_order.quantity * executed_order.filled_price,
                )
            )

        # Calculate new total value
        new_total_value = new_cash_balance + sum(p.value for p in new_positions)

        await self.portfolio_state_service.update_portfolio_state(
            UpdatePortfolioStateRequest(
                date=portfolio_state.date,
                positions=new_positions,
                cash_balance=new_cash_balance,
                total_value=new_total_value,
            )
        )
