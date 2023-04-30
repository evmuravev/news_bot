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


async def set_author_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="""
*\(4\/4\) Последний шаг\! Здесь вы можете указать свое авторство либо остаться анонимным\:*
_\(100 симовлов \- ник в телеграмме\, ссылка на личный блог\, и пр\.\ Возможно\, лучших авторов будет ждать отдельная благодарность\!\)_
\n_для возврата на предудущий шаг нажмите_    ↪/back
\n_для пропуска шага нажмите_    ⏩/skip
""",
        parse_mode="MarkdownV2",
    )
    return Steps.AUTHOR


async def set_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    author = update.message.text

    if len(author) <= 100:
        news_repo = get_repository(NewsRepository, context)
        news_update = {
            'author': author,
            'status': NewsStatus.completed
        }
        await news_repo.update_news(
            news_update=NewsUpdate(**news_update),
            user_id=user.id
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Сократите ваш текст до 1000 символов\.\.\. Сейчас в нем {len(author)}",
            parse_mode="MarkdownV2",
        )
        return Steps.AUTHOR

    next_step = get_next_step(Steps.AUTHOR)
    return await next_step(update, context)


async def author_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context._user_id
    news_repo = get_repository(NewsRepository, context)
    news_update = {
        'author': 'anonymous',
        'status': NewsStatus.completed
    }
    await news_repo.update_news(
        news_update=NewsUpdate(**news_update),
        user_id=user
    )
    next_step = get_next_step(Steps.AUTHOR)
    return await next_step(update, context)


async def author_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(Steps.IMAGES)
    return await previous_step(update, context)
