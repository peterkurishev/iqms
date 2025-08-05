# app/services/stats_service.py
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Measurement

async def calculate_stats(
    db: AsyncSession,
    agent_id: Optional[str] = None,
    time_range: str = "24h"
) -> Dict:
    """
    Основная функция для расчета статистики
    (сохраняем для обратной совместимости)
    """
    service = StatsService(db)
    if agent_id:
        return await service.get_agent_stats(agent_id, time_range)
    return await service.get_global_stats(time_range)

class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_agent_stats(
        self,
        agent_id: str,
        time_range: str = "24h"
    ) -> Dict:
        """Получение статистики для конкретного агента"""
        end_time = datetime.utcnow()
        start_time = self._calculate_start_time(end_time, time_range)

        result = await self.db.execute(
            select(
                func.avg(Measurement.latency).label("avg_latency"),
                func.avg(Measurement.download).label("avg_download"),
                func.avg(Measurement.upload).label("avg_upload"),
                func.avg(Measurement.packet_loss).label("avg_packet_loss"),
                func.count().label("measurement_count")
            ).where(
                and_(
                    Measurement.agent_id == agent_id,
                    Measurement.timestamp >= start_time,
                    Measurement.timestamp <= end_time
                )
            )
        )

        stats = result.first()
        return {
            "agent_id": agent_id,
            "time_range": time_range,
            "avg_latency": round(stats.avg_latency or 0, 2),
            "avg_download": round(stats.avg_download or 0, 2),
            "avg_upload": round(stats.avg_upload or 0, 2),
            "avg_packet_loss": round(stats.avg_packet_loss or 0, 2),
            "measurement_count": stats.measurement_count or 0,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

    async def get_global_stats(
        self,
        time_range: str = "24h"
    ) -> Dict:
        """Глобальная статистика по всем агентам"""
        end_time = datetime.utcnow()
        start_time = self._calculate_start_time(end_time, time_range)

        # Основные метрики
        result = await self.db.execute(
            select(
                func.count(func.distinct(Measurement.agent_id)).label("active_agents"),
                func.avg(Measurement.latency).label("avg_latency"),
                func.max(Measurement.download).label("max_download"),
                func.min(Measurement.download).label("min_download")
            ).where(
                and_(
                    Measurement.timestamp >= start_time,
                    Measurement.timestamp <= end_time
                )
            )
        )

        stats = result.first()
        return {
            "time_range": time_range,
            "active_agents": stats.active_agents or 0,
            "avg_latency": round(stats.avg_latency or 0, 2),
            "max_download": round(stats.max_download or 0, 2),
            "min_download": round(stats.min_download or 0, 2),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

    def _calculate_start_time(self, end_time: datetime, time_range: str) -> datetime:
        """Вычисление начального времени для диапазона"""
        ranges = {
            "1h": timedelta(hours=1),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        return end_time - ranges.get(time_range, timedelta(days=1))
