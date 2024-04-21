from typing import Annotated
from datetime import datetime

from better_proxy import Proxy as BetterProxy
from twitter.utils import hidden_value
import twitter

from sqlalchemy import ForeignKey
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
    username:        Mapped[str | None] = mapped_column(String(100), unique=True)
    name:            Mapped[str | None] = mapped_column(String(50))
    description:     Mapped[str | None] = mapped_column(String(160))
    location:        Mapped[str | None] = mapped_column(String(30))
    created_at:      Mapped[datetime | None]
    followers_count: Mapped[int | None]
    friends_count:   Mapped[int | None]

    account: Mapped["TwitterAccount"] = relationship(back_populates="user")
    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username})"

    def __str__(self):
        return repr(self)


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

    email:          Mapped[str]        = mapped_column(String(254), unique=True)
    email_password: Mapped[str | None] = mapped_column(String(128))

    twitter_id: Mapped[int   | None] = mapped_column(ForeignKey("twitter_user.id"))
    user: Mapped[TwitterUser | None] = relationship(back_populates="account")

    proxy_database_id: Mapped[int | None] = mapped_column(ForeignKey("proxy.database_id"))
    proxy: Mapped[Proxy | None] = relationship(back_populates="twitter_accounts")
    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(database_id={self.database_id}, auth_token={self.hidden_auth_token}, username={self.username})"

    def __str__(self):
        return repr(self)

    @property
    def hidden_auth_token(self) -> str | None:
        return hidden_value(self.auth_token) if self.auth_token else None
