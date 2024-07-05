from typing import Dict


class Portfolio:
    def __init__(self, initial_cash: float):
        self._cash = initial_cash
        self._positions: Dict[str, float] = {}  # asset: quantity

    @property
    def cash(self) -> float:
        return self._cash

    @cash.setter
    def cash(self, value: float):
        if value < 0:
            raise ValueError("Cash cannot be negative")
        self._cash = value

    def add_position(self, asset: str, quantity: float):
        if asset in self._positions:
            self._positions[asset] += quantity
        else:
            self._positions[asset] = quantity

        if self._positions[asset] == 0:
            del self._positions[asset]

    def get_position(self, asset: str) -> float:
        return self._positions.get(asset, 0)

    def get_all_positions(self) -> Dict[str, float]:
        return self._positions.copy()

    def calculate_total_value(self, current_prices: Dict[str, float]) -> float:
        return self._cash + sum(
            self._positions[asset] * current_prices[asset]
            for asset in self._positions
            if asset in current_prices
        )

    def calculate_asset_allocation(
        self, current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        total_value = self.calculate_total_value(current_prices)
        allocation = {
            asset: (quantity * current_prices[asset]) / total_value
            for asset, quantity in self._positions.items()
            if asset in current_prices
        }
        allocation["cash"] = self._cash / total_value
        return allocation

    def to_dict(self) -> Dict[str, float]:
        portfolio_dict = self._positions.copy()
        portfolio_dict["cash"] = self._cash
        return portfolio_dict

    @classmethod
    def from_dict(cls, portfolio_dict: Dict[str, float]) -> "Portfolio":
        portfolio = cls(portfolio_dict.pop("cash", 0))
        for asset, quantity in portfolio_dict.items():
            portfolio.add_position(asset, quantity)
        return portfolio
