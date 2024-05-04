from ..database.models import TwitterAccount
from ..database.crud import ask_and_get_accounts
from ..database import AsyncSessionmaker
from ..twitter import TwitterClient
from .process_utils import process_twitter_accounts


async def enable_totp():
    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(session, statuses=("UNKNOWN", "GOOD", "LOCKED"))

    async def _enable_totp(twitter_account: TwitterAccount):
        async with TwitterClient(twitter_account) as twitter_client:
            await twitter_client.enable_totp()

    await process_twitter_accounts(_enable_totp, twitter_accounts)
