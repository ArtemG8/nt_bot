"""
Обработчики для приватных сообщений пользователей
"""
import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile

from lexicon.lexicon_ru import (
    WELCOME_MESSAGE, MAIN_MENU_TEXT, ABOUT_TEXT,
    TARIFFS_TEXT, SUPPORT_TEXT_TEMPLATE, AFTER_PAYMENT_TEXT_TEMPLATE,
    BUTTON_ABOUT, BUTTON_SUBSCRIBE, BUTTON_SUPPORT, BUTTON_BACK,
    TARIFF_VIEWS_TEXT_TEMPLATE, TARIFF_REACTIONS_TEXT_TEMPLATE,
    TARIFF_BOTH_TEXT_TEMPLATE, RECEIPT_RECEIVED_TEXT_TEMPLATE,
    NEW_RECEIPT_NOTIFICATION, USER_INFO_TEMPLATE, NO_USERNAME,
    ERROR_RECEIPT_FORWARD
)
from keyboards.keyboard_utils import (
    get_main_menu_keyboard, get_tariffs_keyboard, get_back_keyboard
)
from config.config import conf, BASE_DIR
from utils.video_uploader import ensure_video_file_id, save_file_id_to_env

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start - приветственное сообщение с главным меню"""
    await message.answer(
        text=WELCOME_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == BUTTON_ABOUT)
async def show_about(message: Message):
    """Обработчик кнопки 'Подробнее'"""
    # Получаем file_id последнего видео из MANAGER_CHAT_ID
    file_id = await ensure_video_file_id(message.bot)
    
    if file_id:
        try:
            # Используем file_id для мгновенной отправки
            # Пробуем отправить как видео, если не получится - как документ
            try:
                await message.answer_video(
                    video=file_id,
                    caption=ABOUT_TEXT,
                    supports_streaming=True,
                    reply_markup=get_back_keyboard()
                )
                logger.info("Видео успешно отправлено по file_id")
            except Exception as video_error:
                logger.debug(f"Не удалось отправить как видео, пробую как документ: {video_error}")
                # Если не получилось как видео, пробуем как документ
                await message.answer_document(
                    document=file_id,
                    caption=ABOUT_TEXT,
                    reply_markup=get_back_keyboard()
                )
                logger.info("Видео отправлено как документ по file_id")
        except Exception as e:
            logger.error(f"Ошибка при отправке видео по file_id: {e}", exc_info=True)
            await message.answer(
                text=ABOUT_TEXT,
                reply_markup=get_back_keyboard()
            )
    else:
        # Если видео не найдено, отправляем только текст
        logger.info("Видео не найдено в MANAGER_CHAT_ID")
        await message.answer(
            text=ABOUT_TEXT,
            reply_markup=get_back_keyboard()
        )


@router.message(F.text == BUTTON_SUBSCRIBE)
async def show_tariffs(message: Message):
    """Обработчик кнопки 'Оформить подписку'"""
    await message.answer(
        text=TARIFFS_TEXT,
        reply_markup=get_tariffs_keyboard()
    )


@router.message(F.text == BUTTON_SUPPORT)
async def show_support(message: Message):
    """Обработчик кнопки 'Поддержка'"""
    await message.answer(
        text=SUPPORT_TEXT_TEMPLATE.format(manager_username=conf.MANAGER_USERNAME),
        reply_markup=get_back_keyboard()
    )


@router.message(F.text == BUTTON_BACK)
async def back_to_menu(message: Message):
    """Обработчик кнопки 'Назад' - возврат в главное меню"""
    await message.answer(
        text=WELCOME_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "tariff_views")
async def process_tariff_views(callback: CallbackQuery):
    """Обработчик выбора тарифа 'Охваты'"""
    await callback.answer()
    await callback.message.answer(
        text=TARIFF_VIEWS_TEXT_TEMPLATE.format(manager_username=conf.MANAGER_USERNAME),
        reply_markup=get_back_keyboard()
    )

@router.callback_query(F.data == "tariff_reactions")
async def process_tariff_reactions(callback: CallbackQuery):
    """Обработчик выбора тарифа 'Реакции'"""
    await callback.answer()
    await callback.message.answer(
        text=TARIFF_REACTIONS_TEXT_TEMPLATE.format(manager_username=conf.MANAGER_USERNAME),
        reply_markup=get_back_keyboard()
    )


@router.callback_query(F.data == "tariff_both")
async def process_tariff_both(callback: CallbackQuery):
    """Обработчик выбора тарифа 'Охваты + Реакции'"""
    await callback.answer()
    await callback.message.answer(
        text=TARIFF_BOTH_TEXT_TEMPLATE.format(manager_username=conf.MANAGER_USERNAME),
        reply_markup=get_back_keyboard()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Назад' в inline клавиатуре"""
    await callback.answer()
    await callback.message.edit_reply_markup(
        reply_markup=None
    )
    await callback.message.answer(
        text=WELCOME_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.successful_payment)
async def process_payment(message: Message):
    """Обработчик успешной оплаты через Telegram Payments"""
    await message.answer(
        text=AFTER_PAYMENT_TEXT_TEMPLATE.format(manager_username=conf.MANAGER_USERNAME),
        reply_markup=get_back_keyboard()
    )


async def process_video_message(message: Message):
    """Обрабатывает сообщение с видео и обновляет file_id"""
    # Проверяем, что сообщение пришло из MANAGER_CHAT_ID
    if str(message.chat.id) == str(conf.MANAGER_CHAT_ID):
        file_id = None
        
        if message.video:
            file_id = message.video.file_id
            logger.info(f"Получено новое видео в MANAGER_CHAT_ID (как видео): {file_id}")
        elif message.document:
            file_id = message.document.file_id
            logger.info(f"Получено новое видео в MANAGER_CHAT_ID (как документ): {file_id}")
        
        if file_id:
            # Сохраняем новый file_id
            await save_file_id_to_env(file_id)
            # Обновляем в конфиге
            import os
            from dotenv import load_dotenv
            load_dotenv(override=True)
            conf.ABOUT_VIDEO_FILE_ID = os.getenv("ABOUT_VIDEO_FILE_ID", file_id)
            logger.info(f"✅ file_id обновлен: {file_id}")
            
            # Отправляем уведомление в MANAGER_CHAT_ID
            try:
                await message.bot.send_message(
                    chat_id=conf.MANAGER_CHAT_ID,
                    text="✅ Видео загружено и изменено"
                )
                logger.info("Уведомление отправлено в MANAGER_CHAT_ID")
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления: {e}", exc_info=True)


@router.message(F.video | (F.document & F.document.mime_type.startswith("video/")))
async def handle_video_in_manager_chat(message: Message):
    """Обработчик получения видео в MANAGER_CHAT_ID - автоматически обновляет file_id
    Работает для обычных чатов и каналов (если бот является администратором)
    """
    await process_video_message(message)


@router.message(F.photo | F.document)
async def handle_receipt(message: Message):
    """Обработчик получения фото/документа (чек) для пересылки менеджеру"""
    # Пропускаем видео - они обрабатываются отдельным обработчиком
    if message.document and message.document.mime_type and message.document.mime_type.startswith("video/"):
        return
    
    manager_username = conf.MANAGER_USERNAME
    
    # Отправляем подтверждение пользователю
    await message.answer(
        text=RECEIPT_RECEIVED_TEXT_TEMPLATE.format(manager_username=manager_username),
        reply_markup=get_back_keyboard()
    )
    
    # Пересылаем чек менеджеру, если указан chat_id
    if conf.MANAGER_CHAT_ID:
        try:
            bot = message.bot
            user_info = USER_INFO_TEMPLATE.format(
                username=message.from_user.username or NO_USERNAME,
                user_id=message.from_user.id,
                full_name=message.from_user.full_name
            )
            await bot.send_message(
                chat_id=conf.MANAGER_CHAT_ID,
                text=f"{NEW_RECEIPT_NOTIFICATION}\n\n{user_info}"
            )
            await bot.forward_message(
                chat_id=conf.MANAGER_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        except Exception as e:
            # Если не удалось переслать, просто логируем ошибку
            logger.error(ERROR_RECEIPT_FORWARD.format(error=e))
