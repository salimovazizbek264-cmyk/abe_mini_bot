# handlers.py
# ABE VAYN MINI GAME — handlerlar va tugma boshqaruvlari

import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import texts
import keyboards as kb

router = Router()

USERS_DB = {}          # user_id: {balance, total_won, wins_count, username, full_name}
GAME_STATE = {
    "is_active": False,
    "game_time": "20:00",
    "scores": {}       # user_id: click_count
}

ADMIN_IDS = {8007670371}  # Sizning Admin ID'ingiz

class WithdrawStates(StatesGroup):
    waiting_for_card = State()
    waiting_for_amount = State()

class AdminStates(StatesGroup):
    waiting_for_time = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def get_user(user_id: int, user_full_name: str = "", username: str = ""):
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            "balance": 0,
            "total_won": 0,
            "wins_count": 0,
            "full_name": user_full_name,
            "username": username or "yo'q"
        }
    return USERS_DB[user_id]


@router.message(CommandStart())
async def cmd_start(message: Message):
    get_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer(texts.WELCOME.format(game_time=GAME_STATE["game_time"]), reply_markup=kb.main_menu_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "back_to_menu")
async def cb_back_to_menu(call: CallbackQuery):
    await call.message.edit_text(texts.WELCOME.format(game_time=GAME_STATE["game_time"]), reply_markup=kb.main_menu_kb(), parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "start_game")
async def cb_start_game(call: CallbackQuery):
    if not GAME_STATE["is_active"]:
        await call.message.edit_text(
            f"⏳ **Hozircha o'yin faol emas!**\n\n⏰ Navbatdagi rejalashtirilgan o'yin vaqti: `{GAME_STATE['game_time']}`\n\n💡 Admin tomonidan start berilganda xabar keladi!",
            reply_markup=kb.back_to_menu_kb(),
            parse_mode="Markdown"
        )
    else:
        await call.message.edit_text(texts.GAME_STARTED, reply_markup=kb.game_action_kb(), parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "click_action")
async def cb_click_action(call: CallbackQuery):
    if not GAME_STATE["is_active"]:
        await call.answer("❌ O'yin allaqachon yakunlangan yoki boshlanmagan!", show_alert=True)
        return
    
    uid = call.from_user.id
    GAME_STATE["scores"][uid] = GAME_STATE["scores"].get(uid, 0) + 1
    await call.answer(f"⚡ Ball qo'shildi! Jami: {GAME_STATE['scores'][uid]}")


@router.callback_query(F.data == "today_rating")
async def cb_today_rating(call: CallbackQuery):
    scores = GAME_STATE["scores"]
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    top3 = [("Mavjud emas", 0), ("Mavjud emas", 0), ("Mavjud emas", 0)]
    for i in range(min(3, len(sorted_scores))):
        u_id, score = sorted_scores[i]
        u_data = USERS_DB.get(u_id, {})
        top3[i] = (u_data.get("username", "user"), score)

    uid = call.from_user.id
    my_score = scores.get(uid, 0)
    my_rank = "Topdan tashqari"
    if (uid, my_score) in sorted_scores:
        my_rank = sorted_scores.index((uid, my_score)) + 1

    text = texts.TODAY_RATING.format(
        user1=top3[0][0], score1=top3[0][1],
        user2=top3[1][0], score2=top3[1][1],
        user3=top3[2][0], score3=top3[2][1],
        my_score=my_score,
        my_rank=my_rank,
        next_game_time=GAME_STATE["game_time"]
    )
    await call.message.edit_text(text, reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "my_balance")
async def cb_my_balance(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.full_name, call.from_user.username)
    await call.message.edit_text(texts.MY_BALANCE.format(balance=u["balance"], total_won=u["total_won"]), reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "my_profile")
async def cb_my_profile(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.full_name, call.from_user.username)
    await call.message.edit_text(texts.MY_PROFILE.format(
        full_name=u["full_name"],
        username=u["username"],
        user_id=call.from_user.id,
        wins_count=u["wins_count"]
    ), reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "rules")
async def cb_rules(call: CallbackQuery):
    await call.message.edit_text(texts.RULES, reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()


# --- PUL CHIQARISH TIZIMI ---
@router.callback_query(F.data == "claim_prize")
async def cb_claim_prize(call: CallbackQuery, state: FSMContext):
    u = get_user(call.from_user.id)
    if u["balance"] <= 0:
        await call.answer("❌ Balansingizda mablag' yetarli emas!", show_alert=True)
        return
    
    await call.message.edit_text(
        "💳 **KARTA RAQAMINI KIRITISH**\n\nIltimos, mablag' tushishi uchun karta raqamingizni yuboring (Masalan: `8600 1234 5678 9012` yoki Uzcard/Humo):",
        reply_markup=kb.back_to_menu_kb(),
        parse_mode="Markdown"
    )
    await state.set_state(WithdrawStates.waiting_for_card)
    await call.answer()


@router.message(WithdrawStates.waiting_for_card)
async def process_card(message: Message, state: FSMContext):
    card = message.text.strip()
    if len(card) < 12:
        await message.answer("❌ Karta raqami xato ko'rinadi. Iltimos, to'g'ri formatda qaytadan kiriting:")
        return
    
    await state.update_data(card=card)
    u = get_user(message.from_user.id)
    await message.answer(f"💰 **SUMmani KIRITING**\n\nBalansingizda mavjud: `{u['balance']} UZS`\nQancha summa yechib olmoqchisiz?", parse_mode="Markdown")
    await state.set_state(WithdrawStates.waiting_for_amount)


@router.message(WithdrawStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext, bot: Bot):
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Faqat raqamlardan foydalaning. Summani qaytadan yozing:")
        return

    uid = message.from_user.id
    u = get_user(uid)

    if amount <= 0 or amount > u["balance"]:
        await message.answer("❌ Xato summa! Balansingizda yetarli pul yo'q yoki 0 dan ko'p kiriting.")
        return

    data = await state.get_data()
    card = data.get("card")
    await state.clear()

    u["balance"] -= amount

    await message.answer("✅ **So'rov muvaffaqiyatli yuborildi!**\nAdmin tez orada kartangizga pulni o'tkazib beradi. 💸", reply_markup=kb.main_menu_kb(), parse_mode="Markdown")

    admin_text = (
        f"🚨 **YANGI PUL CHIQARISH SO'ROVI!** 💳\n\n"
        f"👤 **Foydalanuvchi:** {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🆔 **ID:** `{uid}`\n"
        f"💳 **Karta:** `{card}`\n"
        f"💵 **Summa:** `{amount} UZS`"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=kb.admin_withdraw_decision_kb(uid), parse_mode="Markdown")
        except:
            pass


@router.callback_query(F.data.startswith("wd_"))
async def admin_wd_decision(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    
    action, uid_str = call.data.split("_")[1], call.data.split("_")[2]
    uid = int(uid_str)

    if action == "yes":
        await call.message.edit_text(f"{call.message.text}\n\n✅ **HOLAT: TO'LAB BERILDI** 🟢", parse_mode="Markdown")
        try:
            await bot.send_message(uid, "🎉 **Ajoyib yangilik!** Pul chiqarish so'rovingiz admin tomonidan tasdiqlandi va kartangizga o'tkazib berildi! 💳💸")
        except:
            pass
    else:
        await call.message.edit_text(f"{call.message.text}\n\n❌ **HOLAT: RAD ETILDI** 🔴", parse_mode="Markdown")
        try:
            await bot.send_message(uid, "❌ Afsuski, pul chiqarish so'rovingiz admin tomonidan rad etildi.")
        except:
            pass
    await call.answer("Am bajarildi!")


# --- PROFESSIONAL ADMIN PANEL ---
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🔧 **PROFESSIONAL ADMIN PANEL** 🛡️", reply_markup=kb.admin_panel_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "admin_set_time")
async def cb_admin_set_time(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text("⏰ Yangi o'yin vaqtini yuboring (Masalan: `14:30` yoki `21:00`):", reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_time)
    await call.answer()


@router.message(AdminStates.waiting_for_time)
async def save_game_time(message: Message, state: FSMContext):
    new_time = message.text.strip()
    GAME_STATE["game_time"] = new_time
    await state.clear()
    await message.answer(f"✅ O'yin vaqti muvaffaqiyatli **{new_time}** etib belgilandi! ⏰", reply_markup=kb.main_menu_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "admin_force_start")
async def cb_admin_force_start(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    
    GAME_STATE["is_active"] = True
    GAME_STATE["scores"] = {}

    await call.message.edit_text("🚀 O'yin admin tomonidan qo'lda boshlandi! Barcha foydalanuvchilarga xabar yuborildi.", reply_markup=kb.admin_panel_kb(), parse_mode="Markdown")
    await call.answer()

    for uid in USERS_DB.keys():
        try:
            await bot.send_message(uid, texts.GAME_STARTED, reply_markup=kb.game_action_kb(), parse_mode="Markdown")
        except:
            pass

    async def finish_game_timer():
        await asyncio.sleep(30)
        GAME_STATE["is_active"] = False
        scores = GAME_STATE["scores"]
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        prizes = [3000, 2000, 1000]
        winners_info = ["Mavjud emas", "Mavjud emas", "Mavjud emas"]
        scores_info = [0, 0, 0]

        for i in range(min(3, len(sorted_scores))):
            u_id, score = sorted_scores[i]
            if u_id in USERS_DB:
                USERS_DB[u_id]["balance"] += prizes[i]
                USERS_DB[u_id]["total_won"] += prizes[i]
                USERS_DB[u_id]["wins_count"] += 1
                winners_info[i] = USERS_DB[u_id]["username"]
                scores_info[i] = score

        finish_text = texts.GAME_FINISHED.format(
            u1=winners_info[0], s1=scores_info[0],
            u2=winners_info[1], s2=scores_info[1],
            u3=winners_info[2], s3=scores_info[2]
        )

        for uid in USERS_DB.keys():
            try:
                await bot.send_message(uid, finish_text, reply_markup=kb.main_menu_kb(), parse_mode="Markdown")
            except:
                pass

    asyncio.create_task(finish_game_timer())


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    total_users = len(USERS_DB)
    await call.message.edit_text(
        f"📊 **BOT STATISTIKASI** 📈\n\n"
        f"👥 **Jami foydalanuvchilar:** `{total_users}` ta\n"
        f"⏰ **Joriy o'yin vaqti:** `{GAME_STATE['game_time']}`\n"
        f"🎮 **O'yin holati:** `{'Faol 🟢' if GAME_STATE['is_active'] else 'Kutish rejimida ⏸'}`",
        reply_markup=kb.admin_panel_kb(),
        parse_mode="Markdown"
    )
    await call.answer()
