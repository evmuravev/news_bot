import logging
from databases import Database
from typing import TypeVar
from telegram.ext._application import Application
from telegram.ext import ContextTypes

from core.config import DATABASE_URL
from db.repositories.base import BaseRepository


global logger
logger = logging.getLogger(__name__)


async def connect_to_db(app: Application) -> None:
    database = Database(DATABASE_URL, min_size=2, max_size=20)
    try:
        await database.connect()
        app._db = database
    except Exception as e:
        logger.warn("--- DB CONNECTION ERROR ---")
        logger.warn(e)
        logger.warn("--- DB CONNECTION ERROR ---")


async def close_db_connection(app: Application) -> None:
    try:
        await app._db.disconnect()
    except Exception as e:
        logger.warn("--- DB DISCONNECT ERROR ---")
        logger.warn(e)
        logger.warn("--- DB DISCONNECT ERROR ---")


def get_database(app: Application) -> Database:
    return app._db


Repository = TypeVar("Repository")


def get_repository(
        Repo_type: Repository,
        context: ContextTypes.DEFAULT_TYPE
) -> Repository:
    return Repo_type(get_database(context.application))
