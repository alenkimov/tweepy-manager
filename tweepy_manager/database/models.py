from typing import Annotated
from datetime import datetime

from better_proxy import Proxy as BetterProxy
from twitter.utils import hidden_value
import twitter

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


Int_PK = Annotated[int, mapped_column(primary_key=True)]


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Proxy(Base):
    __tablename__ = "proxy"

    # fmt: off
    database_id: Mapped[Int_PK]

    host:     Mapped[str] = mapped_column(String(253))
    port:     Mapped[int]
    login:    Mapped[str] = mapped_column(String(32))
    password: Mapped[str] = mapped_column(String(128))
    protocol: Mapped[str] = mapped_column(String(10))

    twitter_accounts: Mapped[list["TwitterAccount"]] = relationship(back_populates="proxy")
    # fmt: on

    def better_proxy(self) -> BetterProxy:
        return BetterProxy(
            host=self.host,
            port=self.port,
            login=self.login,
            password=self.password,
            protocol=self.protocol,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(database_id={self.database_id}, host={self.host}, port={self.port})"

    def __str__(self):
        return self.better_proxy().fixed_length


class TwitterUser(Base):
    __tablename__ = "twitter_user"

    # fmt: off
    id:              Mapped[Int_PK]
    # TODO Изменять TwitterAccount.username при изменении TwitterUser.username
    username:        Mapped[str | None] = mapped_column(String(100), unique=True)
    name:            Mapped[str | None] = mapped_column(String(50))
    description:     Mapped[str | None] = mapped_column(String(160))
    location:        Mapped[str | None] = mapped_column(String(30))
    created_at:      Mapped[datetime | None]
    followers_count: Mapped[int | None]
    friends_count:   Mapped[int | None]

    account: Mapped["TwitterAccount"] = relationship(back_populates="user")
    tweets:  Mapped[list["Tweet"]] = relationship(back_populates="user")
    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username})"

    def __str__(self):
        return repr(self)


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
    user:            Mapped[TwitterUser | None] = relationship(back_populates="tweets")

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


class TwitterAccount(Base):
    __tablename__ = "twitter_account"

    # fmt: off
    database_id: Mapped[Int_PK]

    auth_token:  Mapped[str | None] = mapped_column(unique=True)
    ct0:         Mapped[str | None] = mapped_column(String(160), unique=True)
    username:    Mapped[str | None] = mapped_column(String(100), unique=True)
    password:    Mapped[str | None] = mapped_column(String(128))
    totp_secret: Mapped[str | None] = mapped_column(String(16), unique=True)
    backup_code: Mapped[str | None] = mapped_column(String(12), unique=True)
    status:      Mapped[twitter.AccountStatus] = mapped_column(default="UNKNOWN")
    country_code: Mapped[str | None] = mapped_column(String(2))

    email:          Mapped[str]        = mapped_column(String(254), unique=True)
    email_password: Mapped[str | None] = mapped_column(String(128))

    twitter_id: Mapped[int   | None] = mapped_column(ForeignKey("twitter_user.id"))
    user: Mapped[TwitterUser | None] = relationship(back_populates="account")

    proxy_database_id: Mapped[int | None] = mapped_column(ForeignKey("proxy.database_id"))
    proxy: Mapped[Proxy | None] = relationship(back_populates="twitter_accounts")

    tags: Mapped[list["Tag"]] = relationship(back_populates="twitter_account")
    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(database_id={self.database_id}, auth_token={self.hidden_auth_token}, username={self.username})"

    def __str__(self):
        return repr(self)

    @property
    def hidden_auth_token(self) -> str | None:
        return hidden_value(self.auth_token) if self.auth_token else None


class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = (PrimaryKeyConstraint("twitter_account_id", "tag"),)

    twitter_account_id: Mapped[int] = mapped_column(ForeignKey("twitter_account.database_id"))
    tag: Mapped[str] = mapped_column(String(16))

    twitter_account: Mapped["TwitterAccount"] = relationship(back_populates="tags")


