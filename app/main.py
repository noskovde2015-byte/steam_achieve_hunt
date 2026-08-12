from fastapi import FastAPI
import uvicorn
from core.config import settings
from app.api_router import api_router


app = FastAPI()
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app",host=settings.run.host, port=settings.run.port, reload=True)