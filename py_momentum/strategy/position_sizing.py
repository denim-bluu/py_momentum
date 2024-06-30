class PositionSizer:
    def __init__(self, basis_points: float = 10):
        self.basis_points = basis_points

    def calculate_position_size(self, account_value: float, atr: float) -> int:
        return int(account_value * (self.basis_points / 10000) / atr)
