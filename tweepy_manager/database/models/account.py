from typing import TYPE_CHECKING

from twitter.utils import hidden_value
import twitter

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, Int_PK

if TYPE_CHECKING:
    from .proxy import Proxy
    from .user import TwitterUser
    from .tag import Tag


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
    user: Mapped["TwitterUser" or None] = relationship(back_populates="account")

    proxy_database_id: Mapped[int | None] = mapped_column(ForeignKey("proxy.database_id"))
    proxy: Mapped["Proxy" or None] = relationship(back_populates="twitter_accounts")

    tags: Mapped[list["Tag"]] = relationship(back_populates="twitter_account")
    # fmt: on

    def __repr__(self):
        return f"{self.__class__.__name__}(database_id={self.database_id}, auth_token={self.hidden_auth_token}, username={self.username})"

    def __str__(self):
        return repr(self)

    @property
    def hidden_auth_token(self) -> str | None:
        return hidden_value(self.auth_token) if self.auth_token else None
