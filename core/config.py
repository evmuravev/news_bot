from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

import os

print(os.getcwd())

config = Config(".env")

PROJECT_NAME = "news_bot"
VERSION = "1.0.0"

POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="localhost")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str, default="postgres")
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN", cast=str)
TELEGRAM_CHANNEL_ID = config("TELEGRAM_CHANNEL_ID", cast=str)
SECRET_TOKEN = config("SECRET_TOKEN", cast=str)
WEBHOOK_URL = config("WEBHOOK_URL", cast=str)
PORT = config("PORT", cast=int)

DATABASE_URL = config(
  "DATABASE_URL",
  cast=DatabaseURL,
  default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
