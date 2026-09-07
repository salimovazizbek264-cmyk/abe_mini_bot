# handlers.py
# ABE VAYN MINI GAME — asosiy handlerlar (demo/in-memory versiya)

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import texts
import keyboards as kb

router = Router()

# ------------------------------------------------------------------
# DEMO uchun oddiy xotira (keyinchalik Postgres bilan almashtiriladi)
# ------------------------------------------------------------------
PARTICIPANTS = set()          # o'yinga qo'shilgan user_id'lar
REQUIRED_PARTICIPANTS = 1000
GAME_TIME_TEXT = "10:00"
ADMIN_USERNAME = "abe_vlog"
ADMIN_IDS = {8007670371}      # <-- @abe_vlog


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ------------------------------------------------------------------
# /start
# ------------------------------------------------------------------
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(texts.WELCOME, reply_markup=kb.main_menu_kb())


# ------------------------------------------------------------------
# Asosiy menyu tugmalari
# ------------------------------------------------------------------
@router.callback_query(F.data == "start_game")
async def cb_start_game(call: CallbackQuery):
    current = len(PARTICIPANTS)
    if current < REQUIRED_PARTICIPANTS:
        remaining = REQUIRED_PARTICIPANTS - current
        text = texts.NEXT_GAME_PENDING.format(
            current=current,
            remaining=remaining,
            game_time=GAME_TIME_TEXT,
        )
        await call.message.answer(text, reply_markup=kb.join_game_kb())
    else:
        await call.message.answer("🎮 O'yin boshlandi! (bu yerga real o'yin logikasi ulanadi)")
    await call.answer()


@router.callback_query(F.data == "join_game")
async def cb_join_game(call: CallbackQuery):
    PARTICIPANTS.add(call.from_user.id)
    current = len(PARTICIPANTS)

    if current >= REQUIRED_PARTICIPANTS:
        await call.message.answer(texts.GAME_UNLOCKED_BROADCAST, reply_markup=kb.game_unlocked_kb())
    else:
        remaining = REQUIRED_PARTICIPANTS - current
        text = texts.NEXT_GAME_PENDING.format(
            current=current,
            remaining=remaining,
            game_time=GAME_TIME_TEXT,
        )
        await call.message.answer(text, reply_markup=kb.join_game_kb())
    await call.answer("Siz o'yinga qo'shildingiz ✅")


@router.callback_query(F.data == "today_rating")
async def cb_today_rating(call: CallbackQuery):
    # DEMO qiymatlar — real reyting DB'dan olinadi
    text = texts.TODAY_RATING.format(
        user1="user_one", score1=120,
        user2="user_two", score2=95,
        user3="user_three", score3=80,
        my_rank=7, my_score=40,
        next_game_time=GAME_TIME_TEXT,
    )
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "my_balance")
async def cb_my_balance(call: CallbackQuery):
    text = texts.MY_BALANCE.format(
        total_amount=0,
        games_played=0,
        pending_amount=0,
    )
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "my_profile")
async def cb_my_profile(call: CallbackQuery):
    user = call.from_user
    text = texts.MY_PROFILE.format(
        full_name=user.full_name,
        username=user.username or "yo'q",
        joined_date="—",
        total_wins=0,
        best_result="—",
    )
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "claim_prize")
async def cb_claim_prize(call: CallbackQuery):
    text = texts.CLAIM_PRIZE.format(
        admin_username=ADMIN_USERNAME,
        user_id=call.from_user.id,
        amount=0,
    )
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "rules")
async def cb_rules(call: CallbackQuery):
    await call.message.answer(texts.RULES)
    await call.answer()


# ------------------------------------------------------------------
# Admin panel
# ------------------------------------------------------------------
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🔧 ADMIN PANEL", reply_markup=kb.admin_panel_kb())


@router.callback_query(F.data == "admin_force_start")
async def cb_admin_force_start(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Sizda ruxsat yo'q ❌", show_alert=True)
        return
    await call.message.answer(texts.ADMIN_FORCE_START_CONFIRM)
    await call.answer()


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Sizda ruxsat yo'q ❌", show_alert=True)
        return
    await call.message.answer(f"👥 Hozirgi ishtirokchilar: {len(PARTICIPANTS)} / {REQUIRED_PARTICIPANTS}")
    await call.answer()


@router.callback_query(F.data == "admin_add_channel")
async def cb_admin_add_channel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("Sizda ruxsat yo'q ❌", show_alert=True)
        return
    await call.message.answer("📢 Kanal qo'shish funksiyasi hali ulanmagan (keyingi bosqich).")
    await call.answer()