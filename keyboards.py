# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 O'YINNI BOSHLASH", callback_data="start_game"),
        InlineKeyboardButton(text="⚔️ JONLI DUET (1 vs 1)", callback_data="live_duet")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 REYTING", callback_data="today_rating"),
        InlineKeyboardButton(text="💎 BALANS", callback_data="my_balance"),
    )
    builder.row(
        InlineKeyboardButton(text="👤 PROFIL", callback_data="my_profile"),
        InlineKeyboardButton(text="👥 DO'STLAR (REFERAL)", callback_data="referral_menu")
    )
    builder.row(
        InlineKeyboardButton(text="💳 PUL CHIQARISH", callback_data="claim_prize"),
        InlineKeyboardButton(text="📜 QOIDALAR", callback_data="rules")
    )
    return builder.as_markup()

def check_sub_kb(channels: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(InlineKeyboardButton(text=f"📢 {ch.get('title', 'Kanal')}", url=ch.get('url', 'https://t.me/')))
    builder.row(InlineKeyboardButton(text="✅ A'zo bo'ldim", callback_data="check_subscription"))
    return builder.as_markup()

def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_menu"))
    return builder.as_markup()

def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏰ O'yin vaqtlarini sozlash", callback_data="admin_set_times"))
    builder.row(
        InlineKeyboardButton(text="📢 Majburiy kanal qo'shish", callback_data="admin_add_channel"),
        InlineKeyboardButton(text="📢 Hammaga xabar yuborish", callback_data="admin_broadcast"),
    )
    builder.row(
        InlineKeyboardButton(text="🚀 HOZIR START BERISH", callback_data="admin_force_start"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Chiqish", callback_data="back_to_menu"))
    return builder.as_markup()

def admin_withdraw_decision_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ To'lab berdim", callback_data=f"wd_yes_{user_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"wd_no_{user_id}")
    )
    return builder.as_markup()
