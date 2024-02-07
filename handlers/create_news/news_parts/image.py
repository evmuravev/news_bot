import logging
from telegram import Update
from telegram.ext import ContextTypes
from db.repositories.news import NewsRepository
from db.tasks import get_repository
from handlers.create_news.common import (
    Steps,
    get_next_step,
    get_previous_step
)
from models.news import NewsStatus, NewsUpdate


logger = logging.getLogger()


async def set_image_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    news_repo: NewsRepository = get_repository(NewsRepository, context)
    news = await news_repo.get_last_news_by_user_id(user_id=context._user_id)
    news_update = {
        'image': None,
        'status': NewsStatus.partially_completed
    }
    await news_repo.update_news(
        news_update=NewsUpdate(**news_update),
        news_id=news.id,
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="""
*Отлично\! Теперь приложите изображание, если оно есть, или перейдите к следующему шагу для вставки видео*
\n_для возврата на предудущий шаг нажмите_    ↪/back
\n_для пропуска шага нажмите_    ⏩/skip
""",
        parse_mode="MarkdownV2",
    )
    return Steps.IMAGE


async def set_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image = update.message.photo[0].file_id

    news_repo: NewsRepository = get_repository(NewsRepository, context)
    news = await news_repo.get_last_news_by_user_id(user_id=context._user_id)
    news_update = {'image': image}
    await news_repo.update_news(
        news_update=NewsUpdate(**news_update),
        news_id=news.id
    )
    await update.message.reply_text(
        "Изображение успешно загружено",
    )

    next_step = get_next_step(Steps.IMAGE)
    return await next_step(update, context)


async def image_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(Steps.IMAGE)
    return await previous_step(update, context)


async def image_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(Steps.IMAGE_SKIP)
    return await next_step(update, context)
