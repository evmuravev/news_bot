import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db.repositories.news import NewsRepository
from db.tasks import get_repository
from handlers.create_news.common import (
    Steps,
    get_next_step,
    get_previous_step
)
from models.news import NewsUpdate


logger = logging.getLogger()


async def set_video_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="""
*\(3\/4\) Хорошо\! Теперь приложите видеофайл, если есть*
\n_для возврата на предудущий шаг нажмите_    ↪/back
\n_для пропуска шага нажмите_    ⏩/skip
""",
        parse_mode="MarkdownV2",
    )

    return Steps.VIDEO


async def set_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context._user_id
    video = update.message.video.file_id
    news_repo = get_repository(NewsRepository, context)
    news_update = {
        'video': video
    }
    await news_repo.update_news(
        news_update=NewsUpdate(**news_update),
        user_id=user_id
    )
    next_step = get_next_step(Steps.VIDEO)
    return await next_step(update, context)


async def video_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(Steps.VIDEO)
    return await previous_step(update, context)


async def video_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(Steps.VIDEO)
    return await next_step(update, context)
