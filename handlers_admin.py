# handlers_admin.py
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
import texts
from config import ADMIN_ID

router = Router()


def admin_only(user_id: int) -> bool:
    return user_id == ADMIN_ID


class AdminStates(StatesGroup):
    waiting_times = State()
    waiting_limit = State()
    waiting_broadcast = State()
    waiting_sponsor_name = State()
    waiting_sponsor_username = State()
    waiting_sponsor_url = State()


_sponsor_temp = {}


# ------------------------------------------------------------------
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not admin_only(message.from_user.id):
        return
    await message.answer("⚙️ ADMIN PANEL", reply_markup=kb.admin_panel_kb())


@router.callback_query(F.data == "admin_back")
async def cb_admin_back(call: CallbackQuery):
    if not admin_only(call.from_user.id):
        return
    await call.message.answer("⚙️ ADMIN PANEL", reply_markup=kb.admin_panel_kb())
    await call.answer()


# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_users")
async def cb_admin_users(call: CallbackQuery):
    if not admin_only(call.from_user.id):
        return
    count = await db.count_users()
    await call.message.answer(f"👥 Jami foydalanuvchilar: {count} ta", reply_markup=kb.back_to_admin_kb())
    await call.answer()


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    if not admin_only(call.from_user.id):
        return
    total_users = await db.count_users()
    pending_game = await db.get_pending_game()
    open_game = await db.get_open_game()
    limit = await db.get_start_limit()
    current = 0
    status = "kutilmoqda"
    if open_game:
        current = await db.count_participants(open_game["id"])
        status = "OCHIQ (o'yin ketmoqda)"
    elif pending_game:
        current = await db.count_participants(pending_game["id"])
        status = "kutilmoqda"

    text = (
        f"📊 STATISTIKA\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"🎮 Hozirgi o'yin holati: {status}\n"
        f"👥 Ishtirokchilar: {current} / {limit}"
    )
    await call.message.answer(text, reply_markup=kb.back_to_admin_kb())
    await call.answer()


# ------------------------------------------------------------------
# O'YIN VAQTLARI
# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_set_times")
async def cb_set_times(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return
    current_times = await db.get_game_times()
    await call.message.answer(
        f"⏰ Hozirgi o'yin vaqtlari: {', '.join(current_times)}\n\n"
        f"Yangi vaqtlarni HH:MM formatida, vergul bilan ajratib yozing.\n"
        f"Masalan: 10:00,20:00",
        reply_markup=kb.cancel_kb(),
    )
    await state.set_state(AdminStates.waiting_times)
    await call.answer()


@router.message(AdminStates.waiting_times)
async def process_times(message: Message, state: FSMContext):
    if not admin_only(message.from_user.id):
        return
    raw = message.text.strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    valid = all(len(p) == 5 and p[2] == ":" for p in parts)
    if not valid or not parts:
        await message.answer("❗️ Format noto'g'ri. Masalan: 10:00,20:00")
        return
    await db.set_setting("game_times", ",".join(parts))
    await state.clear()
    await message.answer(f"✅ O'yin vaqtlari yangilandi: {', '.join(parts)}", reply_markup=kb.back_to_admin_kb())


# ------------------------------------------------------------------
# START LIMIT
# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_set_limit")
async def cb_set_limit(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return
    current = await db.get_start_limit()
    await call.message.answer(
        f"🔢 Hozirgi start limit: {current}\n\nYangi limitni raqamda kiriting:",
        reply_markup=kb.cancel_kb(),
    )
    await state.set_state(AdminStates.waiting_limit)
    await call.answer()


@router.message(AdminStates.waiting_limit)
async def process_limit(message: Message, state: FSMContext):
    if not admin_only(message.from_user.id):
        return
    val = message.text.strip()
    if not val.isdigit() or int(val) <= 0:
        await message.answer("❗️ Faqat musbat raqam kiriting.")
        return
    await db.set_setting("start_limit", val)
    await state.clear()
    await message.answer(f"✅ Start limit {val} qilib o'rnatildi.", reply_markup=kb.back_to_admin_kb())


# ------------------------------------------------------------------
# HOZIR START BERISH
# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_force_start")
async def cb_force_start(call: CallbackQuery, bot: Bot):
    if not admin_only(call.from_user.id):
        return

    pending_game = await db.get_pending_game()
    if not pending_game:
        times = await db.get_game_times()
        game_id = await db.create_game("mixed", "-", times[0] if times else "-")
        pending_game = await db.get_pending_game() or {"id": game_id}

    await db.set_game_status(pending_game["id"], "open")

    user_ids = await db.get_all_active_user_ids()
    sent = 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, texts.GAME_UNLOCKED_BROADCAST, reply_markup=kb.join_game_kb())
            sent += 1
        except Exception:
            continue

    await call.message.answer(
        f"{texts.ADMIN_FORCE_START_CONFIRM}\n\n📤 {sent} ta foydalanuvchiga yuborildi.",
        reply_markup=kb.back_to_admin_kb(),
    )
    await call.answer()


# ------------------------------------------------------------------
# BROADCAST
# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast_start(call: CallbackQuery, state: FSMContext):
    if not admin_only(call.from_user.id):
        return
    await call.message.answer("📢 Barchaga yuboriladigan xabar matnini kiriting:", reply_markup=kb.cancel_kb())
    await state.set_state(AdminStates.waiting_broadcast)
    await call.answer()


@router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not admin_only(message.from_user.id):
        return
    text_to_send = message.text
    user_ids = await db.get_all_active_user_ids()
    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, text_to_send)
            sent += 1
        except Exception:
            failed += 1
    await state.clear()
    await message.answer(f"✅ Yuborildi: {sent} ta\n❌ Yuborilmadi: {failed} ta", reply_markup=kb.back_to_admin_kb())


# ------------------------------------------------------------------
# BUGUNGI G'OLIBLAR
# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_winners")
async def cb_admin_winners(call: CallbackQuery):
    if not admin_only(call.from_user.id):
        return
    game = await db.get_open_game() or await db.get_pending_game()
    if not game:
        await call.message.answer("Hozircha o'yin mavjud emas.", reply_markup=kb.back_to_admin_kb())
        await call.answer()
        return
    top3 = await db.get_top3(game["id"])
    if not top3:
        await call.message.answer("Hali natijalar yo'q.", reply_markup=kb.back_to_admin_kb())
        await call.answer()
        return
    lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, row in enumerate(top3):
        uname = f"@{row['username']}" if row["username"] else row["first_name"]
        lines.append(f"{medals[i]} {uname} — {row['score']} ball")
    await call.message.answer("🏆 BUGUNGI G'OLIBLAR\n\n" + "\n".join(lines), reply_markup=kb.back_to_admin_kb())
    await call.answer()


# ------------------------------------------------------------------
# TO'LOVLAR (withdrawals)
# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_withdrawals")
async def cb_admin_withdrawals(call: CallbackQuery):
    if not admin_only(call.from_user.id):
        return
    pending = await db.get_pending_withdrawals()
    if not pending:
        await call.message.answer("💸 Hozircha kutilayotgan to'lov so'rovlari yo'q.", reply_markup=kb.back_to_admin_kb())
        await call.answer()
        return
    for w in pending:
        user = await db.get_user(w["user_id"])
        uname = f"@{user['username']}" if user and user["username"] else (user["first_name"] if user else "—")
        masked = f"**** **** **** {w['card_number'][-4:]}"
        text = texts.ADMIN_NEW_WITHDRAWAL.format(
            username=uname, user_id=w["user_id"], card_masked=masked, amount=w["amount"]
        )
        await call.message.answer(text, reply_markup=kb.withdrawal_admin_kb(w["id"]))
    await call.answer()


@router.callback_query(F.data.startswith("wd_paid:"))
async def cb_withdraw_paid(call: CallbackQuery, bot: Bot):
    if not admin_only(call.from_user.id):
        return
    withdrawal_id = int(call.data.split(":")[1])
    w = await db.get_withdrawal(withdrawal_id)
    if not w or w["status"] != "pending":
        await call.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    await db.set_withdrawal_status(withdrawal_id, "paid")
    await db.deduct_balance(w["user_id"], w["amount"])

    user = await db.get_user(w["user_id"])
    uname = f"@{user['username']}" if user and user["username"] else (user["first_name"] if user else "")
    try:
        await bot.send_message(
            w["user_id"], texts.WITHDRAW_PAID_USER_MSG.format(username=uname, amount=w["amount"])
        )
    except Exception:
        pass

    await call.message.edit_text(call.message.text + "\n\n✅ TO'LANDI")
    await call.answer("To'lov tasdiqlandi ✅")


@router.callback_query(F.data.startswith("wd_reject:"))
async def cb_withdraw_reject(call: CallbackQuery, bot: Bot):
    if not admin_only(call.from_user.id):
        return
    withdrawal_id = int(call.data.split(":")[1])
    w = await db.get_withdrawal(withdrawal_id)
    if not w or w["status"] != "pending":
        await call.answer("Bu so'rov allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    await db.set_withdrawal_status(withdrawal_id, "rejected")
    user = await db.get_user(w["user_id"])
    uname = f"@{user['username']}" if user and user["username"] else (user["first_name"] if user else "")
    try:
        await bot.send_message(w["user_id"], texts.WITHDRAW_REJECTED_USER_MSG.format(username=uname))
    except Exception:
        pass

    await call.message.edit_text(call.message.text + "\n\n❌ RAD ETILDI")
    await call.answer("Rad etildi")


# ------------------------------------------------------------------
# HOMIYLAR (majburiy obuna kanallari sifatida ham ishlaydi)
# ------------------------------------------------------------------
@router.callback_query(F.data == "admin_sponsors")
async def cb_admin_sponsors(call: CallbackQuery):
    if not admin_only(call.from_user.id):
        return
    sponsors = await db.get_active_sponsors()
    b_text = "📣 HOMIYLAR (majburiy obuna kanallari)\n\n"
    if sponsors:
        for s in sponsors:
            b_text += f"• {s['name']} — {s['username']}\n"
    else:
        b_text += "Hozircha homiy yo'q."
    b_text += "\n\nYangi homiy/kanal qo'shish uchun /add_sponsor buyrug'ini yuboring."
    await call.message.answer(b_text, reply_markup=kb.back_to_admin_kb())
    await call.answer()


@router.message(Command("add_sponsor"))
async def cmd_add_sponsor(message: Message, state: FSMContext):
    if not admin_only(message.from_user.id):
        return
    await message.answer("📣 Homiy nomini kiriting:", reply_markup=kb.cancel_kb())
    await state.set_state(AdminStates.waiting_sponsor_name)


@router.message(AdminStates.waiting_sponsor_name)
async def process_sponsor_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Kanal username'ini kiriting (masalan @kanal_nomi):")
    await state.set_state(AdminStates.waiting_sponsor_username)


@router.message(AdminStates.waiting_sponsor_username)
async def process_sponsor_username(message: Message, state: FSMContext):
    uname = message.text.strip()
    if not uname.startswith("@"):
        uname = "@" + uname
    await state.update_data(username=uname)
    await message.answer("Kanal havolasini kiriting (masalan https://t.me/kanal_nomi):")
    await state.set_state(AdminStates.waiting_sponsor_url)


@router.message(AdminStates.waiting_sponsor_url)
async def process_sponsor_url(message: Message, state: FSMContext):
    data = await state.get_data()
    url = message.text.strip()
    await db.add_sponsor(data["name"], data["username"], url)
    await state.clear()
    await message.answer(
        f"✅ Homiy qo'shildi: {data['name']} ({data['username']})\n\n"
        f"⚠️ Muhim: botni shu kanalga ADMIN qilib qo'shishni unutmang, "
        f"aks holda obuna tekshiruvi ishlamaydi!",
        reply_markup=kb.back_to_admin_kb(),
    )
