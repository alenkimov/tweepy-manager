import asyncio
from typing import Callable

import questionary
from loguru import logger

from common.project import print_project_info
from common.author import print_author_info
from common.logger import setup_logger
from tweepy_manager.paths import LOG_DIR
from tweepy_manager.config import CONFIG
from tweepy_manager.database import update_database_or_quite
from tweepy_manager.modules.import_ import select_and_import_table
from tweepy_manager.modules.request_accounts_info import process_twitter_accounts, request_account_info


setup_logger(LOG_DIR, CONFIG.LOGGING.LEVEL)
logger.enable("twitter")


def _select_and_import_table():
    asyncio.run(select_and_import_table())


def _request_accounts_info():
    asyncio.run(process_twitter_accounts(request_account_info))


MODULES = {
    '❌  Quit': quit,
    '➡️ Import xlsx table': _select_and_import_table,
    '➡️ Request accounts info': _request_accounts_info,
}


def select_module(modules: dict[str: Callable]) -> Callable:
    module_name = questionary.select("Select module:", choices=list(modules.keys())).ask()
    return modules[module_name]


def main():
    asyncio.run(update_database_or_quite())
    print_project_info()
    print_author_info()
    while True:
        select_module(MODULES)()


if __name__ == "__main__":
    main()
