from better_proxy import parse_proxy_str

import questionary

from common.excell import get_xlsx_filepaths, get_worksheets
from common.sqlalchemy.crud import update_or_create

from tweepy_manager.paths import INPUT_DIR
from tweepy_manager.excell import excell
from tweepy_manager.database import AsyncSessionmaker, TwitterAccount, Proxy, Tag


async def select_and_import_table():
    table_filepaths = get_xlsx_filepaths(INPUT_DIR)

    if len(table_filepaths) == 0:
        template_table_filepath = excell.create_empty_table(INPUT_DIR, "template")
        print(f"Created template XLSX table: {template_table_filepath}")
        return
    elif len(table_filepaths) == 1:
        selected_table_filepath = table_filepaths[0]
    else:
        table_filenames = [filepath.name for filepath in table_filepaths]
        selected_table_filename = await questionary.select("Which table?", choices=table_filenames).ask_async()
        selected_table_filepath = INPUT_DIR / selected_table_filename

    worksheets = get_worksheets(selected_table_filepath)

    # TODO Показывать также количество строк в листах
    selected_worksheet_name = await questionary.select("Which worksheet?", choices=worksheets).ask_async()
    selected_worksheet = worksheets[selected_worksheet_name]
    table_data = excell.read_worksheet(selected_worksheet)

    print(f"Loaded {len(table_data)} rows from {selected_table_filepath.name} ({selected_worksheet_name})")
    async with AsyncSessionmaker() as session:
        for twitter_account_data in table_data:
            twitter_account, created = await update_or_create(
                session,
                TwitterAccount,
                twitter_account_data["twitter"],
                filter_by={"auth_token": twitter_account_data["twitter"]["auth_token"]},
            )
            if created: print("(NEW!) ", end="")
            print(repr(twitter_account))

            if country_code := twitter_account_data.get("country_code"):  # type: str
                twitter_account.country_code = country_code.lower()

            await session.commit()

            if raw_tags := twitter_account_data["tags"]:  # type: str
                print(f"\tTags: {raw_tags}")
                for tag_name in raw_tags.split(","):  # type: str
                    tag_name = tag_name.strip()
                    await session.merge(Tag(twitter_account_id=twitter_account.database_id, tag=tag_name))

            if twitter_account_data["proxy"]:
                parsed_proxy = parse_proxy_str(twitter_account_data["proxy"])
                parsed_proxy["protocol"] = parsed_proxy["protocol"] or "http"
                twitter_account.proxy, created = await update_or_create(session, Proxy, parsed_proxy, filter_by=parsed_proxy)
                if created:
                    print("\t(NEW!) ", end="")
                else:
                    print("\t")
                print(repr(twitter_account.proxy))

            await session.commit()
