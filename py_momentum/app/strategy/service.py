from typing import Any, Dict

from py_momentum.app.data.models import BatchStockRequest
from .strategy_interface import Strategy
from .momentum_strategy import MomentumStrategy
from .models import SignalRequest, SignalResponse
from ..data.service import DataService


class StrategyService:
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        self.strategies: Dict[str, Strategy] = {"momentum": MomentumStrategy()}

    async def generate_signals(self, request: SignalRequest) -> SignalResponse:
        index_data = await self.data_service.get_stock_data(
            request.market_index, request.start_date, request.end_date, request.interval
        )
        batch_request = BatchStockRequest(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval,
        )
        batch_stock_data = await self.data_service.get_batch_stock_data(batch_request)

        strategy = self.strategies["momentum"]
        signals = strategy.generate_signals(batch_stock_data.stock_data, index_data)

        return SignalResponse(signals=signals)

    def configure_strategy(self, strategy_name: str, params: Dict[str, Any]) -> None:
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")

        self.strategies[strategy_name].set_parameters(params)

    def get_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy {strategy_name} not found")

        return self.strategies[strategy_name].get_parameters()
