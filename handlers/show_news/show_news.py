import logging
from dataclasses import dataclass
from telegram import (
    InputMediaPhoto,
    InputMediaVideo,
    Update,
    error
)
from telegram.ext import (
    ContextTypes,
)
from db.repositories.news import NewsRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from core.config import TELEGRAM_CHANNEL_ID
from models.user import UserPublic
from utils.utils import escape_markdownv2


logger = logging.getLogger()


DESCRIPTION = f"""
{{text}}

Автор: {{author}}
\-\-\-\-\-\-\-
⚡️[Опубликовать свою новость](https://t.me/{TELEGRAM_CHANNEL_ID.replace('@','')}_bot)
🐦‍⬛️ ||Чик\-чирик\!||
"""


async def show_news(user: UserPublic, context: ContextTypes.DEFAULT_TYPE):
    news_repo: NewsRepository = get_repository(NewsRepository, context)
    news = await news_repo.get_last_news_by_user_id(user_id=user.id)

    caption = DESCRIPTION.format(
        text=escape_markdownv2(news.text),
        author=escape_markdownv2(news.author)
    )
    media = [
        *[InputMediaPhoto(image) for image in news.images],
        *[InputMediaVideo(video) for video in [news.video] if news.video]
    ]
    return media, caption


async def show_news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    media, caption = await show_news(user, context)
    if media:
        await context.bot.send_media_group(
                chat_id=user.id,
                media=media,
                caption=caption,
                parse_mode="MarkdownV2",
        )
    else:
        await context.bot.send_message(
                chat_id=user.id,
                text=caption,
                parse_mode="MarkdownV2",
        )
