from telegram import Update
from telegram.ext import ContextTypes
from handlers.menu.menu import menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await menu(update, context)
