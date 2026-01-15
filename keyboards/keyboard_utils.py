"""
Утилиты для создания клавиатур
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon_ru import (
    BUTTON_ABOUT, BUTTON_SUBSCRIBE, BUTTON_SUPPORT,
    BUTTON_BACK, BUTTON_TARIFF_VIEWS, BUTTON_TARIFF_REACTIONS, BUTTON_TARIFF_BOTH
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру главного меню"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=BUTTON_ABOUT),
        KeyboardButton(text=BUTTON_SUBSCRIBE)
    )
    builder.row(KeyboardButton(text=BUTTON_SUPPORT))
    return builder.as_markup(resize_keyboard=True)


def get_tariffs_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру выбора тарифов"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=BUTTON_TARIFF_VIEWS,
        callback_data="tariff_views"
    ))
    builder.row(InlineKeyboardButton(
        text=BUTTON_TARIFF_REACTIONS,
        callback_data="tariff_reactions"
    ))
    builder.row(InlineKeyboardButton(
        text=BUTTON_TARIFF_BOTH,
        callback_data="tariff_both"
    ))
    builder.row(InlineKeyboardButton(
        text=BUTTON_BACK,
        callback_data="back_to_menu"
    ))
    return builder.as_markup()


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру с кнопкой назад"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=BUTTON_BACK))
    return builder.as_markup(resize_keyboard=True)
