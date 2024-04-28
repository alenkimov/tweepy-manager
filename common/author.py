import webbrowser

GITHUB_LINK = "https://github.com/alenkimov"
TG_CHANNEL_LINK = "https://t.me/cum_insider"
TG_DIRECT_CHANNEL_LINK = "tg://resolve?domain=cum_insider"


def print_author_info():
    print(f"\nПодписывайтесь на канал: {TG_CHANNEL_LINK}")


def open_channel():
    webbrowser.open(TG_DIRECT_CHANNEL_LINK)
