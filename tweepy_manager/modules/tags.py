import questionary
from loguru import logger

from ..database.models import Tag
from ..database.crud import ask_and_get_accounts, get_tags, choose_accounts
from ..database import AsyncSessionmaker


async def add_tag():
    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(
            session,
            statuses=(
                "GOOD",
                "UNKNOWN",
                "BAD_TOKEN",
                "LOCKED",
                "CONSENT_LOCKED",
                "SUSPENDED",
            ),
        )

    if not twitter_accounts:
        return

    twitter_accounts = await choose_accounts(twitter_accounts)

    tags = await get_tags(session)
    print(f"Existing tags: {', '.join(tags)}")
    tag = await questionary.text("Enter tag:").ask_async()
    tag = tag.strip()

    async with AsyncSessionmaker() as session:
        for account in twitter_accounts:
            await session.merge(Tag(twitter_account_id=account.database_id, tag=tag))
        await session.commit()

    logger.info("Tags added successfully to selected accounts.")
