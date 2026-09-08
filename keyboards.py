# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CHANNEL_USERNAME


def main_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🎮 O'YINNI BOSHLASH", callback_data="start_game"))
    b.row(
        InlineKeyboardButton(text="🏆 BUGUNGI REYTING", callback_data="today_rating"),
        InlineKeyboardButton(text="💰 MENING BALANSIM", callback_data="my_balance"),
    )
    b.row(
        InlineKeyboardButton(text="👤 PROFIL", callback_data="my_profile"),
        InlineKeyboardButton(text="📤 PULNI CHIQARISH", callback_data="withdraw_start"),
    )
    b.row(InlineKeyboardButton(text="ℹ️ QOIDALAR", callback_data="rules"))
    return b.as_markup()


def subscribe_kb(channels: list[str] = None) -> InlineKeyboardMarkup:
    """
    channels berilmasa faqat asosiy CHANNEL_USERNAME ko'rsatiladi.
    channels berilsa (masalan obuna bo'lmagan homiy kanallar), har biri uchun
    alohida tugma chiqadi.
    """
    b = InlineKeyboardBuilder()
    channel_list = channels if channels else ([CHANNEL_USERNAME] if CHANNEL_USERNAME else [])
    for idx, ch in enumerate(channel_list, start=1):
        link = f"https://t.me/{ch.lstrip('@')}"
        label = "📢 KANALGA OBUNA BO'LISH" if len(channel_list) == 1 else f"📢 {idx}-KANALGA OBUNA"
        b.row(InlineKeyboardButton(text=label, url=link))
    b.row(InlineKeyboardButton(text="✅ OBUNANI TEKSHIRISH", callback_data="check_subscription"))
    return b.as_markup()


def join_game_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🎮 O'YINGA QO'SHILISH", callback_data="join_game"))
    return b.as_markup()


def game_options_kb(options: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for idx, opt in enumerate(options):
        b.button(text=opt, callback_data=f"ans:{idx}")
    b.adjust(2)
    return b.as_markup()


def withdrawal_admin_kb(withdrawal_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="💸 TO'LADIM", callback_data=f"wd_paid:{withdrawal_id}"),
        InlineKeyboardButton(text="❌ RAD ETISH", callback_data=f"wd_reject:{withdrawal_id}"),
    )
    return b.as_markup()


def admin_panel_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"))
    b.row(InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"))
    b.row(InlineKeyboardButton(text="⏰ O'yin vaqtlarini sozlash", callback_data="admin_set_times"))
    b.row(InlineKeyboardButton(text="🔢 Start limit", callback_data="admin_set_limit"))
    b.row(InlineKeyboardButton(text="▶️ Hozir start berish", callback_data="admin_force_start"))
    b.row(InlineKeyboardButton(text="📢 Hammaga xabar yuborish", callback_data="admin_broadcast"))
    b.row(InlineKeyboardButton(text="🏆 Bugungi g'oliblar", callback_data="admin_winners"))
    b.row(InlineKeyboardButton(text="💸 To'lovlar", callback_data="admin_withdrawals"))
    b.row(InlineKeyboardButton(text="📣 Homiylar", callback_data="admin_sponsors"))
    b.row(InlineKeyboardButton(text="📢 Majburiy kanallar", callback_data="admin_channels"))
    return b.as_markup()


def channels_admin_kb(channels: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for ch in channels:
        b.row(InlineKeyboardButton(
            text=f"❌ {ch['title'] or ch['username']}", callback_data=f"ch_remove:{ch['id']}"
        ))
    b.row(InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="ch_add"))
    b.row(InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_back"))
    return b.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_back"))
    return b.as_markup()


def cancel_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action"))
    return b.as_markup()
