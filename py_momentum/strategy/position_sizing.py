from py_momentum.strategy.interfaces import PositionSizer


class FixedRiskPositionSizer(PositionSizer):
    def __init__(self, risk_per_trade: float = 0.01):
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, account_value: float, atr: float) -> int:
        risk_amount = account_value * self.risk_per_trade
        return int(risk_amount / atr)
