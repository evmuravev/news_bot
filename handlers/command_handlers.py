from telegram.ext import CommandHandler
from handlers.create_news import create_news
from handlers.menu import menu
from handlers.start import start


COMMAND_HANDLERS = [
    CommandHandler("start", start.start),
    CommandHandler("menu", menu.menu),
    CommandHandler("create_news", create_news.create_news)
]
