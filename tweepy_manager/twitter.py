import asyncio
import random

from loguru import logger
from common.sqlalchemy.crud import update_or_create
from sqlalchemy import select
import twitter

from .config import CONFIG
from .database import (
    AsyncSessionmaker,
    TwitterAccount,
    TwitterUser,
    Following,
    Tweet,
)


async def sleep_between_actions(twitter_account: TwitterAccount):
    sleep_time = random.randint(*CONFIG.CONCURRENCY.DELAY_BETWEEN_ACTIONS)
    if not sleep_time:
        return

    logger.info(f"@{twitter_account.username} (id={twitter_account.user.id}) Sleep time: {sleep_time} seconds")
    await asyncio.sleep(sleep_time)


class TwitterClient(twitter.Client):
    """
    - Принимает модель TwitterAccount
    - Сохраняет данные о TwitterAccount и TwitterAccount.user в бд по завершении работы
    """

    def __init__(self, twitter_account: TwitterAccount):
        self.db_account = twitter_account

        account = twitter.Account(
            auth_token=self.db_account.auth_token,
            ct0=self.db_account.ct0,
            username=self.db_account.username,
            password=self.db_account.password,
            email=self.db_account.email,
            totp_secret=self.db_account.totp_secret,
            backup_code=self.db_account.backup_code,
            status=self.db_account.status,
            id=self.db_account.twitter_id,
        )
        super().__init__(
            account,
            proxy=twitter_account.proxy.better_proxy(),
            max_unlock_attempts=CONFIG.TWITTER.MAX_UNLOCK_ATTEMPTS,
            capsolver_api_key=CONFIG.CAPTCHA.CAPSOLVER_API_KEY,
            update_account_info_on_startup=False,
        )

    async def __aexit__(self, *args):
        await self.close()

    async def close(self):
        async with AsyncSessionmaker() as session:
            twitter_account_data = self.account.model_dump(
                include={"id", "auth_token", "ct0", "username", "password", "email", "totp_secret", "backup_code",
                         "status"}
            )
            session.add(self.db_account)
            # По сути это как update из Django ORM
            for key, value in twitter_account_data.items():
                setattr(self.db_account, key, value)

            twitter_user_data = self.account.model_dump(
                include={"id", "username", "name", "created_at", "description", "location", "followers_count",
                         "friends_count"}
            )
            if twitter_user_data["id"]:
                self.db_account.user, _ = await update_or_create(
                    session, TwitterUser, twitter_user_data, filter_by={"id": twitter_user_data["id"]})

            await session.commit()

        await super().close()

    async def quote_and_save(
            self,
            tweet_url: str,
            text: str,
            *,
            media_id: int | str = None,
    ) -> Tweet:
        # TODO Когда этот метод будет принимать tweet_id, а не tweet_url,
        #   не делать твит, если в бд уже есть об этом информация
        tweet = await self.quote(tweet_url, text, media_id=media_id)

        db_tweet = Tweet.from_pydantic_model(tweet)
        async with AsyncSessionmaker() as session:
            await session.merge(db_tweet)
            await session.commit()

        await sleep_between_actions(self.db_account)
        return db_tweet

    async def follow_and_save(self, user: twitter.User) -> bool:
        async with AsyncSessionmaker() as session:
            query = select(Following).options(
            ).filter_by(
                user_id=self.account.id,
                followed_to_user_id=user.id,
            )
            if await session.scalar(query):
                logger.warning(f"@{self.account.username} (id={self.account.id})"
                               f" User (id={user.id}) already followed")
                return True

        followed = await super().follow(user.id)
        if followed:
            logger.success(f"@{self.account.username} (id={self.account.id})"
                           f" Followed: @{user.username} (id={user.id})")
            async with AsyncSessionmaker() as session:
                session.add(Following(user_id=self.account.id, followed_to_user_id=user.id))
                await session.commit()

        await sleep_between_actions(self.db_account)
        return followed

    async def unfollow_and_save(self, user_id: str | int):
        unfollowed = await super().unfollow(user_id)
        if unfollowed:
            async with AsyncSessionmaker() as session:
                await session.delete(Following(user_id=self.account.id, followed_to_user_id=user_id))
                await session.commit()
        await sleep_between_actions(self.db_account)
        return unfollowed
