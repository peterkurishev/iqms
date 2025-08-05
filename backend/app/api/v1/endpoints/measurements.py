from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.session import get_db
from db.models import Measurement
from db.schemas import MeasurementCreate, MeasurementOut
from services.agent_service import verify_agent_key

router = APIRouter()

#@router.post("/", response_model=MeasurementOut, status_code=201)
async def create_measurement(
    measurement: MeasurementCreate,
    db: AsyncSession = Depends(get_db),
    agent_id: str = Depends(verify_agent_key)
):
    db_measurement = Measurement(
        agent_id=agent_id,
        **measurement.dict()
    )
    
    db.add(db_measurement)
    await db.commit()
    await db.refresh(db_measurement)
    
    return MeasurementOut.from_orm(db_measurement)

#@router.get("/{measurement_id}", response_model=MeasurementOut)
async def get_measurement(
    measurement_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Measurement).where(Measurement.id == measurement_id)
    )
    measurement = result.scalar_one_or_none()
    
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    return MeasurementOut.from_orm(measurement)
