from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Включить для отладки SQL-запросов
    future=True
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def create_db_tables():
    """Создает все таблицы в базе данных"""
    async with engine.begin() as conn:
        # Для production используйте миграции Alembic вместо этого!
        await conn.run_sync(Base.metadata.create_all)
        
    # Опционально: создание индексов
    async with async_session() as session:
        await session.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_agent_id 
            ON measurements (agent_id);
        """)
        await session.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_timestamp 
            ON measurements (timestamp);
        """)
        await session.commit()
