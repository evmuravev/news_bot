from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    profile = [
        [InlineKeyboardButton("📝Опубликовать новость", callback_data='create_news')],
    ]
    keyboard = [*profile]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="*Выберите пункт меню:*",
        reply_markup=reply_markup,
        parse_mode="MarkdownV2",
    )
