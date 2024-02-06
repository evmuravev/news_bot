import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.repositories.news import NewsRepository
from db.tasks import get_repository
from handlers.create_news.common import (
    Steps,
    get_next_step
)
from models.news import NewsStatus, NewsUpdate


logger = logging.getLogger()


async def set_text_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Добавьте текстовое описание новости *\n_\(Следуйте правилам, смело расставляйте \#тэги и постарайтесь уложиться в 1000 символов\)_",
        parse_mode="MarkdownV2",
    )

    return Steps.TEXT


async def set_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    if len(text) <= 1000:
        news_repo = get_repository(NewsRepository, context)
        news_update = {
            'text': text,
            'status': NewsStatus.partially_completed
        }
        await news_repo.update_news(
            news_update=NewsUpdate(**news_update),
            user_id=user.id
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Сократите ваш текст до 1000 символов\.\.\. Сейчас в нем {len(text)}",
            parse_mode="MarkdownV2",
        )
        return Steps.TEXT

    next_step = get_next_step(Steps.TEXT)
    return await next_step(update, context)
