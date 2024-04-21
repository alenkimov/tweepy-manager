import asyncio
from typing import Callable

from loguru import logger
from tqdm.asyncio import tqdm
import twitter
import curl_cffi

from ..database.crud import get_accounts
from ..database import AsyncSessionmaker, TwitterAccount
from ..config import CONFIG
from ..twitter import TwitterClient


async def process_twitter_accounts(fn: Callable):
    async with AsyncSessionmaker() as session:
        twitter_accounts = await get_accounts(session)

    async def process_account(twitter_account):
        retries = CONFIG.CONCURRENCY.MAX_RETRIES
        while retries > 0:
            try:
                # Функции будет вызываться повторно, если не произведен выход из цикла (break)
                await fn(twitter_account)
                break

            except twitter.errors.BadAccount as exc:
                logger.warning(f"{twitter_account} {exc}")
                break

            except twitter.errors.HTTPException as exc:
                if exc.response.status_code >= 500:
                    logger.warning(f"{twitter_account} {exc}")
                    # повторная попытка
                elif 398 in exc.api_codes:
                    logger.error(f"{twitter_account} Relogin failed! Try again later")
                    break
                else:
                    raise

            except curl_cffi.requests.errors.RequestsError as exc:
                if exc.code in (23, 28, 35, 56, 7):
                    logger.warning(f"{twitter_account} (May be bad or slow proxy) {exc}")
                    # повторная попытка
                else:
                    raise

            retries -= 1
            if retries > 0:
                # Пауза перед следующей попыткой
                sleep_time = CONFIG.CONCURRENCY.DELAY_BETWEEN_RETRIES
                logger.warning(f"{twitter_account}"
                               f" Не удалось завершить выполнение."
                               f" Повторная попытка через {sleep_time}s."
                               f" Осталось попыток: {retries}.")
                await asyncio.sleep(sleep_time)

    if CONFIG.CONCURRENCY.MAX_TASKS > 1:
        # Create a semaphore with the specified max tasks
        semaphore = asyncio.Semaphore(CONFIG.CONCURRENCY.MAX_TASKS)

        async def wrapper(twitter_account):
            async with semaphore:
                await process_account(twitter_account)

        # Create a list of tasks to be executed concurrently
        tasks = [wrapper(twitter_account) for twitter_account in twitter_accounts]

        # Wait for all tasks to complete
        await tqdm.gather(*tasks)
    else:
        for twitter_account in tqdm(twitter_accounts):
            await process_account(twitter_account)


async def request_account_info(twitter_account: TwitterAccount):
    async with TwitterClient(twitter_account) as twitter_client:
        ...

