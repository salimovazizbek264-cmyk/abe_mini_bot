# handlers_user.py
import time
import datetime
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
import texts
import games
import subscription
from config import ADMIN_ID, PRIZE_1, PRIZE_2, PRIZE_3

router = Router()


class WithdrawStates(StatesGroup):
    waiting_card = State()
    waiting_amount = State()


# in-memory: hozir davom etayotgan savol holati (game_token -> data)
ACTIVE_ROUNDS: dict[str, dict] = {}


def make_token(user_id: int) -> str:
    return f"{user_id}_{int(time.time()*1000)}"


# ------------------------------------------------------------------
# /start
# ------------------------------------------------------------------
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await db.get_or_create_user(user.id, user.username or "", user.first_name or "")
    await message.answer(texts.WELCOME, reply_markup=kb.main_menu_kb())


# ------------------------------------------------------------------
# O'YINNI BOSHLASH -> obuna tekshiruvi -> o'yin holatiga qarab javob
# ------------------------------------------------------------------
@router.callback_query(F.data == "start_game")
async def cb_start_game(call: CallbackQuery, bot: Bot):
    ok, missing = await subscription.check_subscription(bot, call.from_user.id)
    if not ok:
        await call.message.answer(texts.SUBSCRIBE_REQUIRED, reply_markup=kb.subscribe_kb(missing))
        await call.answer()
        return
    await show_game_state(call, bot)


@router.callback_query(F.data == "check_subscription")
async def cb_check_subscription(call: CallbackQuery, bot: Bot):
    ok, missing = await subscription.check_subscription(bot, call.from_user.id)
    if not ok:
        await call.answer("Hali barcha kanallarga obuna bo'lmagansiz ❌", show_alert=True)
        return
    await call.answer("Obuna tasdiqlandi ✅", show_alert=True)
    await show_game_state(call, bot)


async def show_game_state(call: CallbackQuery, bot: Bot):
    open_game = await db.get_open_game()
    if open_game:
        await send_round(call.message, call.from_user.id, open_game["id"])
        return

    pending_game = await db.get_pending_game()
    limit = await db.get_start_limit()
    times = await db.get_game_times()
    next_time = pending_game["start_time"] if pending_game else (times[0] if times else "—")
    current = await db.count_participants(pending_game["id"]) if pending_game else 0

    text = texts.NEXT_GAME_PENDING.format(
        current=current, limit=limit, remaining=max(limit - current, 0), game_time=next_time
    )
    await call.message.answer(text, reply_markup=kb.join_game_kb())


@router.callback_query(F.data == "join_game")
async def cb_join_game(call: CallbackQuery, bot: Bot):
    ok, missing = await subscription.check_subscription(bot, call.from_user.id)
    if not ok:
        await call.message.answer(texts.SUBSCRIBE_REQUIRED, reply_markup=kb.subscribe_kb(missing))
        await call.answer()
        return

    pending_game = await db.get_pending_game()
    if not pending_game:
        await call.answer("Hozircha faol o'yin yo'q, birozdan so'ng urinib ko'ring.", show_alert=True)
        return

    await db.add_participant(pending_game["id"], call.from_user.id)
    current = await db.count_participants(pending_game["id"])
    limit = await db.get_start_limit()

    if current >= limit:
        await db.set_game_status(pending_game["id"], "open")
        await bot.send_message(call.from_user.chat.id, texts.GAME_UNLOCKED_BROADCAST)
        await send_round(call.message, call.from_user.id, pending_game["id"])
    else:
        text = texts.NEXT_GAME_PENDING.format(
            current=current, limit=limit, remaining=limit - current, game_time=pending_game["start_time"]
        )
        await call.message.answer(text, reply_markup=kb.join_game_kb())
    await call.answer("Qo'shildingiz ✅")


# ------------------------------------------------------------------
# O'YIN ROUND
# ------------------------------------------------------------------
async def send_round(message: Message, user_id: int, game_id: int):
    already = await db.has_played(game_id, user_id)
    if already:
        await message.answer("✅ Siz bu o'yinda allaqachon qatnashdingiz. Natijalarni kuting!")
        return

    question, options, correct_index = games.get_random_round()
    token = make_token(user_id)
    ACTIVE_ROUNDS[token] = {
        "user_id": user_id,
        "game_id": game_id,
        "correct_index": correct_index,
        "started_at": time.time(),
    }
    await message.answer(question, reply_markup=kb.game_options_kb(options, token))


@router.callback_query(F.data.startswith("ans:"))
async def cb_answer(call: CallbackQuery, bot: Bot):
    _, token, idx_str = call.data.split(":")
    idx = int(idx_str)
    round_data = ACTIVE_ROUNDS.pop(token, None)

    if not round_data or round_data["user_id"] != call.from_user.id:
        await call.answer("Bu savol muddati tugagan.", show_alert=True)
        return

    elapsed = time.time() - round_data["started_at"]
    is_correct = idx == round_data["correct_index"]
    score = games.calculate_score(is_correct, elapsed)

    await db.add_score(round_data["game_id"], call.from_user.id, score)

    if is_correct:
        await call.message.answer(f"✅ To'g'ri! Siz {score} ball to'pladingiz.\n\nNatijalar o'yin yakunida e'lon qilinadi 🏆")
    else:
        await call.message.answer(f"❌ Noto'g'ri javob. Ball: {score}\n\nKeyingi o'yinda omad tilaymiz!")
    await call.answer()


# ------------------------------------------------------------------
# REYTING / BALANS / PROFIL / QOIDALAR
# ------------------------------------------------------------------
@router.callback_query(F.data == "today_rating")
async def cb_today_rating(call: CallbackQuery):
    game = await db.get_open_game() or await db.get_pending_game()
    if not game:
        await call.message.answer("Hozircha faol o'yin yo'q.")
        await call.answer()
        return

    top3 = await db.get_top3(game["id"])
    rank, score = await db.get_user_rank_and_score(game["id"], call.from_user.id)
    times = await db.get_game_times()

    def label(i):
        return top3[i]["username"] and f"@{top3[i]['username']}" or top3[i]["first_name"]

    text = texts.TODAY_RATING.format(
        user1=label(0) if len(top3) > 0 else "—", score1=top3[0]["score"] if len(top3) > 0 else 0,
        user2=label(1) if len(top3) > 1 else "—", score2=top3[1]["score"] if len(top3) > 1 else 0,
        user3=label(2) if len(top3) > 2 else "—", score3=top3[2]["score"] if len(top3) > 2 else 0,
        my_rank=rank or "—", my_score=score or 0,
        next_game_time=times[0] if times else "—",
    )
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "my_balance")
async def cb_my_balance(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    balance = user["balance"] if user else 0
    total = user["total_winnings"] if user else 0
    paid = total - balance
    text = texts.MY_BALANCE.format(total_amount=total, paid_amount=paid, unpaid_amount=balance)
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "my_profile")
async def cb_my_profile(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    joined = "—"
    if user and user.get("created_at"):
        joined = datetime.datetime.fromtimestamp(user["created_at"]).strftime("%d.%m.%Y")
    text = texts.MY_PROFILE.format(
        full_name=call.from_user.full_name,
        username=call.from_user.username or "yo'q",
        joined_date=joined,
        total_wins=user["total_winnings"] if user else 0,
    )
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data == "rules")
async def cb_rules(call: CallbackQuery):
    await call.message.answer(texts.RULES)
    await call.answer()


# ------------------------------------------------------------------
# PULNI CHIQARISH (karta raqam -> summa -> admin'ga xabar)
# ------------------------------------------------------------------
@router.callback_query(F.data == "withdraw_start")
async def cb_withdraw_start(call: CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    balance = user["balance"] if user else 0
    if balance <= 0:
        await call.answer("Sizda hozircha yechib olish uchun mablag' yo'q.", show_alert=True)
        return
    await call.message.answer(texts.WITHDRAW_ASK_CARD, reply_markup=kb.cancel_kb())
    await state.set_state(WithdrawStates.waiting_card)
    await call.answer()


@router.callback_query(F.data == "cancel_action")
async def cb_cancel_action(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Bekor qilindi.")
    await call.answer()


@router.message(WithdrawStates.waiting_card)
async def process_card_number(message: Message, state: FSMContext):
    card = message.text.strip()
    digits = "".join(c for c in card if c.isdigit())
    if len(digits) < 12:
        await message.answer("❗️ Karta raqami noto'g'ri ko'rinmoqda. Qaytadan kiriting (masalan: 8600 1234 5678 9012)")
        return
    await state.update_data(card_number=digits)
    user = await db.get_user(message.from_user.id)
    await message.answer(texts.WITHDRAW_ASK_AMOUNT.format(balance=user["balance"]))
    await state.set_state(WithdrawStates.waiting_amount)


@router.message(WithdrawStates.waiting_amount)
async def process_amount(message: Message, state: FSMContext, bot: Bot):
    text_val = message.text.strip().replace(" ", "")
    if not text_val.isdigit():
        await message.answer("❗️ Faqat summani raqamda kiriting (masalan: 3000)")
        return

    amount = int(text_val)
    user = await db.get_user(message.from_user.id)

    if amount <= 0 or amount > user["balance"]:
        await message.answer(f"❗️ Noto'g'ri summa. Balansingizda {user['balance']} so'm bor.")
        return

    data = await state.get_data()
    card_number = data.get("card_number")
    withdrawal_id = await db.create_withdrawal(message.from_user.id, amount, card_number)
    await state.clear()

    await message.answer(texts.WITHDRAW_REQUEST_SENT.format(amount=amount))

    masked = f"**** **** **** {card_number[-4:]}"
    username_part = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    admin_text = texts.ADMIN_NEW_WITHDRAWAL.format(
        username=username_part, user_id=message.from_user.id, card_masked=masked, amount=amount
    )
    await bot.send_message(ADMIN_ID, admin_text, reply_markup=kb.withdrawal_admin_kb(withdrawal_id))
