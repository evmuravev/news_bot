from enum import Enum
import handlers.create_news.news_parts as part

from typing import Coroutine
from telegram import Update
from telegram.ext import ContextTypes

from models.news import NewsInDB


class Steps(Enum):
    TEXT = 0
    IMAGE = 1
    IMAGE_SKIP = 11
    VIDEO = 2
    AUTHOR = 3
    FINAL_STEP = 99


def get_next_step(current_step: int) -> Coroutine[Update, ContextTypes, int]:
    next_steps_map = {
        Steps.TEXT: part.image.set_image_step,
        Steps.IMAGE: part.author.set_author_step,
        Steps.IMAGE_SKIP: part.video.set_video_step,
        Steps.VIDEO: part.author.set_author_step,
        Steps.AUTHOR: part.final_step.set_final_step,
    }
    return next_steps_map[current_step]


def get_previous_step(
        current_step: int,
        news: NewsInDB = None
) -> Coroutine[Update, ContextTypes, int]:
    previous_steps_map = {
        Steps.IMAGE: part.text.set_text_step,
        Steps.VIDEO: part.image.set_image_step,
        Steps.AUTHOR: part.image.set_image_step if news and news.image else part.video.set_video_step,
        Steps.FINAL_STEP: part.author.set_author_step,
    }

    return previous_steps_map[current_step]
