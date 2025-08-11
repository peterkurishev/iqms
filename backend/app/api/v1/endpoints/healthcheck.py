from fastapi import APIRouter, Depends
from sqlalchemy import text
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db

router = APIRouter()

@router.get("/")
async def health():
    return {"status": "ok"}

@router.get("/db")
async def db_health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"database": "healthy"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"database": "unavailable", "error": str(e)}
        )
