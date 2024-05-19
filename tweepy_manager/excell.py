from common.excell import Excel, Column

# fmt: off
COLUMNS = [
    Column("Tags",           "Tags. Example: tag1, tag2, tag3\nTags are case-insensitive!", "tags"),
    Column("Proxy",          "Proxy: any format",             "proxy"),
    Column("Country code",   "Country code. Example: RU",     "country_code"),
    Column("ID",             "Twitter ID",                    "id",             group_name="twitter"),
    Column("Username",       "Twitter username (without @)",  "username",       group_name="twitter"),
    Column("Password",       "Twitter password",              "password",       group_name="twitter"),
    Column("Email",          "Twitter email",                 "email",          group_name="twitter"),
    Column("Email password", "Twitter email password",        "email_password", group_name="twitter"),
    Column("TOTP secret",    "Twitter TOTP secret key (2FA)", "totp_secret",    group_name="twitter"),
    Column("Backup code",    "Twitter backup code",           "backup_code",    group_name="twitter"),
    Column("Token",          "Twitter auth_token",            "auth_token",     group_name="twitter"),
]
# fmt: on

excell = Excel(COLUMNS)
