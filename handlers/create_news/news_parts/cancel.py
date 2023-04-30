import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


logger = logging.getLogger()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Пользователь %s отменил создание.", user.first_name)
    await update.message.reply_text(
        'Вы отменили создание профиля, если передумаете - всегда можете продолжить создание в другое время!'
    )

    return ConversationHandler.END
