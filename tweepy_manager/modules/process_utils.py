import asyncio
from typing import Callable, Iterable

from loguru import logger
from tqdm.asyncio import tqdm
import twitter
import curl_cffi

from common.ask import ask_values_with_separator

from ..database.models import TwitterAccount
from ..database import AsyncSessionmaker
from ..twitter import TwitterClient
from ..config import CONFIG


async def sleep_between_retries(twitter_account: TwitterAccount, retries: int):
    if not CONFIG.CONCURRENCY.DELAY_BETWEEN_RETRIES:
        return

    logger.info(f"@{twitter_account.username} (id={twitter_account.twitter_id})"
                f" Sleep time: {CONFIG.CONCURRENCY.DELAY_BETWEEN_RETRIES} seconds."
                f"\n\tОсталось попыток: {retries}")
    await asyncio.sleep(CONFIG.CONCURRENCY.DELAY_BETWEEN_RETRIES)


async def process_account(fn, twitter_account):
    retries = CONFIG.CONCURRENCY.MAX_RETRIES
    while retries > 0:
        try:
            # Функции будет вызываться повторно, если не произведен выход из цикла (break)
            await fn(twitter_account)
            break

        except (twitter.errors.BadAccount, twitter.errors.TwitterException) as exc:
            logger.warning(f"{twitter_account} {exc}")
            break

        except twitter.errors.HTTPException as exc:
            if exc.response.status_code >= 500:
                logger.warning(f"{twitter_account} {exc}")
                # повторная попытка
            elif 398 in exc.api_codes:
                logger.error(f"{twitter_account} Relogin failed! Try again later")
                break
            elif 399 in exc.api_codes:
                logger.error(f"{twitter_account} Account deleted! Deleting from database...")
                async with AsyncSessionmaker() as session:
                    await session.delete(twitter_account)
                    await session.commit()
                break
            else:
                raise

        except curl_cffi.requests.errors.RequestsError as exc:
            if exc.code in (23, 28, 35, 56, 7, 18, 56):
                logger.warning(f"{twitter_account} (May be bad or slow proxy) {exc}")
                # повторная попытка
            else:
                raise

        retries -= 1
        if retries > 0:
            await sleep_between_retries(twitter_account, retries)


async def process_twitter_accounts(fn: Callable, twitter_accounts: Iterable[TwitterAccount]):

    if CONFIG.CONCURRENCY.MAX_TASKS > 1:
        # Create a semaphore with the specified max tasks
        semaphore = asyncio.Semaphore(CONFIG.CONCURRENCY.MAX_TASKS)

        async def wrapper(twitter_account):
            async with semaphore:
                await process_account(fn, twitter_account)

        # Create a list of tasks to be executed concurrently
        tasks = [wrapper(twitter_account) for twitter_account in twitter_accounts]

        # Wait for all tasks to complete
        await tqdm.gather(*tasks)
    else:
        for twitter_account in tqdm(twitter_accounts):
            await process_account(fn, twitter_account)


# TODO ask_and_get_users() - В первую очередь ищет твит в бд
async def ask_and_request_users(twitter_account: TwitterAccount) -> list[twitter.User]:
    usernames = await ask_values_with_separator(
        "Usernames:",
        f"Enter Twitter usernames (handles / screen_names) separated by spaces"
        f"\nExample: elonmusk jeffbezos twitterdev"
    )

    users = []
    async with TwitterClient(twitter_account) as twitter_client:  # type: TwitterClient
        for username in usernames:
            username = twitter.utils.remove_at_sign(username)
            user = await twitter_client.request_user_by_username(username)
            if user:
                users.append(user)
            else:
                print(f"User @{username} not found")

    print("Users:")
    for user in users:
        print(f"\t@{user.username} (id={user.id})")
    return users


# TODO ask_and_get_tweets() - В первую очередь ищет твит в бд
async def ask_and_request_tweets(twitter_account: TwitterAccount) -> list[twitter.Tweet]:
    tweet_ids = await ask_values_with_separator(
        "Tweet IDs:",
        f"Enter Tweet IDs separated by spaces"
        f"\nExample: 1780204494640304336 1780506488701624699"
    )

    tweets = []
    print("Tweets:")
    async with TwitterClient(twitter_account) as twitter_client:  # type: TwitterClient
        for tweet_id in tweet_ids:
            tweet = await twitter_client.request_tweet(tweet_id)
            if tweet:
                tweets.append(tweet)
                print(f"\t(id={tweet.id}) {tweet.short_text}")
            else:
                print(f"Tweet (id={tweet_id}) not found")

    return tweets
