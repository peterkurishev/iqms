from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import Agent
from db.schemas import AgentCreate, AgentOut
from services.agent_service import generate_agent_key

router = APIRouter()
admin_key_scheme = APIKeyHeader(name="X-ADMIN-KEY")

@router.post("/", response_model=AgentOut)
async def register_agent(
    agent: AgentCreate,
    db: AsyncSession = Depends(get_db),
    admin_key: str = Depends(admin_key_scheme)
):
    if admin_key != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    agent_key = generate_agent_key()
    db_agent = await Agent.create(
        db,
        name=agent.name,
        location=agent.location,
        api_key=agent_key
    )
    return {**db_agent.dict(), "api_key": agent_key}

@router.get("/{agent_id}", response_model=AgentOut)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(admin_key_scheme)
):
    agent = await Agent.get(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
