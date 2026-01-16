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
    # Путь к видеофайлу относительно корня проекта (например: "videos/about.mp4")
    ABOUT_VIDEO_PATH: str = os.getenv("ABOUT_VIDEO_PATH", "")
    # file_id видео в Telegram (получается автоматически при первой загрузке)
    ABOUT_VIDEO_FILE_ID: str = os.getenv("ABOUT_VIDEO_FILE_ID", "")
    
    @property
    def about_video_full_path(self) -> Path | None:
        """Возвращает полный путь к видеофайлу, если он указан и существует"""
        if not self.ABOUT_VIDEO_PATH:
            return None
        video_path = BASE_DIR / self.ABOUT_VIDEO_PATH
        return video_path if video_path.exists() else None

# Создаем экземпляр конфигурации
conf = Config()
