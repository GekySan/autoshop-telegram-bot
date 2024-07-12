import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import TOKEN
from bot.handlers import start, callback, gift, admin
from bot.utils.db import init_db
from bot.utils.payment import check_and_process_logs

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    init_db()

    start.register_handlers(dp)
    callback.register_handlers(dp)
    gift.register_gift_handlers(dp)
    admin.register_admin_handlers(dp)

    asyncio.create_task(check_and_process_logs(bot))

    print("Bot is running. Press CTRL+C to stop.")

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
