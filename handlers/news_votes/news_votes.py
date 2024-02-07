import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    ContextTypes,
)
from core.config import TELEGRAM_CHANNEL_ID
from db.repositories.news_votes import NewsVotesRepository
from db.repositories.news import NewsRepository
from db.repositories.users import UsersRepository
from db.tasks import get_repository

from handlers.common.users import get_user
from models.news import NewsStatus, NewsUpdate
from models.user import UserPublic


logger = logging.getLogger()


async def delete_news(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        news_id: int
) -> None:
    news_repo: NewsRepository = get_repository(NewsRepository, context)
    user_repo: UsersRepository = get_repository(UsersRepository, context)
    user_repo = get_repository(UsersRepository, context)
    news = await news_repo.get_news_by_id(id=news_id)
    user = await user_repo.get_user_by_id(id=news.user_id)
    if user.is_admin:
        return

    updated_user = await user_repo.inc_num_of_complains(user_id=news.user_id)
    # Если больше 2, то в бан!
    if updated_user.num_of_complains > 2:
        await user_repo.update_is_banned(user_id=updated_user.id)
        await context.bot.send_message(
            chat_id=updated_user.id,
            text='Нам очень жаль, Ваши новости негативно оценены аудиторией канала. Вы были забанены и больше не можете публиковать новости!',
        )
    else:
        await context.bot.send_message(
            chat_id=updated_user.id,
            text='Участники канала негативно оценили Вашу новость и она была удалена! Повторный отрицательный рейтинг на двух следующих новостях приведут Вас к бану!',
        )

    # Обновляем статус новости
    news_update = {
        'status': NewsStatus.deleted
    }
    await news_repo.update_news(
        news_update=NewsUpdate(**news_update),
        news_id=news.id
    )

    # Удаляем новость из канала
    try:
        await context.bot.delete_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            message_id=update.effective_message.message_id
        )
    except BadRequest as ex:
        logger.warning(ex)


async def news_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_user: UserPublic = await get_user(update, context)
    news_votes_repo: NewsVotesRepository = get_repository(NewsVotesRepository, context)
    news_id = int(update.callback_query.data.split(':')[1])

    if current_user and current_user.is_admin:
        await delete_news(update, context, news_id)

    rating = await news_votes_repo.news_downvote(
        news_id=news_id,
        user_id=context._user_id
    )
    await context.bot.answer_callback_query(
        callback_query_id=update.callback_query.id,
        show_alert=True,
        text='Спасибо, ваш голос учтён!',
    )

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Рейтинг: {rating}", callback_data=f'rating')],
            [
                InlineKeyboardButton("👍", callback_data=f'approve:{news_id}'),
                InlineKeyboardButton("👎", callback_data=f'decline:{news_id}'),
            ]
        ]
    )
    try:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
    except BadRequest as ex:
        logger.warning(ex)

    if rating <= -5:
        await delete_news(update, context, news_id)


async def news_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news_votes_repo: NewsVotesRepository = get_repository(NewsVotesRepository, context)
    news_id = int(update.callback_query.data.split(':')[1])

    rating = await news_votes_repo.news_upvote(
        news_id=news_id,
        user_id=context._user_id
    )
    await context.bot.answer_callback_query(
        callback_query_id=update.callback_query.id,
        show_alert=True,
        text='Спасибо, ваш голос учтён!',
    )

    reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"Рейтинг: {rating}", callback_data=f'rating')],
            [
                InlineKeyboardButton("👍", callback_data=f'approve:{news_id}'),
                InlineKeyboardButton("👎", callback_data=f'decline:{news_id}'),
            ]
        ]
    )
    try:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
    except BadRequest as ex:
        logger.warning(ex)
