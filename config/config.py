import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Базовый путь проекта
BASE_DIR = Path(__file__).parent.parent

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    MANAGER_USERNAME: str = os.getenv("MANAGER_USERNAME", "Мэнеджер_юзер")
    MANAGER_CHAT_ID: str = os.getenv("MANAGER_CHAT_ID", "")
    # file_id видео в Telegram (получается автоматически при отправке видео в MANAGER_CHAT_ID)
    ABOUT_VIDEO_FILE_ID: str = os.getenv("ABOUT_VIDEO_FILE_ID", "")

# Создаем экземпляр конфигурации
conf = Config()
