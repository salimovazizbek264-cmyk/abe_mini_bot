# keyboards.py
# ABE VAYN MINI GAME — professional inline keyboardlar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    """Asosiy /start menyusi tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 O'YINNI BOSHLASH", callback_data="start_game")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 REYTING", callback_data="today_rating"),
        InlineKeyboardButton(text="💎 BALANS", callback_data="my_balance"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 PROFIL", callback_data="my_profile"),
        InlineKeyboardButton(text="💳 PUL CHIQARISH", callback_data="claim_prize"),
    )
    builder.row(
        InlineKeyboardButton(text="📜 QOIDALAR", callback_data="rules")
    )
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_menu")
    )
    return builder.as_markup()


def game_action_kb() -> InlineKeyboardMarkup:
    """O'yin ichidagi tezkor bosish tugmasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚡ TEZROQ BOSISH! 🔥", callback_data="click_action")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_menu")
    )
    return builder.as_markup()


def admin_panel_kb() -> InlineKeyboardMarkup:
    """Professional admin panel tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏰ O'yin vaqtini o'zgartirish", callback_data="admin_set_time")
    )
    builder.row(
        InlineKeyboardButton(text="🚀 HOZIR START BERISH", callback_data="admin_force_start"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Chiqish", callback_data="back_to_menu")
    )
    return builder.as_markup()


def admin_withdraw_decision_kb(user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun pul chiqarishni tasdiqlash/rad etish"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ To'lab berdim", callback_data=f"wd_yes_{user_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"wd_no_{user_id}")
    )
    return builder.as_markup()
