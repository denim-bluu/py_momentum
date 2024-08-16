from abc import ABC, abstractmethod
from datetime import date

from app.portfolio_state.models import PortfolioState, Position


class BaseDataRepository(ABC):
    @abstractmethod
    async def get_latest_portfolio_state(self) -> PortfolioState:
        pass

    @abstractmethod
    async def get_portfolio_state(self, date: date) -> PortfolioState:
        pass

    @abstractmethod
    async def update_portfolio_state(
        self,
        date: date,
        positions: list[Position],
        cash_balance: float,
        total_value: float,
    ) -> None:
        pass

    @abstractmethod
    async def initiate_portfolio_state(
        self, initial_cash_balance: float
    ) -> PortfolioState:
        pass
