from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings
import os

settings = get_settings()

db_url = settings.DATABASE_URL

# Ensure async driver for sqlite
if db_url.startswith("sqlite:///") and "+aiosqlite" not in db_url:
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Fallback: convert postgresql to sqlite for local dev
if db_url.startswith("postgresql"):
    db_url = db_url.replace("postgresql+asyncpg://", "sqlite+aiosqlite://")
    db_url = db_url.replace("postgresql://", "sqlite+aiosqlite://")
    if "/" in db_url.split("//")[-1]:
        db_path = db_url.split("//")[-1].split("/")[-1]
        db_url = f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', db_path)}"

engine = create_async_engine(
    db_url,
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
