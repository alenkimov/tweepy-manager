from pydantic import BaseModel

from .logger import LoggingLevel


class LoggingConfig(BaseModel):
    LEVEL: LoggingLevel = "INFO"


class ConcurrencyConfig(BaseModel):
    MAX_TASKS: int = 1
    MAX_RETRIES: int = 3
    DELAY_BETWEEN_RETRIES: int = 5
    DELAY_BETWEEN_ACTIONS: tuple[int, int] = (0, 0)
    DELAY_BETWEEN_ACCOUNTS: tuple[int, int] = (0, 0)


class RequestsConfig(BaseModel):
    TIMEOUT: int = 30
    REQUIRE_PROXY: bool = True


class TwitterConfig(BaseModel):
    AUTO_RELOGIN: bool = True
    MAX_UNLOCK_ATTEMPTS: int = 5
    USE_SUSPENDED_ACCOUNTS: bool = False


class CaptchaConfig(BaseModel):
    CAPSOLVER_API_KEY: str | None = None


class MobileProxyConfig(BaseModel):
    PROXY: str | None = None
    CHANGE_IP_URL: str | None = None


class DatabaseConfig(BaseModel):
    DATABASE_NAME: str
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: int
