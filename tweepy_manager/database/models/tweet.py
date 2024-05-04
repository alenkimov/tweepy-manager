from typing import TYPE_CHECKING
from datetime import datetime

import twitter

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user import TwitterUser


class Tweet(Base):
    __tablename__ = "tweet"

    # fmt: off
    id:              Mapped[int] = mapped_column(primary_key=True)
    text:            Mapped[str]
    created_at:      Mapped[datetime]
    conversation_id: Mapped[int]
    quoted:          Mapped[bool]
    retweeted:       Mapped[bool]
    bookmarked:      Mapped[bool]
    favorited:       Mapped[bool]
    url:             Mapped[str]

    user_id:            Mapped[int] = mapped_column(ForeignKey("twitter_user.id"))
    user:            Mapped["TwitterUser" or None] = relationship(back_populates="tweets")

    quote_tweet_id:     Mapped[int | None] = mapped_column(ForeignKey("tweet.id"))
    # quote_tweets: Mapped[list["Tweet"]] = relationship(back_populates="quoted_tweet")
    # quoted_tweet: Mapped["Tweet" or None] = relationship(back_populates="quote_tweets", foreign_keys=[quote_tweet_id], remote_side=[id])
    quoted_tweet: Mapped["Tweet" or None] = relationship(foreign_keys=[quote_tweet_id], remote_side=[id])

    retweeted_tweet_id: Mapped[int | None] = mapped_column(ForeignKey("tweet.id"))
    # retweets:        Mapped[list["Tweet"]] = relationship(back_populates="retweeted_tweet")
    # retweeted_tweet: Mapped["Tweet" or None] = relationship(back_populates="retweets", foreign_keys=[retweeted_tweet_id], remote_side=[id])
    retweeted_tweet: Mapped["Tweet" or None] = relationship(foreign_keys=[retweeted_tweet_id], remote_side=[id])

    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, user_id={self.user_id})"

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_pydantic_model(cls, tweet: twitter.Tweet) -> "Tweet":
        from .user import TwitterUser

        tweet_fields = {"id", "text", "created_at", "conversation_id", "quoted",
                        "retweeted", "bookmarked", "favorited", "url"}
        user_fields = {"id", "username", "name", "description", "location",
                       "created_at", "followers_count", "friends_count"}
        db_tweet = cls(**tweet.model_dump(include=tweet_fields))
        db_tweet.user = TwitterUser(**tweet.user.model_dump(include=user_fields))

        if tweet.quoted_tweet:
            db_tweet.quoted_tweet = cls.from_pydantic_model(tweet.quoted_tweet)

        if tweet.retweeted_tweet:
            db_tweet.retweeted_tweet = cls.from_pydantic_model(tweet.retweeted_tweet)

        return db_tweet
