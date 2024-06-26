from pydantic import BaseModel

from common.utils import load_toml

from common.config import (
    LoggingConfig,
    TwitterConfig,
    CaptchaConfig,
    ConcurrencyConfig,
    RequestsConfig,
    DatabaseConfig,
)
from .paths import CONFIG_TOML


class Config(BaseModel):
    LOGGING: LoggingConfig
    CONCURRENCY: ConcurrencyConfig
    TWITTER: TwitterConfig
    CAPTCHA: CaptchaConfig
    REQUESTS: RequestsConfig
    DATABASE: DatabaseConfig


CONFIG = Config(**load_toml(CONFIG_TOML))
