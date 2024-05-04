from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import String, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base, Int_PK
from .tweet import Tweet

if TYPE_CHECKING:
    from .account import TwitterAccount


class TwitterUser(Base):
    __tablename__ = "twitter_user"

    # fmt: off
    id:              Mapped[Int_PK]
    # TODO Изменять TwitterAccount.username при изменении TwitterUser.username на уровне базы данных
    username:        Mapped[str | None] = mapped_column(String(100), unique=True)
    name:            Mapped[str | None] = mapped_column(String(50))
    description:     Mapped[str | None] = mapped_column(String(160))
    location:        Mapped[str | None] = mapped_column(String(30))
    created_at:      Mapped[datetime | None]
    followers_count: Mapped[int | None]
    friends_count:   Mapped[int | None]

    account: Mapped["TwitterAccount"] = relationship(back_populates="user")
    tweets:  Mapped[list[Tweet]] = relationship(back_populates="user")
    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username})"

    def __str__(self):
        return repr(self)

    # async def get_tweets_by_quote_tweet_id(
    #         self,
    #         session: AsyncSession,
    #         quote_tweet_ids: list[int],
    # ) -> dict[int: Tweet | None]:
    #     query = self.tweets.where(Tweet.quote_tweet_id.in_(quote_tweet_ids))
    #     quoted_tweets = await session.scalars(query)
    #
    #     result = {}
    #
    #     for tweet in quoted_tweets:
    #         result[tweet.quote_tweet_id] = tweet.quoted_tweet
    #
    #     for quote_tweet_id in quote_tweet_ids:
    #         if quote_tweet_id not in result:
    #             result[quote_tweet_id] = None
    #
    #     return result


class Following(Base):
    __tablename__ = "following"
    __table_args__ = (PrimaryKeyConstraint("user_id", "followed_to_user_id"),)

    # fmt: off
    user_id:        Mapped[int] = mapped_column(ForeignKey("twitter_user.id"))
    followed_to_user_id: Mapped[int] = mapped_column(ForeignKey("twitter_user.id"))
    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(user_id={self.user_id}, followed_to_user_id={self.followed_to_user_id})"

    def __str__(self):
        return repr(self)
