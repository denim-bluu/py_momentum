class ATRRiskModel:
    def __init__(self, risk_factor: float = 1.0):
        self.risk_factor = risk_factor

    def calculate_position_risk(self, price: float, atr: float) -> float:
        return atr * self.risk_factor
