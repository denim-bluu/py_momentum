from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from .data.router import router as data_router
from .database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Application started")
    yield


app = FastAPI()

app.include_router(data_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Application started")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
