import asyncio
from typing import Callable
import inspect

import questionary
from loguru import logger

from common.project import print_project_info
from common.author import print_author_info, open_channel
from common.logger import setup_logger
from tweepy_manager.paths import LOG_DIR
from tweepy_manager.config import CONFIG
from tweepy_manager.database import update_database_or_quite
from tweepy_manager.modules.import_accounts import select_and_import_table
from tweepy_manager.modules.request_accounts_info import update_accounts_info
from tweepy_manager.modules.follow import follow
from tweepy_manager.modules.quote_tweet import quote
from tweepy_manager.modules.tags import add_tag


MODULES = {
    '❤️ Channel': open_channel,
    '➡️ Import accounts from .xlsx table': select_and_import_table,
    '➡️ Add tag': add_tag,
    '➡️ Update accounts info': update_accounts_info,
    '➡️ Follow': follow,
    '➡️ Quote Tweet (random word)': quote,
    '❌  Quit': quit,
}


def select_module(modules: dict[str: Callable]) -> Callable:
    module_name = questionary.select("Select module:", choices=modules).ask()
    return modules[module_name]


def main():
    asyncio.run(update_database_or_quite())
    setup_logger(LOG_DIR, CONFIG.LOGGING.LEVEL)
    logger.enable("twitter")
    print_project_info()
    print(">>>")
    print("Спасибо, что используете tweepy-manager!")
    print("Это бесплатный скрипт для работы с Twitter аккаунтами.")
    print("Сейчас доступно всего три модуля, но в будущем их будет гораздо больше!")
    print("Если вы программист, буду рад пулл реквестами.")
    print("Я рассчитываю на поддержку сообщества, давайте развивать этот инструмент вместе!")
    print_author_info()
    print("<<<")
    while True:
        fn = select_module(MODULES)
        if inspect.iscoroutinefunction(fn):
            asyncio.run(fn())
        else:
            fn()


if __name__ == "__main__":
    main()
