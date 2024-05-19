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

# Модули
from tweepy_manager.modules.import_ import select_and_import_xlsx
from tweepy_manager.modules.export import export_to_xlsx
from tweepy_manager.modules.request_accounts_info import update_accounts_info
from tweepy_manager.modules.follow import follow
from tweepy_manager.modules.quote_tweet import quote
from tweepy_manager.modules.tags import add_tag
from tweepy_manager.modules.enable_totp import enable_totp
from tweepy_manager.modules.follow_each_other import follow_each_other


MODULES = {
    '❤️ Channel': open_channel,
    '➡️ Import accounts from .xlsx table': select_and_import_xlsx,
    '➡️ Export accounts to .xlsx table': export_to_xlsx,
    '➡️ Add tag': add_tag,
    '➡️ Update accounts info': update_accounts_info,
    '➡️ Follow': follow,
    '➡️ Quote Tweet (random word)': quote,
    '➡️ Enable TOTP (2FA)': enable_totp,
    '➡️ Follow each other': follow_each_other,
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
    print("Сейчас доступно всего несколько модулей, но в будущем их будет гораздо больше!")
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
