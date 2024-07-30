from contextlib import asynccontextmanager
from fastapi import FastAPI
from py_momentum.app.data.router import router as data_router
from py_momentum.app.strategy.router import router as strategy_router
from py_momentum.app.database import engine, Base
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    logger.info("Application started")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(data_router, prefix="/api/v1/data", tags=["data"])
app.include_router(strategy_router, prefix="/api/v1/strategy", tags=["strategy"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
