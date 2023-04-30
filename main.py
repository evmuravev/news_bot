import asyncio
from telegram.ext import ApplicationBuilder
from core import config, tasks
import nest_asyncio
nest_asyncio.apply()


async def main(token):
    application = (
        ApplicationBuilder()
        .token(token)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .pool_timeout(60)
        .build()
    )
    await tasks.start_bot(application)


if __name__ == '__main__':
    asyncio.run(main(config.TELEGRAM_BOT_TOKEN))
