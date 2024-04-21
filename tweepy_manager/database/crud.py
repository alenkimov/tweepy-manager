from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import twitter

from .models import TwitterAccount


async def get_accounts(
        session: AsyncSession,
        statuses: Iterable[twitter.AccountStatus] = None
) -> list[TwitterAccount]:
    query = select(TwitterAccount).options(
        joinedload(TwitterAccount.proxy),
        joinedload(TwitterAccount.user),
    )
    accounts = list(await session.scalars(query))
    logger.info(f"Из базы данных запрошены аккаунты со следующими статусами: {statuses}")
    return accounts
