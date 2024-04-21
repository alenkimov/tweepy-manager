from asyncio import current_task
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, async_scoped_session

from common.sqlalchemy.alembic import AsyncAlembicUtils
from ..paths import DATABASE_FILEPATH, ALEMBIC_INI

DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_FILEPATH}"
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionmaker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
alembic_utils = AsyncAlembicUtils(async_engine, AsyncSessionmaker, ALEMBIC_INI)
# ScopedSession = async_scoped_session(AsyncSessionmaker, scopefunc=current_task)
