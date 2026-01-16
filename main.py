import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config.config import conf
from handlers import private_user
from utils.video_uploader import ensure_video_file_id

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
    
    # Проверяем последнее видео в MANAGER_CHAT_ID
    if conf.MANAGER_CHAT_ID:
        logger.info("Проверяю последнее видео в MANAGER_CHAT_ID...")
        try:
            file_id = await ensure_video_file_id(bot)
            if file_id:
                logger.info(f"✅ Найдено видео, file_id: {file_id}")
            else:
                logger.warning("⚠️ Видео не найдено. Отправьте видео в чат/канал с MANAGER_CHAT_ID")
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке видео: {e}", exc_info=True)
    else:
        logger.warning("MANAGER_CHAT_ID не указан. Укажите его в .env для автоматического поиска видео")
    
    logger.info("Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
