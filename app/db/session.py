from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency to get db session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
