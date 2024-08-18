from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException
from loguru import logger

from app.data.models import BatchStockRequest
from app.data.service import DataService
from app.portfolio.models import (
    Order,
    OrderType,
    PortfolioPerformance,
    PortfolioSummary,
    RebalanceRequest,
    RebalanceResponse,
)
from app.portfolio_state.models import (
    GetPortfolioStateRequest,
    PortfolioState,
    Position,
)
from app.portfolio_state.service import PortfolioStateService
from app.strategy.models import SignalRequest, SignalType, StockSignal
from app.strategy.service import StrategyService
from app.trade_execution.models import ExecuteOrdersRequest
from app.trade_execution.service import TradeExecutionService


class PortfolioService:
    def __init__(
        self,
        strategy_service: StrategyService,
        portfolio_state_service: PortfolioStateService,
        trade_execution_service: TradeExecutionService,
        data_service: DataService,
    ):
        self.strategy_service = strategy_service
        self.portfolio_state_service = portfolio_state_service
        self.trade_execution_service = trade_execution_service
        self.data_service = data_service

    async def rebalance(self, request: RebalanceRequest) -> RebalanceResponse:
        try:
            logger.info(f"Starting portfolio rebalance for date: {request.date}")

            # Get current portfolio state
            current_state = (
                await self.portfolio_state_service.get_latest_portfolio_state()
            )

            # Get market data
            market_data = await self.data_service.get_batch_stock_data(
                BatchStockRequest(
                    symbols=request.symbols,
                    start_date=request.date,
                    end_date=request.date,
                    interval=request.interval,
                )
            )

            # Generate signals

            signals = await self.strategy_service.generate_signals(
                SignalRequest(
                    symbols=request.symbols,
                    date=datetime.combine(request.date, datetime.min.time()),
                    interval=request.interval,
                    market_index=request.market_index,
                )
            )

            # Determine required trades
            trades = self._determine_trades(current_state, signals.signals)

            # Execute trades
            for trade in trades:
                await self.trade_execution_service.create_order(
                    trade.symbol, trade.quantity, OrderType.MARKET
                )

            executed_orders = (  # noqa: F841
                await self.trade_execution_service.execute_orders(
                    ExecuteOrdersRequest(
                        date=datetime.combine(request.date, datetime.min.time()),
                        market_data={
                            symbol: data.data_points[-1].close
                            for symbol, data in market_data.stock_data.items()
                        },
                    )
                )
            )

            # Update portfolio state
            new_state = (  # noqa: F841
                await self.portfolio_state_service.get_latest_portfolio_state()
            )

            logger.info("Rebalance completed successfully")
            return RebalanceResponse(
                success=True, message="Portfolio rebalanced successfully"
            )
        except Exception as e:
            logger.error(f"Error during rebalance: {str(e)}")
            return RebalanceResponse(
                success=False, message=f"Rebalance failed: {str(e)}"
            )

    def _determine_trades(
        self, current_state: PortfolioState, signals: list[StockSignal]
    ) -> list[Order]:
        trades = []
        for signal in signals:
            if signal.signal == "BUY":
                current_position = next(
                    (p for p in current_state.positions if p.symbol == signal.symbol),
                    None,
                )
                current_quantity = current_position.quantity if current_position else 0
                target_quantity = int(
                    signal.risk_unit * current_state.total_value / signal.current_price
                )
                trade_quantity = target_quantity - current_quantity
                if trade_quantity != 0:
                    trades.append(
                        Order(
                            symbol=signal.symbol,
                            quantity=trade_quantity,
                            order_type=OrderType.MARKET,
                            price=signal.current_price,
                        )
                    )
        return trades

    async def check_and_rebalance(self, date: datetime):
        # This method would be called periodically or by the backtesting service
        rebalance_request = RebalanceRequest(
            date=date,
            symbols=[
                p.symbol
                for p in (
                    await self.portfolio_state_service.get_latest_portfolio_state()
                ).positions
            ],
            interval="1d",
            market_index="^GSPC",  # S&P 500 index
        )
        await self.rebalance(rebalance_request)

    async def calculate_target_positions(
        self, signals: list[StockSignal], current_portfolio_state: PortfolioState
    ) -> dict[str, Position]:
        total_value = Decimal(str(current_portfolio_state.total_value))
        target_positions: dict[str, Position] = {}

        for signal in signals:
            if signal.signal == SignalType.BUY:
                allocation = Decimal(str(signal.risk_unit)) * total_value
                quantity = int(allocation / Decimal(str(signal.current_price)))
                target_positions[signal.symbol] = Position(
                    symbol=signal.symbol,
                    quantity=quantity,
                    price=float(signal.current_price),
                    value=float(quantity * Decimal(str(signal.current_price))),
                )

        return target_positions

    async def generate_orders(
        self,
        current_positions: dict[str, Position],
        target_positions: dict[str, Position],
    ) -> list[Order]:
        orders: list[Order] = []

        # Sell positions that are not in target_positions
        for symbol, position in current_positions.items():
            if symbol not in target_positions:
                orders.append(
                    Order(
                        symbol=symbol,
                        order_type=OrderType.MARKET,
                        quantity=-position.quantity,
                        price=position.price,
                    )
                )

        for symbol, position in target_positions.items():
            if symbol not in current_positions:
                # Buy new positions
                orders.append(
                    Order(
                        symbol=symbol,
                        order_type=OrderType.MARKET,
                        quantity=position.quantity,
                        price=position.price,
                    )
                )
            else:
                # Rebalance existing positions
                current_position = current_positions[symbol]
                order_quantity = position.quantity - current_position.quantity
                if order_quantity != 0:
                    orders.append(
                        Order(
                            symbol=symbol,
                            order_type=OrderType.MARKET,
                            quantity=order_quantity,
                            price=position.price,
                        )
                    )

        return orders

    async def execute_orders(
        self, current_state: PortfolioState, orders: list[Order]
    ) -> PortfolioState:
        new_positions = {i.symbol: i for i in current_state.positions.copy()}
        cash_balance = current_state.cash_balance

        for order in orders:
            if order.symbol not in new_positions:
                new_positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=0,
                    price=order.price,
                    value=0.0,
                )

            position = new_positions[order.symbol]
            order_value = order.quantity * order.price

            position.quantity += order.quantity
            position.price = order.price  # Assuming we update to the latest price
            position.value = position.quantity * position.price

            cash_balance -= order_value

            if position.quantity == 0:
                del new_positions[order.symbol]

        total_value = cash_balance + sum(p.value for p in new_positions.values())
        return PortfolioState(
            date=current_state.date,
            timestamp=current_state.timestamp,
            positions=list(new_positions.values()),
            cash_balance=float(cash_balance),
            total_value=float(total_value),
        )

    async def get_portfolio_summary(self, date: date) -> PortfolioSummary:
        logger.info(f"Getting portfolio summary for date: {date}")
        get_portfolio_req = GetPortfolioStateRequest(date=date)
        portfolio_state = await self.portfolio_state_service.get_portfolio_state(
            get_portfolio_req
        )

        return PortfolioSummary(
            date=portfolio_state.date,
            total_value=portfolio_state.total_value,
            cash_balance=portfolio_state.cash_balance,
            positions={p.symbol: p.quantity for p in portfolio_state.positions},
            allocation={
                p.symbol: p.value / portfolio_state.total_value
                for p in portfolio_state.positions
            },
        )

    async def get_portfolio_performance(
        self, start_date: date, end_date: date
    ) -> PortfolioPerformance:
        try:
            get_portfolio_req_start = GetPortfolioStateRequest(date=start_date)
            get_portfolio_req_end = GetPortfolioStateRequest(date=end_date)
            start_state = await self.portfolio_state_service.get_portfolio_state(
                get_portfolio_req_start
            )
            end_state = await self.portfolio_state_service.get_portfolio_state(
                get_portfolio_req_end
            )

            total_return = (
                end_state.total_value - start_state.total_value
            ) / start_state.total_value
            days = (end_date - start_date).days
            annualized_return = (1 + total_return) ** (365 / days) - 1

            # Note: Sharpe ratio and max drawdown calculations would require daily data
            sharpe_ratio = None
            max_drawdown = 0

            return PortfolioPerformance(
                start_date=start_date,
                end_date=end_date,
                total_return=total_return,
                annualized_return=annualized_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
            )
        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to calculate portfolio performance: {str(e)}",
            )
