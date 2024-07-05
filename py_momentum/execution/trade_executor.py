from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Tuple

import pandas as pd

from py_momentum.portfolio.portfolio import Portfolio


@dataclass
class Trade:
    date: date
    asset: str
    action: str
    quantity: float
    price: float
    commission: float


class TradeExecutor:
    def __init__(self, commission_rate: float = 0.001):
        self.commission_rate = commission_rate

    def execute_trades(
        self,
        current_date: date,
        target_positions: Dict[str, float],
        market_data: Dict[str, pd.DataFrame],
        portfolio: Portfolio,
    ) -> Tuple[Portfolio, List[Trade]]:
        trades: List[Trade] = []
        current_prices = {
            asset: data["close"].loc[current_date]
            for asset, data in market_data.items()
        }

        for asset, target_quantity in target_positions.items():
            if asset not in current_prices:
                continue  # Skip if we don't have market data for this asset

            current_quantity = portfolio.get_position(asset)
            price = current_prices[asset]

            if target_quantity > current_quantity:
                # Buy
                quantity_to_buy = target_quantity - current_quantity
                cost = quantity_to_buy * price
                commission = cost * self.commission_rate
                total_cost = cost + commission

                if total_cost <= portfolio.cash:
                    portfolio.cash -= total_cost
                    portfolio.add_position(asset, quantity_to_buy)
                    trades.append(
                        Trade(
                            date=current_date,
                            asset=asset,
                            action="BUY",
                            quantity=quantity_to_buy,
                            price=price,
                            commission=commission,
                        )
                    )
            elif target_quantity < current_quantity:
                # Sell
                quantity_to_sell = current_quantity - target_quantity
                revenue = quantity_to_sell * price
                commission = revenue * self.commission_rate
                total_revenue = revenue - commission

                portfolio.cash += total_revenue
                portfolio.add_position(asset, -quantity_to_sell)
                trades.append(
                    Trade(
                        date=current_date,
                        asset=asset,
                        action="SELL",
                        quantity=quantity_to_sell,
                        price=price,
                        commission=commission,
                    )
                )

        return portfolio, trades
