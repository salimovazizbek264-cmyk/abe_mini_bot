# keyboards.py
# ABE VAYN MINI GAME — inline keyboardlar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    """Asosiy /start menyusi tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 O'YINNI BOSHLASH", callback_data="start_game")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 BUGUNGI REYTING", callback_data="today_rating"),
        InlineKeyboardButton(text="💰 MENING BALANSIM", callback_data="my_balance"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 PROFIL", callback_data="my_profile"),
        InlineKeyboardButton(text="📤 SOVRINNI OLISH", callback_data="claim_prize"),
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ QOIDALAR", callback_data="rules")
    )
    return builder.as_markup()


def join_game_kb() -> InlineKeyboardMarkup:
    """1000 taga yetmagan holatdagi tugma"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎮 O'YINGA QO'SHILISH", callback_data="join_game")
    )
    return builder.as_markup()


def game_unlocked_kb() -> InlineKeyboardMarkup:
    """1000 ishtirokchi to'lgandagi tugma"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚡ O'YINNI BOSHLASH", callback_data="start_game")
    )
    return builder.as_markup()


def admin_panel_kb() -> InlineKeyboardMarkup:
    """Admin panel tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="▶️ HOZIR START BERISH", callback_data="admin_force_start")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
        InlineKeyboardButton(text="📢 Kanal qo'shish", callback_data="admin_add_channel"),
    )
    return builder.as_markup()