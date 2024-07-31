from datetime import timedelta
from typing import Any

from loguru import logger

from app.data.models import BatchStockRequest
from app.data.service import DataService
from app.strategy.models import SignalRequest, SignalResponse, StrategyParameters
from app.strategy.momentum_strategy import MomentumStrategy


class StrategyService:
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        self.strategy = MomentumStrategy(StrategyParameters())

    async def generate_signals(self, request: SignalRequest) -> SignalResponse:
        start_date = request.date - timedelta(
            days=max(
                self.strategy.params.lookback_period,
                self.strategy.params.market_regime_period,
            )
        )
        logger.info(
            f"📶 Signal request for {request.symbols} from {start_date} to {request.date}"
        )
        index_data = await self.data_service.get_stock_data(
            symbol=request.market_index,
            start_date=start_date,
            end_date=request.date,
            interval=request.interval,
        )
        batch_request = BatchStockRequest(
            symbols=request.symbols,
            start_date=start_date,
            end_date=request.date,
            interval=request.interval,
        )
        batch_stock_data = await self.data_service.get_batch_stock_data(batch_request)
        signals = self.strategy.generate_signals(
            batch_stock_data.stock_data, index_data
        )

        return SignalResponse(signals=signals)

    def configure_strategy(self, params: dict[str, Any]) -> None:
        self.strategy.set_parameters(params)

    def get_strategy_parameters(self) -> dict[str, Any]:
        return self.strategy.get_parameters()
