# app/api/v1/api.py
from fastapi import APIRouter
from .endpoints import (
    agents,
    measurements,
    healthcheck,
    statistics
)
from core.config import settings

api_router = APIRouter()

# Включение всех роутеров API
api_router.include_router(
    healthcheck.router,
    prefix="/health",
    tags=["Healthcheck"]
)
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["Agents Management"]
)
api_router.include_router(
    measurements.router,
    prefix="/measurements",
    tags=["Measurements"]
)
api_router.include_router(
    statistics.router,
    prefix="/stats",
    tags=["Statistics"]
)
