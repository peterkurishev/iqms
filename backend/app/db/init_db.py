# app/db/init_db.py
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db.session import engine, Base
from core.logger import logger

async def create_db_tables():
    """Асинхронное создание таблиц с обработкой ошибок"""
    try:
        async with engine.begin() as conn:
            # Создание стандартных таблиц
            await conn.run_sync(Base.metadata.create_all)
            
            # Установка расширений TimescaleDB
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE"))
            
            # Преобразование таблицы measurements в гипертаблицу TimescaleDB
            await conn.execute(text("""
                SELECT create_hypertable(
                    'measurements', 
                    'timestamp',
                    if_not_exists => TRUE,
                    chunk_time_interval => INTERVAL '1 week'
                )
            """))
            
            logger.info("Database tables created successfully")
            
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise
