from ..database.models import TwitterAccount
from ..database.crud import ask_and_get_accounts
from ..database import AsyncSessionmaker
from ..twitter import TwitterClient

from .process_utils import process_twitter_accounts


async def _update_account_info(twitter_account: TwitterAccount):
    async with TwitterClient(twitter_account) as twitter_client:
        # Обновление информации об аккаунте по умолчанию отключено, так что делаем это вручную
        await twitter_client.update_account_info()
        await twitter_client.establish_status()


async def update_accounts_info():
    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(session, statuses=("UNKNOWN", "GOOD", "LOCKED", "BAD_TOKEN"))
    await process_twitter_accounts(_update_account_info, twitter_accounts)
