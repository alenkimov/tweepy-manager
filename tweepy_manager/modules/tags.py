import questionary
from loguru import logger

from ..database import AsyncSessionmaker, Tag
from ..database.crud import ask_and_get_accounts, get_tags


async def add_tag():
    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(session, statuses=(
            "GOOD", "UNKOWN", "BAD_TOKEN", "LOCKED", "CONSENT_LOCKED", "SUSPENDED"))

    if not twitter_accounts:
        return

    # TODO           Выводить также: proxy, tags, status, id
    accounts_dict = {str(account): account for account in twitter_accounts}
    chosen_accounts = await questionary.checkbox(
        "Choose accounts:",
        choices=accounts_dict,
        validate=lambda choices: True if choices else "Select at least one account!"
    ).ask_async()

    tags = await get_tags(session)
    print(f"Existing tags: {', '.join(tags)}")
    tag = await questionary.text("Enter tag:").ask_async()
    tag = tag.strip()

    async with AsyncSessionmaker() as session:
        for choice in chosen_accounts:
            account = accounts_dict[choice]
            await session.merge(Tag(twitter_account_id=account.database_id, tag=tag))
        await session.commit()

    logger.info("Tags added successfully to selected accounts.")
