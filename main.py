from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.data.router import router as data_router
from app.database import Base, engine
from app.portfolio_state.router import router as portfolio_state_router
from app.strategy.router import router as strategy_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    logger.info("Application started")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(data_router, prefix="/api/v1/data", tags=["data"])
app.include_router(strategy_router, prefix="/api/v1/strategy", tags=["strategy"])
app.include_router(
    portfolio_state_router, prefix="/api/v1/portfolio_state", tags=["portfolio_state"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
