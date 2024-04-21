import questionary

from .database import alembic_utils


async def update_database_or_quite():
    current_revision = await alembic_utils.get_current_revision()
    latest_revision = alembic_utils.get_latest_revision()
    if current_revision != latest_revision:
        print(
            f"Current revision is {current_revision}, but the latest revision is {latest_revision}."
            f" An update is required."
        )
        should_upgrade = await questionary.confirm(
            "Do you want to upgrade the database to the latest revision?"
        ).ask_async()

        if not should_upgrade:
            quit()

        await alembic_utils.upgrade()
