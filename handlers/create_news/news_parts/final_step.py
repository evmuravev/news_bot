import logging
from typing import Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes, ConversationHandler
from core.config import TELEGRAM_CHANNEL_ID
from db.repositories.news import NewsRepository
from db.repositories.news_votes import NewsVotesRepository
from db.tasks import get_repository
from handlers.common.users import get_user
from handlers.menu import menu
from handlers.show_news import show_news_handler, show_news
from handlers.create_news.common import (
    Steps,
    get_previous_step
)
from handlers.create_news.news_parts.text import set_text_step
from models.news import NewsBase, NewsStatus, NewsUpdate
from models.news_votes import NewsVotesCreate
from models.user import UserPublic


logger = logging.getLogger()


async def set_final_step(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):


    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Все почти готово\! Так выглядит ваша новость\.*\n ↪/back",
        parse_mode="MarkdownV2",
    )

    await show_news_handler(update, context)
    options = [
        [
            InlineKeyboardButton("🔃 Заново", callback_data='start_over'),
            InlineKeyboardButton("Далее ⏩", callback_data='final_step'),
        ]
    ]
    keyboard = [*options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Публикуем или переделываем\?*",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )
    return Steps.FINAL_STEP


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.callback_query.from_user
    news_repo: NewsRepository = get_repository(NewsRepository, context)
    news = await news_repo.get_last_news_by_user_id(user_id=user.id)
    await news_repo.update_news(
        news_update=NewsBase(),
        news_id=news.id,
        exclude_unset=False
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text='Созданная новость очищена - начинаем сначала :)',
    )
    return await set_text_step(update, context)


async def final_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    previous_step = get_previous_step(Steps.FINAL_STEP)
    return await previous_step(update, context)


async def final_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)
    news_repo: NewsRepository = get_repository(NewsRepository, context)
    news = await news_repo.get_last_news_by_user_id(user_id=user.id)

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Рейтинг: 0", callback_data=f'rating')],
            [
                InlineKeyboardButton("👍", callback_data=f'approve:{news.id}'),
                InlineKeyboardButton("👎", callback_data=f'decline:{news.id}'),
            ]
        ]
    )
    news_post = await show_news(user, context)

    common_params = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "parse_mode": "MarkdownV2",
        "reply_markup": reply_markup,
    }
    match news_post:
        case object(image=None, video=None):
            message = await context.bot.send_message(
                text=news_post.caption,
                **common_params
            )
        case object(video=None):
            message = await context.bot.send_photo(
                photo=news_post.image,
                caption=news_post.caption,
                **common_params
            )
        case object(image=None):
            message = await context.bot.send_video(
                video=news_post.video,
                caption=news_post.caption,
                **common_params
            )

    news_update = {
        'message_id': message.id,
        'status': NewsStatus.published
    }

    await news_repo.update_news(
        news_update=NewsUpdate(**news_update),
        news_id=news.id
    )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f'''💪 Ваша новость опубликована! \nПомните, если рейтинг вашей новости станет ниже -5, она будет удалена, и это будет считаться за предупреждение!
\n Перейти в канал: {TELEGRAM_CHANNEL_ID}
''',
    )
    await menu.menu(update, context)

    return ConversationHandler.END
