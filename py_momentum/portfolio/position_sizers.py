class ATRPositionSizer:
    def __init__(self, risk_per_trade: float = 0.001):  # 0.1% risk per trade
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(
        self, account_value: float, price: float, atr: float
    ) -> float:
        risk_amount = account_value * self.risk_per_trade
        shares = risk_amount / atr
        return shares
