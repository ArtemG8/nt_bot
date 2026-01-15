"""
Обработчики для приватных сообщений пользователей
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery

from lexicon.lexicon_ru import (
    WELCOME_MESSAGE, MAIN_MENU_TEXT, ABOUT_TEXT,
    TARIFFS_TEXT, SUPPORT_TEXT_TEMPLATE, AFTER_PAYMENT_TEXT_TEMPLATE,
    BUTTON_ABOUT, BUTTON_SUBSCRIBE, BUTTON_SUPPORT, BUTTON_BACK
)
from keyboards.keyboard_utils import (
    get_main_menu_keyboard, get_tariffs_keyboard, get_back_keyboard
)
from config.config import conf

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start - приветственное сообщение без кнопок"""
    await message.answer(
        text=WELCOME_MESSAGE,
        reply_markup=None
    )
    # Отправляем главное меню через небольшую задержку
    await message.answer(
        text=MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == BUTTON_ABOUT)
async def show_about(message: Message):
    """Обработчик кнопки 'Подробнее'"""
    await message.answer(
        text=ABOUT_TEXT,
        reply_markup=get_back_keyboard()
    )
    # Здесь можно добавить отправку видеоролика, если он есть
    # await message.answer_video(video="FILE_ID_VIDEO")


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
        text=MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "tariff_views")
async def process_tariff_views(callback: CallbackQuery):
    """Обработчик выбора тарифа 'Охваты'"""
    await callback.answer()
    await callback.message.answer(
        text=f"💳 Тариф: Охваты\n\n"
             f"Для оформления подписки свяжитесь с менеджером: \n\n"
             "После оплаты перешлите чек менеджеру @{conf.MANAGER_USERNAME}",
        reply_markup=get_back_keyboard()
    )
#Для оформления подписки отправьте сумму (x) по реквизитам 123-456-789 MoneyBank

@router.callback_query(F.data == "tariff_reactions")
async def process_tariff_reactions(callback: CallbackQuery):
    """Обработчик выбора тарифа 'Реакции'"""
    await callback.answer()
    await callback.message.answer(
        text=f"💳 Тариф: Реакции\n\n"
             f"Для оформления подписки свяжитесь с менеджером: @{conf.MANAGER_USERNAME}\n\n"
             "После оплаты перешлите чек менеджеру.",
        reply_markup=get_back_keyboard()
    )


@router.callback_query(F.data == "tariff_both")
async def process_tariff_both(callback: CallbackQuery):
    """Обработчик выбора тарифа 'Охваты + Реакции'"""
    await callback.answer()
    await callback.message.answer(
        text=f"💳 Тариф: Охваты + Реакции (скидка 30%)\n\n"
             f"Для оформления подписки свяжитесь с менеджером: @{conf.MANAGER_USERNAME}\n\n"
             "После оплаты перешлите чек менеджеру.",
        reply_markup=get_back_keyboard()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Назад' в inline клавиатуре"""
    await callback.answer()
    await callback.message.answer(
        text=MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.successful_payment)
async def process_payment(message: Message):
    """Обработчик успешной оплаты через Telegram Payments"""
    await message.answer(
        text=AFTER_PAYMENT_TEXT_TEMPLATE.format(manager_username=conf.MANAGER_USERNAME),
        reply_markup=get_back_keyboard()
    )


@router.message(F.photo | F.document)
async def handle_receipt(message: Message):
    """Обработчик получения фото/документа (чек) для пересылки менеджеру"""
    manager_username = conf.MANAGER_USERNAME
    
    # Отправляем подтверждение пользователю
    await message.answer(
        text=f"✅ Чек получен! Мы переслали его менеджеру @{manager_username}.\n\n"
             "Ожидайте обработки заказа.",
        reply_markup=get_back_keyboard()
    )
    
    # Пересылаем чек менеджеру, если указан chat_id
    if conf.MANAGER_CHAT_ID:
        try:
            bot = message.bot
            user_info = f"Пользователь: @{message.from_user.username or 'без username'}\nID: {message.from_user.id}\nИмя: {message.from_user.full_name}"
            await bot.send_message(
                chat_id=conf.MANAGER_CHAT_ID,
                text=f"📋 Новый чек об оплате\n\n{user_info}"
            )
            await bot.forward_message(
                chat_id=conf.MANAGER_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        except Exception as e:
            # Если не удалось переслать, просто логируем ошибку
            logger.error(f"Ошибка при пересылке чека менеджеру: {e}")
