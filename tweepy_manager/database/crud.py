import questionary
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import twitter

from .models import TwitterAccount, Tag
from ..config import CONFIG


# UNTAGGED = "untagged"


async def get_accounts(
        session: AsyncSession,
        statuses: tuple[twitter.AccountStatus] = None,
        tags: tuple[str] = None,
        # untagged: bool = False,
) -> list[TwitterAccount]:
    query = select(TwitterAccount).options(
        joinedload(TwitterAccount.proxy),
        joinedload(TwitterAccount.user),
    )

    if statuses:
        query = query.filter(TwitterAccount.status.in_(statuses))

    if tags:
        query = query.join(TwitterAccount.tags).filter(Tag.tag.in_(tags))

    accounts = list(await session.scalars(query))

    accounts_count = len(accounts)

    level = "INFO"
    if accounts_count == 0:
        level = "WARNING"

    log_message = f"Из базы данных запрошено {accounts_count} аккаунтов"
    if statuses:
        log_message += f"\n\tЗапрашиваемые статусы: {statuses}"
    if tags:
        log_message += f"\n\tЗапрашиваемые теги: {tags}"
    # if untagged:
    #     log_message += "\n\tЗапрошены аккаунты без тегов включительно"
    logger.log(level, log_message)

    if CONFIG.REQUESTS.REQUIRE_PROXY:
        if accounts_without_proxy := [account for account in accounts if not account.proxy]:
            logger.warning(f"{len(accounts_without_proxy)} accounts have no proxy!")

        return [account for account in accounts if account.proxy]

    return accounts


async def get_tags(session: AsyncSession) -> list[str]:
    return list(await session.scalars(select(Tag.tag).distinct()))


async def ask_and_get_accounts(
        session: AsyncSession,
        statuses: tuple[twitter.AccountStatus] = ("UNKNOWN", "GOOD"),
) -> list[TwitterAccount]:
    tags = await get_tags(session)

    selected_tags = await questionary.checkbox(
        "Choose tags:",
        choices=tags,
        validate=lambda choices: True if choices else "Select at least one tag!"
    ).ask_async()

    if len(statuses) > 1:
        statuses = await questionary.checkbox(
            "Choose statuses",
            choices=statuses,
            validate=lambda choices: True if choices else "Select at least one status!"
        ).ask_async()

    return await get_accounts(session, statuses=statuses, tags=selected_tags)
