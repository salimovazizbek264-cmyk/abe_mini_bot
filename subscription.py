# subscription.py
# Majburiy obuna tekshiruvi: asosiy kanal + admin qo'shgan barcha homiy kanallar

from aiogram import Bot
from config import CHANNEL_USERNAME
import database as db

VALID_STATUSES = ("member", "administrator", "creator")


async def get_mandatory_channels() -> list[str]:
    """Asosiy kanal + barcha faol homiy kanallar ro'yxati (@username formatida)"""
    channels = []
    if CHANNEL_USERNAME:
        channels.append(CHANNEL_USERNAME)
    sponsors = await db.get_active_sponsors()
    for s in sponsors:
        uname = s.get("username")
        if uname and uname not in channels:
            channels.append(uname)
    return channels


async def check_subscription(bot: Bot, user_id: int) -> tuple[bool, list[str]]:
    """
    Foydalanuvchi barcha majburiy kanallarga obuna bo'lganmi tekshiradi.
    Qaytaradi: (hammasiga_obuna_bolganmi, obuna_bolmagan_kanallar_royxati)
    """
    channels = await get_mandatory_channels()
    if not channels:
        return True, []

    not_subscribed = []
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in VALID_STATUSES:
                not_subscribed.append(channel)
        except Exception:
            # bot kanalga admin qilib qo'yilmagan yoki username noto'g'ri bo'lsa ham
            # botni to'xtatib qo'ymaslik uchun shu kanalni "obuna bo'lmagan" deb belgilaymiz
            not_subscribed.append(channel)

    return (len(not_subscribed) == 0), not_subscribed
