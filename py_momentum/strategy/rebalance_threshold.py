from typing import Protocol


class RebalanceStrategy(Protocol):
    def should_rebalance(self, current_shares: int, target_shares: int) -> bool: ...


class ThresholdRebalanceStrategy:
    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold

    def should_rebalance(self, current_shares: int, target_shares: int) -> bool:
        if current_shares == 0:
            return target_shares > 0
        else:
            return abs(current_shares - target_shares) / current_shares > self.threshold
