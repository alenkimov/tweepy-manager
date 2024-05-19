from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import URL

from common.sqlalchemy.alembic import AsyncAlembicUtils
from ..paths import BASE_DIR
from ..config import CONFIG


ALEMBIC_INI = BASE_DIR / "alembic.ini"
DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    database=CONFIG.DATABASE.DATABASE_NAME,
    username=CONFIG.DATABASE.USERNAME,
    password=CONFIG.DATABASE.PASSWORD,
    host=CONFIG.DATABASE.HOST,
    port=CONFIG.DATABASE.PORT,
)
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionmaker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
alembic_utils = AsyncAlembicUtils(async_engine, AsyncSessionmaker, ALEMBIC_INI)
