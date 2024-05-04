from functools import lru_cache

from loguru import logger
import requests


@lru_cache
def request_english_words() -> list[str]:
    """
    Запрашивает список английских слов.
    """
    url = 'https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt'
    response = requests.get(url)
    words = response.text.splitlines()
    logger.info(f"Requested {len(words)} english words from {url}")
    return words
