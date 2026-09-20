from fastapi import FastAPI
import uvicorn
from core.config import settings
from app.api_router import api_router
from core.logger import setup_logging
from fastapi.middleware.cors import CORSMiddleware

setup_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host=settings.run.host, port=settings.run.port, reload=True
    )
