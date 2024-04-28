import twitter

from .config import CONFIG

from common.sqlalchemy.crud import update_or_create
from .database import (
    AsyncSessionmaker,
    TwitterAccount,
    TwitterUser,
    Following,
    Tweet,
)


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
        tweet = await self.quote(tweet_url, text, media_id=media_id)

        db_tweet = Tweet.from_pydantic_model(tweet)
        async with AsyncSessionmaker() as session:
            await session.merge(db_tweet)
            await session.commit()

        return db_tweet

    async def follow(self, user_id: str | int):
        # TODO Не подписываться, если в бд есть об этом информация
        followed = await super().follow(user_id)
        if followed:
            async with AsyncSessionmaker() as session:
                session.add(Following(user_id=self.account.id, followed_to_user_id=user_id))
                await session.commit()

    async def unfollow(self, user_id: str | int):
        followed = await super().unfollow(user_id)
        if followed:
            async with AsyncSessionmaker() as session:
                await session.delete(Following(user_id=self.account.id, followed_to_user_id=user_id))
                await session.commit()
