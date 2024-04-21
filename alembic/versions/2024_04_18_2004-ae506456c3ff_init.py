"""init

Revision ID: ae506456c3ff
Revises: 
Create Date: 2024-04-18 20:04:48.885546

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ae506456c3ff"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "proxy",
        sa.Column("database_id", sa.Integer(), nullable=False),
        sa.Column("host", sa.String(length=253), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("login", sa.String(length=32), nullable=False),
        sa.Column("password", sa.String(length=128), nullable=False),
        sa.Column("protocol", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("database_id"),
    )
    op.create_table(
        "twitter_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.Column("description", sa.String(length=160), nullable=True),
        sa.Column("location", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("followers_count", sa.Integer(), nullable=True),
        sa.Column("friends_count", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "twitter_account",
        sa.Column("database_id", sa.Integer(), nullable=False),
        sa.Column("auth_token", sa.String(), nullable=True),
        sa.Column("ct0", sa.String(length=160), nullable=True),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("password", sa.String(length=128), nullable=True),
        sa.Column("totp_secret", sa.String(length=16), nullable=True),
        sa.Column("backup_code", sa.String(length=12), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "UNKNOWN",
                "BAD_TOKEN",
                "SUSPENDED",
                "LOCKED",
                "CONSENT_LOCKED",
                "GOOD",
                name="accountstatus",
            ),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("email_password", sa.String(length=128), nullable=True),
        sa.Column("twitter_id", sa.Integer(), nullable=True),
        sa.Column("proxy_database_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["proxy_database_id"],
            ["proxy.database_id"],
        ),
        sa.ForeignKeyConstraint(
            ["twitter_id"],
            ["twitter_user.id"],
        ),
        sa.PrimaryKeyConstraint("database_id"),
        sa.UniqueConstraint("auth_token"),
        sa.UniqueConstraint("backup_code"),
        sa.UniqueConstraint("ct0"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("totp_secret"),
        sa.UniqueConstraint("username"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("twitter_account")
    op.drop_table("twitter_user")
    op.drop_table("proxy")
    # ### end Alembic commands ###
