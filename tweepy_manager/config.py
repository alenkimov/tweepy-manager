from pydantic import BaseModel

from common.utils import load_toml

from common.config import (
    LoggingConfig,
    TwitterConfig,
    CaptchaConfig,
    ConcurrencyConfig,
    RequestsConfig,
)
from .paths import CONFIG_TOML


class Config(BaseModel):
    LOGGING: LoggingConfig
    CONCURRENCY: ConcurrencyConfig
    TWITTER: TwitterConfig
    CAPTCHA: CaptchaConfig
    REQUESTS: RequestsConfig


CONFIG = Config(**load_toml(CONFIG_TOML))

VALID_TWITTER_STATUSES = ["UNKNOWN", "GOOD"]
if CONFIG.TWITTER.USE_SUSPENDED_ACCOUNTS:
    VALID_TWITTER_STATUSES.append("SUSPENDED")
if CONFIG.CAPTCHA.CAPSOLVER_API_KEY:
    VALID_TWITTER_STATUSES.append("LOCKED")

