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
from models.news import NewsUpdate


logger = logging.getLogger()


async def set_images_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    news_repo = get_repository(NewsRepository, context)
    news_update = {'images': None}
    await news_repo.update_news(
        news_update=NewsUpdate(**news_update),
        user_id=context._user_id
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="""
*\(2\/4\) Отлично\! Теперь приложите до трех изображений, если они есть*
\n_для возврата на предудущий шаг нажмите_    ↪/back
\n_для пропуска шага нажмите_    ⏩/skip
""",
        parse_mode="MarkdownV2",
    )
    return Steps.IMAGES


async def set_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_repo = get_repository(NewsRepository, context)

    user = update.message.from_user
    image = update.message.photo[0].file_id

    num_images = await news_repo.add_images(user_id=user.id, image=image)
    await update.message.reply_text(
        f"""Получено {num_images} изображение\!\n_приложите еще или нажмите  /skip ⏩_""",
        parse_mode="MarkdownV2",
    )

    # If the user has sent 3 images, end the conversation
    if num_images == 3:
        await update.message.reply_text(
            "Все изображения загружены!"
        )
        next_step = get_next_step(Steps.IMAGES)
        return await next_step(update, context)

    return Steps.IMAGES


async def images_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(Steps.IMAGES)
    return await previous_step(update, context)


async def images_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    next_step = get_next_step(Steps.IMAGES)
    return await next_step(update, context)
