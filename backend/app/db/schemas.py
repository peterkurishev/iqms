from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class AgentBase(BaseModel):
    name: str = Field(..., example="Home Router")
    location: Optional[str] = Field(None, example="New York, USA")
    is_active: bool = Field(default=True)

class AgentCreate(AgentBase):
    """Схема для создания агента (без ID)"""
    pass

class AgentUpdate(BaseModel):
    """Схема для обновления агента"""
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

class AgentOut(AgentBase):
    """Схема для вывода данных агента"""
    id: str
    api_key: str
    created_at: datetime
    last_seen: Optional[datetime]

    class Config:
        orm_mode = True

class MeasurementBase(BaseModel):
    latency: float = Field(..., ge=0, example=25.4)
    download: float = Field(..., ge=0, example=78.2)
    upload: float = Field(..., ge=0, example=32.1)
    packet_loss: float = Field(..., ge=0, le=100, example=0.5)
    jitter: float = Field(..., ge=0, example=3.2)

class MeasurementCreate(MeasurementBase):
    """Схема для создания измерения"""
    agent_id: str = Field(..., example="agent-123")

class MeasurementOut(MeasurementCreate):
    """Схема для вывода измерения"""
    id: str
    timestamp: datetime
    metadata: dict = {}

    class Config:
        orm_mode = True
