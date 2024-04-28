import random
from typing import Iterable

import twitter
from loguru import logger

from ..database import TwitterAccount, AsyncSessionmaker
from ..database.crud import ask_and_get_accounts
from ..twitter import TwitterClient
from ._process_utils import process_twitter_accounts, ask_and_request_users, sleep_between_actions


async def _follow(twitter_account: TwitterAccount, users: Iterable[twitter.User]):
    async with TwitterClient(twitter_account) as twitter_client:  # type: TwitterClient
        for user in users:
            await twitter_client.follow(user.id)
            logger.success(f"@{twitter_account.username} (id={twitter_account.user.id})"
                           f" Followed: @{user.username} (id={user.id})")
            await sleep_between_actions(twitter_account)


async def follow():
    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(session, statuses=("GOOD", ))

    if not twitter_accounts:
        return

    users = await ask_and_request_users(random.choice(twitter_accounts))

    async def _custom_follow(twitter_account: TwitterAccount):
        return await _follow(twitter_account, users)

    await process_twitter_accounts(_custom_follow, twitter_accounts)
