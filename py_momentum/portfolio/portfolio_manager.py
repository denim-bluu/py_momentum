from datetime import date
from typing import Dict

import pandas as pd

from .interfaces import PositionSizer
from .portfolio import Portfolio


class PortfolioManager:
    def __init__(self, position_sizer: PositionSizer):
        self.position_sizer = position_sizer

    def calculate_target_positions(
        self,
        current_date: date,
        signals: Dict[str, str],
        market_data: Dict[str, pd.DataFrame],
        portfolio: Portfolio,
    ) -> Dict[str, float]:
        target_positions = {}
        current_prices = {
            asset: data["close"].loc[current_date]
            for asset, data in market_data.items()
        }
        account_value = portfolio.calculate_total_value(current_prices)

        for asset, signal in signals.items():
            if signal == "BUY":
                price = current_prices[asset]
                atr = market_data[asset]["atr"].loc[current_date]
                target_positions[asset] = self.position_sizer.calculate_position_size(
                    account_value, price, atr
                )
            elif signal == "SELL":
                target_positions[asset] = 0
            else:
                target_positions[asset] = portfolio.get_position(asset)

        return target_positions

    def rebalance_portfolio(
        self,
        current_date: date,
        market_data: Dict[str, pd.DataFrame],
        portfolio: Portfolio,
    ) -> Dict[str, float]:
        rebalanced_positions = {}
        current_prices = {
            asset: data["close"].loc[current_date]
            for asset, data in market_data.items()
        }
        account_value = portfolio.calculate_total_value(current_prices)

        for asset in portfolio.get_all_positions():
            if asset not in market_data:
                continue
            price = current_prices[asset]
            atr = market_data[asset]["atr"].loc[current_date]
            rebalanced_positions[asset] = self.position_sizer.calculate_position_size(
                account_value, price, atr
            )

        return rebalanced_positions
