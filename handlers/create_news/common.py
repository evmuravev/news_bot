from enum import Enum
import handlers.create_news.news_parts as part

from typing import Coroutine
from telegram import Update
from telegram.ext import ContextTypes


class Steps(Enum):
    TEXT = 0
    IMAGES = 1
    VIDEO = 2
    AUTHOR = 3
    FINAL_STEP = 99


def get_next_step(current_step: int) -> Coroutine[Update, ContextTypes, int]:
    next_steps_map = {
        Steps.TEXT: part.images.set_images_step,
        Steps.IMAGES: part.video.set_video_step,
        Steps.VIDEO: part.author.set_author_step,
        Steps.AUTHOR: part.final_step.set_final_step,
    }
    return next_steps_map[current_step]


def get_previous_step(current_step: int) -> Coroutine[Update, ContextTypes, int]:
    previous_steps_map = {
        Steps.IMAGES: part.text.set_text_step,
        Steps.VIDEO: part.images.set_images_step,
        Steps.AUTHOR: part.video.set_video_step,
        Steps.FINAL_STEP: part.author.set_author_step,
    }

    return previous_steps_map[current_step]
