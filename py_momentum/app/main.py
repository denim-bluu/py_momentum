from fastapi import FastAPI
from .data.router import router as data_router

app = FastAPI()

app.include_router(data_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
