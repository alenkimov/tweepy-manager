from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..database.models import TwitterAccount, Tag
from ..database import AsyncSessionmaker
from ..paths import OUTPUT_DIR
from ..excel import excel


async def get_tags(session, account_id: int) -> str:
    tags = await session.scalars(select(Tag).where(Tag.twitter_account_id == account_id))
    return ", ".join([tag.tag for tag in tags])


async def export_to_xlsx():
    """
    Экспортирует все аккаунты из базы данных в Excel-таблицу.
    """
    async with AsyncSessionmaker() as session:
        accounts = await session.scalars(select(TwitterAccount).options(
            joinedload(TwitterAccount.proxy),
            joinedload(TwitterAccount.user),
        ))
        accounts = list(accounts)

    if not accounts:
        print(f"No accounts to export")

    accounts = sorted(accounts, key=lambda account: account.status)

    data = []
    for account in accounts:
        row = {
            "tags": await get_tags(session, account.database_id),
            "proxy": str(account.proxy.better_proxy()) if account.proxy else "",
            "country_code": account.country_code,
            "twitter": {
                "id": account.twitter_id,
                "username": account.username,
                "password": account.password,
                "email": account.email,
                "email_password": account.email_password,
                "totp_secret": account.totp_secret,
                "backup_code": account.backup_code,
                "auth_token": account.auth_token,
                "status": account.status,
            },
        }
        data.append(row)

    export_dir = OUTPUT_DIR / "accounts"
    export_dir.mkdir(exist_ok=True)
    filename = f"twitter_accounts.{datetime.now().strftime('date_%d_%m_%Y.time_%H_%M_%S')}.xlsx"
    filepath = export_dir / filename
    excel.export(filepath, data)
    print(f"Success! {filepath}")
