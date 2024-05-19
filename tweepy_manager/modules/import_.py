from better_proxy import parse_proxy_str

import questionary

from common.excel import get_xlsx_filepaths, get_worksheets
from common.sqlalchemy.crud import update_or_create

from ..database.models import TwitterAccount, Proxy, Tag
from ..database import AsyncSessionmaker
from ..paths import INPUT_DIR
from ..excel import excel


async def select_and_import_xlsx():
    table_filepaths = get_xlsx_filepaths(INPUT_DIR)

    if len(table_filepaths) == 0:
        template_table_filepath = excel.create_empty_table(INPUT_DIR, "template")
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
    table = excel.read_worksheet(selected_worksheet)

    print(f"Loaded {len(table)} rows from {selected_table_filepath.name} ({selected_worksheet_name})")
    async with AsyncSessionmaker() as session:
        for data in table:
            if data["country_code"]:  # type: str
                data["country_code"] = data["country_code"].lower()

            twitter_id = None
            if data["twitter"]["twitter_id"]:
                twitter_id = int(data["twitter"]["twitter_id"])
                del data["twitter"]["twitter_id"]

            # keys = await questionary.checkbox("What to import:", choices=data).ask_async()
            # data = {key: data[key] for key in keys}

            if twitter_id:
                twitter_account, created = await update_or_create(
                    session,
                    TwitterAccount,
                    data["twitter"],
                    filter_by={"twitter_id": twitter_id},
                )

            else:
                twitter_account = TwitterAccount(**data["twitter"])
                session.add(twitter_account)
                created = True

            if created: print("(NEW!) ", end="")
            print(repr(twitter_account))

            if raw_tags := data["tags"]:  # type: str
                print(f"\tTags: {raw_tags}")
                for tag_name in raw_tags.split(","):  # type: str
                    tag_name = tag_name.strip()
                    await session.merge(Tag(twitter_account_id=twitter_account.database_id, tag=tag_name))

            if data["proxy"]:
                parsed_proxy = parse_proxy_str(data["proxy"])
                parsed_proxy["protocol"] = parsed_proxy["protocol"] or "http"
                # TODO Не фильтровать по протоколу
                twitter_account.proxy, created = await update_or_create(session, Proxy, parsed_proxy, filter_by=parsed_proxy)
                if created:
                    print("\t(NEW!) ", end="")
                else:
                    print("\t")
                print(repr(twitter_account.proxy))

            await session.commit()
