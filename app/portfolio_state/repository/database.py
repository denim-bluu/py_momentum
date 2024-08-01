from datetime import date, datetime

from loguru import logger
from sqlalchemy.orm import Session

from app.portfolio_state.exceptions import PortfolioStateNotFoundError
from app.portfolio_state.models import PortfolioState, PortfolioStateDB, Position

from .base import BaseDataRepository


class DatabaseRepository(BaseDataRepository):
    def __init__(self, db: Session):
        self.db = db

    async def get_latest_portfolio_state(self) -> PortfolioState:
        latest_state = (
            self.db.query(PortfolioStateDB)
            .order_by(PortfolioStateDB.date.desc(), PortfolioStateDB.timestamp.desc())
            .first()
        )

        if not latest_state:
            raise PortfolioStateNotFoundError("latest")

        return PortfolioState(
            date=latest_state.date,  # type: ignore
            timestamp=latest_state.timestamp,  # type: ignore
            positions=[Position(**pos) for pos in latest_state.positions],  # type: ignore
            cash_balance=latest_state.cash_balance,  # type: ignore
            total_value=latest_state.total_value,  # type: ignore
        )

    async def get_portfolio_state(self, date: date) -> PortfolioState:
        portfolio_state = (
            self.db.query(PortfolioStateDB)
            .filter(PortfolioStateDB.date == date)
            .order_by(PortfolioStateDB.timestamp.desc())
            .first()
        )

        if not portfolio_state:
            logger.error(f"❌ Portfolio state not found for {date}")
            raise PortfolioStateNotFoundError(date)

        return PortfolioState(
            date=portfolio_state.date,  # type: ignore
            timestamp=portfolio_state.timestamp,  # type: ignore
            positions=[Position(**pos) for pos in portfolio_state.positions],  # type: ignore
            cash_balance=portfolio_state.cash_balance,  # type: ignore
            total_value=portfolio_state.total_value,  # type: ignore
        )

    async def update_portfolio_state(
        self, positions: list[Position], cash_balance: float, total_value: float
    ) -> None:
        today = date.today()
        now = datetime.now()

        db_item = PortfolioStateDB(
            date=today,
            timestamp=now,
            positions=[pos.model_dump() for pos in positions],
            cash_balance=cash_balance,
            total_value=total_value,
        )
        self.db.add(db_item)
        self.db.commit()
        logger.info(f"✅ Portfolio state updated for {today} at {now}")

    async def initiate_portfolio_state(
        self, initial_cash_balance: float
    ) -> PortfolioState:
        logger.info("🔄 Dropping and recreating portfolio state table")
        PortfolioStateDB.__table__.drop(self.db.bind)
        PortfolioStateDB.__table__.create(self.db.bind)

        db_item = PortfolioStateDB(
            positions=[],
            cash_balance=initial_cash_balance,
            total_value=initial_cash_balance,
        )
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)

        now = datetime.now()
        logger.info(
            f"✨ Portfolio state initiated at {now} with cash balance {initial_cash_balance}"
        )

        return PortfolioState(
            date=db_item.date,  # type: ignore
            timestamp=db_item.timestamp,  # type: ignore
            positions=[],
            cash_balance=db_item.cash_balance,  # type: ignore
            total_value=db_item.total_value,  # type: ignore
        )
