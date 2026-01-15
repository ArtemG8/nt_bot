import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config.config import conf
from handlers import private_user

# Настройка логирования
logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info("Starting bot...")

    # Проверка наличия токена
    if not conf.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return

    storage = MemoryStorage()

    # Инициализируем бота и диспетчера
    bot = Bot(
        token=conf.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры
    dp.include_router(private_user.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
