import random

import questionary

from ..database.models import TwitterAccount
from ..database.crud import ask_and_get_accounts
from ..database import AsyncSessionmaker
from ..twitter import TwitterClient
from .process_utils import process_twitter_accounts, ask_and_request_users


async def follow():
    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(session, statuses=("GOOD", ))

    if not twitter_accounts:
        return

    users = await ask_and_request_users(random.choice(twitter_accounts))

    if not await questionary.confirm("Resume?").ask_async():
        return

    async def _follow(twitter_account: TwitterAccount):
        async with TwitterClient(twitter_account) as twitter_client:  # type: TwitterClient
            for user in users:
                await twitter_client.follow_and_save(user)

    await process_twitter_accounts(_follow, twitter_accounts)
