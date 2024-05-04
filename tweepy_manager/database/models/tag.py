from typing import TYPE_CHECKING

from sqlalchemy import String, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .account import TwitterAccount


class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = (PrimaryKeyConstraint("twitter_account_id", "tag"),)

    twitter_account_id: Mapped[int] = mapped_column(ForeignKey("twitter_account.database_id"))
    tag: Mapped[str] = mapped_column(String(16))

    twitter_account: Mapped["TwitterAccount"] = relationship(back_populates="tags")
