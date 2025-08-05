from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import Agent

api_key_scheme = APIKeyHeader(name="X-API-KEY")

def generate_agent_key(length: int = 32) -> str:
    """Генерация случайного API ключа для агента"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def verify_agent_key(
    api_key: str,
    db: AsyncSession
) -> Agent:
    """Проверка валидности API ключа агента"""
    agent = await db.execute(
        select(Agent).where(Agent.api_key == api_key)
    )
    agent = agent.scalar_one_or_none()
    
    if not agent or not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    
    # Обновляем время последней активности
    agent.last_seen = datetime.utcnow()
    await db.commit()
    
    return agent
