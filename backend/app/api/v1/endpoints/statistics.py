# app/api/v1/endpoints/statistics.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.stats_service import calculate_stats, StatsService

router = APIRouter()

@router.get("/")
async def get_stats(
    agent_id: Optional[str] = Query(None),
    time_range: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статистики (общей или для конкретного агента)
    
    Параметры:
    - agent_id: ID агента (опционально)
    - time_range: диапазон времени (1h, 24h, 7d, 30d)
    """
    try:
        return await calculate_stats(db, agent_id, time_range)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calculating stats: {str(e)}"
        )

@router.get("/advanced")
async def get_advanced_stats(
    time_range: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    db: AsyncSession = Depends(get_db)
):
    """Расширенная статистика с использованием StatsService"""
    service = StatsService(db)
    try:
        if time_range == "30d":
            # Пример дополнительной логики
            weekly = await service.get_global_stats("7d")
            monthly = await service.get_global_stats("30d")
            return {
                "weekly": weekly,
                "monthly": monthly,
                "comparison": {
                    "latency_change": round(
                        (monthly["avg_latency"] - weekly["avg_latency"]) / weekly["avg_latency"] * 100, 2
                    )
                }
            }
        return await service.get_global_stats(time_range)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calculating advanced stats: {str(e)}"
        )
