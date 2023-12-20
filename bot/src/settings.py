from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from pydantic import SecretStr, AnyUrl, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from web3 import Web3

__all__ = [
    "bot",
    "dp",
    "settings",
    "web3",
]

from web3.middleware import geth_poa_middleware


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        frozen=True
    )

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DOMAIN: HttpUrl

    DATABASE_URL: AnyUrl

    TELEGRAM_BOT_TOKEN: SecretStr
    TELEGRAM_SECRET_TOKEN: SecretStr


settings = Settings()

bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN.get_secret_value(),
    parse_mode=ParseMode.HTML
)
dp = Dispatcher()
web3 = Web3(Web3.HTTPProvider("https://eth.drpc.org"))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3.eth.account.enable_unaudited_hdwallet_features()
