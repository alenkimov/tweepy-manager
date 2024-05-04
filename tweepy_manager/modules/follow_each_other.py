import random

import twitter
from loguru import logger

from ..database.models import TwitterAccount, TwitterUser
from ..database.crud import ask_and_get_accounts, choose_accounts
from ..database import AsyncSessionmaker
from ..twitter import TwitterClient
from common.ask import ask_int
from .process_utils import process_account


async def _follow(twitter_account: TwitterAccount, user: twitter.User | TwitterUser):
    async with TwitterClient(twitter_account) as twitter_client:  # type: TwitterClient
        await twitter_client.follow_and_save(user)


async def follow_each_other():
    print(f"Эта функция подписывает выбранные аккаунты друг на другу"
          f" для достижения определенного количества подписчиков.")

    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(session, statuses=("GOOD",))

    while True:
        max_followers = await ask_int("Enter max followers:", min=0, max=len(twitter_accounts))
        accounts_dict = {f"{account}\nFollowers: {account.user.followers_count if account.user else 'UNKNOWN USER'}": account
                         for account in twitter_accounts
                         if not account.user
                         or account.user.followers_count is None
                         or account.user.followers_count < max_followers}

        if not accounts_dict:
            logger.warning(f"No accounts. Change max followers count!")
        else:
            break

    twitter_accounts_to_follow = await choose_accounts(accounts_dict)

    if not twitter_accounts:
        return

    while twitter_accounts_to_follow:
        twitter_account = twitter_accounts_to_follow.pop(0)

        async def try_follow(twitter_account):
            async with TwitterClient(twitter_account) as twitter_client:  # type: TwitterClient
                await twitter_client.update_account_info()
                logger.info(f"@{twitter_account.username} (id={twitter_account.twitter_id})"
                            f" Followers count: {twitter_client.account.followers_count}")

                if twitter_client.account.followers_count < max_followers:
                    await _follow(random.choice(twitter_accounts), twitter_account.user)
                    twitter_accounts_to_follow.append(twitter_account)

        await process_account(try_follow, twitter_account)
