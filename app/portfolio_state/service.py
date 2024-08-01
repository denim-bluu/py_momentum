from loguru import logger
from sqlalchemy.orm import Session

from .exceptions import PortfolioStateNotFoundError
from .models import (
    GetPortfolioStateRequest,
    InitiatePortfolioStateRequest,
    PortfolioState,
    UpdatePortfolioStateRequest,
)
from .repository.base import BaseDataRepository
from .repository.database import DatabaseRepository


class PortfolioStateService:
    def __init__(self, db: Session):
        self.db_repo: BaseDataRepository = DatabaseRepository(db)

    async def get_latest_portfolio_state(self) -> PortfolioState:
        logger.info("🔎 Querying latest portfolio state")
        try:
            return await self.db_repo.get_latest_portfolio_state()
        except PortfolioStateNotFoundError as e:
            logger.error(f"Portfolio state not found: {str(e)}")
            logger.warning("Check if the portfolio state has been initiated")
            raise
        except Exception as e:
            logger.error(f"Error retrieving latest portfolio state: {str(e)}")
            raise

    async def get_portfolio_state(
        self, req: GetPortfolioStateRequest
    ) -> PortfolioState:
        logger.info(f"🔎 Querying portfolio state for {req.date}")
        try:
            return await self.db_repo.get_portfolio_state(req.date)
        except PortfolioStateNotFoundError as e:
            logger.error(f"Portfolio state not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving portfolio state: {str(e)}")
            raise

    async def update_portfolio_state(self, req: UpdatePortfolioStateRequest) -> None:
        logger.info("🔎 Updating portfolio state")
        try:
            await self.db_repo.update_portfolio_state(
                req.positions, req.cash_balance, req.total_value
            )
        except Exception as e:
            logger.error(f"Error updating portfolio state: {str(e)}")
            raise

    async def initiate_portfolio_state(
        self, req: InitiatePortfolioStateRequest
    ) -> PortfolioState:
        logger.info(
            f"🔎 Initiating portfolio state with cash balance: {req.initial_cash_balance}"
        )
        try:
            return await self.db_repo.initiate_portfolio_state(req.initial_cash_balance)
        except Exception as e:
            logger.error(f"Error initiating portfolio state: {str(e)}")
            raise
