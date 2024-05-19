from typing import TYPE_CHECKING

from better_proxy import Proxy as BetterProxy

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, Int_PK

if TYPE_CHECKING:
    from .account import TwitterAccount


class Proxy(Base):
    __tablename__ = "proxy"

    # fmt: off
    database_id: Mapped[Int_PK]

    host:     Mapped[str] = mapped_column(String(253))
    port:     Mapped[int]
    login:    Mapped[str] = mapped_column(String(256))
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
