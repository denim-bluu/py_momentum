from py_momentum.strategy.interfaces import (
    MarketFilter,
    PositionSizer,
    RankingStrategy,
    RebalanceStrategy,
)
from py_momentum.strategy.filters import MovingAverageFilter
from py_momentum.strategy.position_sizing import FixedRiskPositionSizer
from py_momentum.strategy.ranking import MomentumRankingStrategy
from py_momentum.strategy.rebalancing import ThresholdRebalanceStrategy


class StrategyFactory:
    @staticmethod
    def create_ranking_strategy(config: dict) -> RankingStrategy:
        if config["type"] == "momentum":
            return MomentumRankingStrategy(
                momentum_window=config["momentum_window"],
                ma_window_filter=config["ma_window"],
                max_gap_filter=config["max_gap"],
                pct_rank=config["pct_rank"],
            )
        raise ValueError(f"Unknown ranking strategy type: {config['type']}")

    @staticmethod
    def create_position_sizer(config: dict) -> PositionSizer:
        if config["type"] == "fixed_risk":
            return FixedRiskPositionSizer(risk_per_trade=config["risk_per_trade"])
        raise ValueError(f"Unknown position sizer type: {config['type']}")

    @staticmethod
    def create_market_filter(config: dict) -> MarketFilter:
        if config["type"] == "moving_average":
            return MovingAverageFilter(ma_window=config["ma_window"])
        raise ValueError(f"Unknown market filter type: {config['type']}")

    @staticmethod
    def create_rebalance_strategy(config: dict) -> RebalanceStrategy:
        if config["type"] == "threshold":
            return ThresholdRebalanceStrategy(threshold=config["threshold"])
        raise ValueError(f"Unknown rebalance strategy type: {config['type']}")
