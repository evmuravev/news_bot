import logging
import random
from dataclasses import dataclass
from telegram import (
    Update,
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


SOUNDS = ['Чик-чирик!', 'Чив-чив!']
DESCRIPTION = f"""
{{text}}

Автор: {{author}}
\-\-\-\-\-\-\-
⚡️[Опубликовать свою новость](https://t.me/{TELEGRAM_CHANNEL_ID.replace('@','')}_bot)
🐦‍⬛️ ||{{sound}}||
"""


@dataclass
class News:
    image: str
    video: str
    caption: str


async def show_news(user: UserPublic, context: ContextTypes.DEFAULT_TYPE):
    news_repo: NewsRepository = get_repository(NewsRepository, context)
    news = await news_repo.get_last_news_by_user_id(user_id=user.id)

    caption = DESCRIPTION.format(
        text=escape_markdownv2(news.text),
        author=escape_markdownv2(news.author),
        sound=escape_markdownv2(random.choice(SOUNDS))
    )

    return News(news.image, news.video, caption)


async def show_news_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    news: News = await show_news(user, context)
    common_params = {
        "chat_id": user.id,
        "parse_mode": "MarkdownV2",
    }
    match news:
        case News(image=None, video=None):
            await context.bot.send_message(
                    text=news.caption,
                    **common_params
            )
        case News(video=None):
            await context.bot.send_photo(
                    photo=news.image,
                    caption=news.caption,
                    **common_params
            )
        case News(image=None):
            await context.bot.send_video(
                    video=news.video,
                    caption=news.caption,
                    **common_params
            )
