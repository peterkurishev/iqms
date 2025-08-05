from fastapi import FastAPI
from api.v1.api import api_router
from core.config import settings
from db.init_db import create_db_tables

app = FastAPI(
    title="Internet Monitor API",
    description="Distributed internet quality monitoring system",
    version="1.0.0"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup():
    await create_db_tables()

@app.get("/")
async def root():
    return {"message": "Internet Monitoring Service"}
