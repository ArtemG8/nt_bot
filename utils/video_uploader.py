"""
получение file_id последнего видео из MANAGER_CHAT_ID
"""
import logging
from aiogram import Bot

from config.config import conf, BASE_DIR

logger = logging.getLogger(__name__)


async def ensure_video_file_id(bot: Bot = None) -> str | None:
    """
    Получает file_id последнего видео из MANAGER_CHAT_ID
    Если file_id уже есть в конфиге, возвращает его
    Новые видео автоматически обновляются через обработчик сообщений
    """
    # Если file_id уже есть, используем его
    if conf.ABOUT_VIDEO_FILE_ID:
        logger.debug(f"Используется сохраненный file_id: {conf.ABOUT_VIDEO_FILE_ID}")
        return conf.ABOUT_VIDEO_FILE_ID
    
    # Если file_id нет, пытаемся найти последнее видео
    logger.info("file_id не найден. Ожидаю новое видео в MANAGER_CHAT_ID...")
    logger.info("💡 Отправьте видео в чат/канал с MANAGER_CHAT_ID, и оно автоматически будет использовано")
    
    return None


async def save_file_id_to_env(file_id: str):
    """
    Сохраняет file_id в .env
    """
    env_file = BASE_DIR / ".env"
    
    try:
        # Читаем текущий .env файл
        env_content = ""
        if env_file.exists():
            env_content = env_file.read_text(encoding='utf-8')

        lines = env_content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('ABOUT_VIDEO_FILE_ID='):
                lines[i] = f'ABOUT_VIDEO_FILE_ID={file_id}'
                updated = True
                break

        if not updated:
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f'ABOUT_VIDEO_FILE_ID={file_id}\n'
            lines = env_content.split('\n')

        env_file.write_text('\n'.join(lines), encoding='utf-8')
        logger.info(f"file_id сохранен в .env файл: {file_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении file_id в .env: {e}", exc_info=True)
