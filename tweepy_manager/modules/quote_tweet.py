import datetime
import random
from collections import defaultdict
from typing import Iterable

import twitter
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import joinedload, subqueryload
import questionary

from ..database import TwitterAccount, AsyncSessionmaker, Tweet
from ..database.crud import ask_and_get_accounts
from ..twitter import TwitterClient
from ._process_utils import process_twitter_accounts, ask_and_request_tweets
from ..utils import request_english_words
from ..paths import OUTPUT_DIR


async def _quote(twitter_account: TwitterAccount, tweets: Iterable[twitter.Tweet], texts: Iterable[str]) -> list[Tweet]:
    async with TwitterClient(twitter_account) as twitter_client, AsyncSessionmaker() as session:
        quote_tweets = []
        for tweet_to_quote, text in zip(tweets, texts):
            query = select(Tweet).options(
                joinedload(Tweet.quoted_tweet),
                joinedload(Tweet.retweeted_tweet),
                joinedload(Tweet.user),
            ).filter_by(
                user_id=twitter_account.twitter_id,
                quote_tweet_id=tweet_to_quote.id,
            )

            if existing_quote_tweet := await session.scalar(query):
                await session.refresh(existing_quote_tweet.quoted_tweet, ["user"])
                quote_tweets.append(existing_quote_tweet)
                logger.warning(f"@{twitter_account.username} (id={twitter_account.user.id})"
                               f" Quote Tweet already existing"
                               f"\n\tTweet ID: {existing_quote_tweet.id}"
                               f"\n\tQuoted Tweet ID: {tweet_to_quote.id}"
                               f"\n\tText: {existing_quote_tweet.text}")
                continue

            tweet = await twitter_client.quote_and_save(tweet_to_quote.url, text)
            quote_tweets.append(tweet)
            logger.success(f"@{twitter_account.username} (id={twitter_account.user.id})"
                           f" Tweet Quoted"
                           f"\n\tTweet ID: {tweet.id}"
                           f"\n\tQuoted Tweet ID: {tweet_to_quote.id}"
                           f"\n\tText: {text}")
        return quote_tweets


async def quote():
    english_words = request_english_words()

    async with AsyncSessionmaker() as session:
        twitter_accounts = await ask_and_get_accounts(session, statuses=("GOOD",))

    if not twitter_accounts:
        return

    tweets = await ask_and_request_tweets(random.choice(twitter_accounts))

    if not await questionary.confirm("Resume?").ask_async():
        return

    quote_tweets = []

    async def _custom_quote(twitter_account: TwitterAccount):
        quote_tweets.extend(await _quote(twitter_account, tweets, random.sample(english_words, len(tweets))))

    await process_twitter_accounts(_custom_quote, twitter_accounts)

    #                         tweet_to_quote      quote_tweet
    sorted_quote_tweets: dict[Tweet: list[Tweet]] = defaultdict(list)
    for tweet in quote_tweets:  # type: Tweet
        sorted_quote_tweets[tweet.quoted_tweet].append(tweet)

    # Сохранение результатов в текстовый файл
    now = datetime.datetime.now()
    date_str = now.strftime("date_%d_%m_%Y.time_%H_%M_%S")
    for tweet, quote_tweets in sorted_quote_tweets.items():
        tweets_count = len(quote_tweets)
        filename = f"{tweets_count}_quote_tweets.id_{tweet.id}.{date_str}.txt"
        with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as file:
            file.write("Quoted Tweet:\n")
            file.write(f"User ID: {tweet.user.id}\n")
            file.write(f"Username: {tweet.user.username}\n")
            file.write(f"Tweet ID: {tweet.id}\n")
            file.write(f"Tweet URL: {tweet.url}\n")
            file.write(f"Tweet Text:\n")
            file.write(f"\"\"\"\n")
            file.write(f"{tweet.text}\n")
            file.write(f"\"\"\"\n")
            file.write("User ID,Username,Quote Tweet ID,Quote Tweet URL,Quote Tweet Text\n")
            for quote_tweet in quote_tweets:  # type: twitter.Tweet
                file.write(','.join((
                    str(quote_tweet.user.id),
                    quote_tweet.user.username,
                    str(quote_tweet.id),
                    quote_tweet.url,
                    quote_tweet.text,
                )))
                file.write("\n")
