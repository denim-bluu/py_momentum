from typing import Any

import numpy as np
from loguru import logger

from app.data.models import StockData

from app.strategy.models import (
    MarketRegime,
    OrderSignal,
    StockSignal,
    StrategyParameters,
)
from app.strategy.strategy_interface import Strategy
from app.strategy.utils import (
    calculate_atr,
    calculate_momentum_score,
    calculate_moving_average,
    has_recent_large_gap,
)


class MomentumStrategy(Strategy):
    def __init__(self, params: StrategyParameters):
        self.params = params

    def __repr__(self):
        return f"MomentumStrategy({self.params})"

    def generate_signals(
        self,
        stock_data: dict[str, StockData],
        index_data: StockData,
    ) -> list[StockSignal]:
        regime = self.detect_market_regime(index_data)
        logger.info(f"⛳️ Market regime is {regime.name}")
        if regime == MarketRegime.BEAR:
            logger.info("🐻 Market regime is bearish, no signals generated")
            return []

        signals = []
        for symbol, data in stock_data.items():
            signal = self._generate_signal(symbol, data)
            if signal:
                signals.append(signal)

        return self._sort_and_filter_signals(signals)

    def _generate_signal(
        self,
        symbol: str,
        stock_data: StockData,
    ) -> StockSignal | None:
        logger.info(f"🔍 Checking {symbol} for signals")
        if self._is_stock_disqualified(stock_data):
            logger.info(f"❌ {symbol} disqualified")
            return None
        logger.info(f"✅ {symbol} qualified")

        last_price = stock_data.data_points[-1].close
        momentum_score = calculate_momentum_score(
            prices=np.array([point.close for point in stock_data.data_points]),
            lookback=90,
        )
        risk_unit = self.calculate_risk(stock_data)
        logger.info(
            "🔖 {0} momentum score: {1:.2f}, risk unit: {2:.2f}".format(
                symbol,
                momentum_score,
                risk_unit,
            ),
        )

        return StockSignal(
            symbol=symbol,
            signal=OrderSignal.BUY,
            risk_unit=risk_unit,
            momentum_score=momentum_score,
            current_price=last_price,
        )

    def _is_stock_disqualified(self, stock_data: StockData) -> bool:
        if has_recent_large_gap(
            data_points=stock_data.data_points,
            lookback_period=90,
            threshold=0.15,
        ):
            logger.info("❌ Recent large gap detected")
            return True

        last_price = stock_data.data_points[-1].close
        moving_average = calculate_moving_average(
            tuple([p.close for p in stock_data.data_points]), 100
        )
        if last_price < moving_average:
            logger.info("❌ Price below 100-day moving average")
            return True

        momentum_score = calculate_momentum_score(
            prices=np.array([point.close for point in stock_data.data_points]),
            lookback=90,
        )
        if momentum_score < 0:
            logger.info("❌ Negative momentum score")
            return True

        return False

    def _sort_and_filter_signals(self, signals: list[StockSignal]) -> list[StockSignal]:
        logger.info("🔍 Sorting and filtering signals")
        sorted_signals = sorted(signals, key=lambda x: x.momentum_score, reverse=True)
        logger.info(f"🧹 Sorted signals: {[i.symbol for i in sorted_signals]}")
        self.params.top_percentage = 1.0
        top_count = int(len(sorted_signals) * self.params.top_percentage)
        logger.info(f"👑 Top {top_count} signals selected")
        return sorted_signals[:top_count]

    def calculate_risk(self, stock_data: StockData) -> float:
        atr = calculate_atr(stock_data, 20)
        if atr is None:
            return 0.0
        return atr * self.params.risk_factor

    def detect_market_regime(self, market_index_data: StockData) -> MarketRegime:
        if len(market_index_data.data_points) < self.params.market_regime_period:
            return MarketRegime.NEUTRAL

        current_price = market_index_data.data_points[-1].close
        ma200 = calculate_moving_average(
            tuple([p.close for p in market_index_data.data_points]),
            self.params.market_regime_period,
        )

        if current_price > ma200:
            return MarketRegime.BULL
        else:
            return MarketRegime.BEAR

    def get_parameters(self) -> dict[str, Any]:
        logger.info(f"📩 Getting strategy parameters: {self.params}")
        return self.params.model_dump()

    def set_parameters(self, params: dict[str, Any]) -> None:
        logger.info(f"Original params: {self.params}")
        logger.info(f"🔧 Setting strategy parameters: {params}")
        self.params = StrategyParameters(**params)
