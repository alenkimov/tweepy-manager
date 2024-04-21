"""
Перед использованием в файл env нужно внести следующие изменения:

```python
def run_migrations_online() -> None:
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)
```

Подробнее об этом:
https://github.com/sqlalchemy/alembic/discussions/991
"""
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.exc import NoSuchTableError


def get_current_revision(connection):
    alembic_context = MigrationContext.configure(connection)
    return alembic_context.get_current_revision()


class AlembicUtils:
    """Helper for a SQLAlchemy and Alembic-powered database."""

    def __init__(
        self,
        engine,
        sessionmaker,
        alembic_ini_filepath: str | Path = "alembic.ini",
    ):
        self.engine = engine
        self.sessionmaker = sessionmaker
        self.alembic_ini_filepath = Path(alembic_ini_filepath)
        self.alembic_cfg = AlembicConfig(self.alembic_ini_filepath)

    def get_current_revision(self, connection=None):
        """Get the current alembic database revision."""
        if connection is None:
            with self.engine.begin() as connection:
                return get_current_revision(connection)
        else:
            return get_current_revision(connection)

    def get_latest_revision(self):
        """Get the most up-to-date alembic database revision available."""
        script_dir = ScriptDirectory.from_config(self.alembic_cfg)
        return script_dir.get_current_head()

    def upgrade(self, revision: str = "head"):
        """Upgrade the database schema."""
        command.upgrade(self.alembic_cfg, revision)

    def sync(self):
        """Create or update the database schema."""
        if self.get_current_revision() != self.get_latest_revision():
            self.upgrade()


class AsyncAlembicUtils(AlembicUtils):
    """Helper for a SQLAlchemy and Alembic-powered database, asynchronous version."""

    async def get_current_revision(self, connection=None):
        try:
            if connection is None:
                async with self.engine.begin() as connection:
                    return await connection.run_sync(super().get_current_revision)
            else:
                return await connection.run_sync(super().get_current_revision)
        except NoSuchTableError:
            return None

    async def upgrade(self, revision: str = "head"):
        def _run_upgrade(connection):
            alembic_cfg = AlembicConfig(self.alembic_ini_filepath)
            alembic_cfg.attributes["connection"] = connection
            command.upgrade(alembic_cfg, revision)

        async with self.engine.begin() as connection:
            await connection.run_sync(_run_upgrade)

    async def sync(self):
        if await self.get_current_revision() != self.get_latest_revision():
            await self.upgrade()
