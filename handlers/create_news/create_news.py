import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)

from db.tasks import get_repository
from db.repositories.news import NewsRepository
from models.news import NewsBase, NewsCreate, NewsStatus
from models.user import UserPublic
from handlers.create_news.news_parts import (
    author, image, cancel, text, final_step, video
)
from handlers.create_news.common import Steps
from handlers.common.users import get_user, register_new_user


logger = logging.getLogger()


async def create_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user: UserPublic = await get_user(update, context)

    if user and user.is_banned:
        await context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            show_alert=True,
            text='Вы были забанены и больше не можете пуликовать новости!',
        )
        return

    if not user:
        user = await register_new_user(update, context)

    news_repo: NewsRepository = get_repository(NewsRepository, context)
    news = await news_repo.get_last_news_by_user_id(user_id=user.id)
    if not news or news.status in (NewsStatus.published, NewsStatus.deleted):
        news_create = NewsCreate(user_id=user.id)
        await news_repo.create_news(
            news_create=news_create
        )
    else:
        await news_repo.update_news(
            news_update=NewsBase(),
            user_id=user.id,
            exclude_unset=False,
        )

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="""
*Пройдите все шаги для опубликования новости*
_\(добавление текста обязательно\, фото или видео \- опционально\)_
\n*Запрещены\:\n• спам, флуд и пр\.\n• бессмысленное содержание\n• любая реклама\n• незацензуренные мат\, обнаженка и сцены насилия\n• все\, что запрещено действующими законами РФ*
\n*За одно нарушение \- предупреждение\, за повторное \- бан\!*
""",
        parse_mode="MarkdownV2",
    )

    return await text.set_text_step(update, context)


CREATE_NEWS_CONVERSATION = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CommandHandler('create_news', create_news),
        CallbackQueryHandler(create_news, pattern='create_news')],

    states={
        Steps.TEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, text.set_text),
        ],
        Steps.IMAGE: [
            MessageHandler(filters.PHOTO, image.set_image),
            CommandHandler('skip', image.image_skip),
            CommandHandler('back', image.image_back),
        ],
        Steps.VIDEO: [
            MessageHandler(filters.VIDEO, video.set_video),
            CommandHandler('back', video.video_back),
            CommandHandler('skip', video.video_skip),
        ],
        Steps.AUTHOR: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, author.set_author),
            CommandHandler('back', author.author_back),
            CommandHandler('skip', author.author_skip),
        ],
        Steps.FINAL_STEP: [
            CallbackQueryHandler(final_step.start_over, pattern='start_over'),
            CallbackQueryHandler(final_step.final_step, pattern='final_step'),
            CommandHandler('back', final_step.final_back),
        ],
    },

    fallbacks=[CommandHandler('cancel', cancel.cancel)],
)
