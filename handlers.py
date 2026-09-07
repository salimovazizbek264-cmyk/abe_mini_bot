# handlers.py
import asyncio
import time
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import texts
import keyboards as kb
from games_db import get_random_game

router = Router()

USERS_DB = {}          # user_id: {balance, total_won, wins_count, score, username, full_name, last_duet_time}
CHANNELS_DB = []       
GAME_CONFIG = {
    "time1": "10:00",
    "time2": "20:00",
    "is_active": False,
    "current_answer": None
}

# Jonli duet navbati va faol xonalar
DUET_QUEUE = []
ACTIVE_DUETS = {}      # room_id: {p1, p2, answer, question}

ADMIN_IDS = {8007670371}  

class WithdrawStates(StatesGroup):
    waiting_for_card = State()
    waiting_for_amount = State()

class AdminStates(StatesGroup):
    waiting_for_time1 = State()
    waiting_for_time2 = State()
    waiting_for_channel_title = State()
    waiting_for_channel_url = State()
    waiting_for_broadcast = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def get_user(user_id: int, user_full_name: str = "", username: str = ""):
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            "balance": 0,
            "total_won": 0,
            "wins_count": 0,
            "score": 0,
            "full_name": user_full_name,
            "username": username or "yo'q",
            "last_duet_time": 0
        }
    return USERS_DB[user_id]

def get_league(score: int):
    if score >= 50: return "👑 Brilliant Legenda"
    if score >= 30: return "💎 Platina"
    if score >= 15: return "🥇 Oltin"
    if score >= 5: return "🥈 Kumush"
    return "🥉 Bronza"

async def check_channels_subscription(bot: Bot, user_id: int) -> bool:
    for ch in CHANNELS_DB:
        ch_id = ch.get("id")
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            pass
    return True

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    uid = message.from_user.id
    args = message.text.split()
    
    if len(args) > 1:
        ref_id_str = args[1]
        if ref_id_str.isdigit():
            ref_id = int(ref_id_str)
            if ref_id != uid and ref_id in USERS_DB and uid not in [u.get("referred_by") for u in USERS_DB.values()]:
                USERS_DB[ref_id]["balance"] += 100
                USERS_DB[ref_id]["total_won"] += 100
                try:
                    await bot.send_message(ref_id, f"👥 **Yangi referal!** Siz taklif qilgan do'stingiz uchun `100 UZS` bonus oldingiz! 🎁", parse_mode="Markdown")
                except:
                    pass

    get_user(uid, message.from_user.full_name, message.from_user.username)
    
    if CHANNELS_DB and not await check_channels_subscription(bot, uid):
        await message.answer("⚠️ Botdan foydalanish uchun quyidagi homiy kanallarga obuna bo'lishingiz shart:", reply_markup=kb.check_sub_kb(CHANNELS_DB))
        return

    await message.answer(texts.WELCOME.format(time1=GAME_CONFIG["time1"], time2=GAME_CONFIG["time2"]), reply_markup=kb.main_menu_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "check_subscription")
async def cb_check_sub(call: CallbackQuery, bot: Bot):
    uid = call.from_user.id
    if await check_channels_subscription(bot, uid):
        await call.message.edit_text(texts.WELCOME.format(time1=GAME_CONFIG["time1"], time2=GAME_CONFIG["time2"]), reply_markup=kb.main_menu_kb(), parse_mode="Markdown")
    else:
        await call.answer("❌ Hali hamma kanallarga obuna bo'lmadingiz!", show_alert=True)

@router.callback_query(F.data == "back_to_menu")
async def cb_back_to_menu(call: CallbackQuery):
    await call.message.edit_text(texts.WELCOME.format(time1=GAME_CONFIG["time1"], time2=GAME_CONFIG["time2"]), reply_markup=kb.main_menu_kb(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == "start_game")
async def cb_start_game(call: CallbackQuery):
    await call.message.edit_text(
        f"⏳ **Asosiy o'yin kutish rejimida!**\n\n⏰ Vaqtlar: `{GAME_CONFIG['time1']}` va `{GAME_CONFIG['time2']}`\n\n💡 Shuningdek, asosiy menyudan **'⚔️ JONLI DUET'** tugmasini bosib istalgan vaqtda raqib bilan bellashishingiz mumkin!",
        reply_markup=kb.back_to_menu_kb(),
        parse_mode="Markdown"
    )
    await call.answer()

# --- JONLI DUET (1 vs 1) TIZIMI ---
@router.callback_query(F.data == "live_duet")
async def cb_live_duet(call: CallbackQuery, bot: Bot):
    uid = call.from_user.id
    u = get_user(uid)
    
    current_time = time.time()
    if current_time - u["last_duet_time"] < 86400:
        remaining_hours = int((86400 - (current_time - u["last_duet_time"])) / 3600)
        await call.answer(f"⏳ Siz oxirgi duetda mag'lub bo'lgansiz! Yana o'ynash uchun {remaining_hours} soat qoldi.", show_alert=True)
        return

    sorted_users = sorted(USERS_DB.items(), key=lambda x: x[1]["score"], reverse=True)
    top10_ids = [u_id for u_id, _ in sorted_users[:10]]
    
    if len(sorted_users) >= 3 and uid not in top10_ids:
        await call.answer("⚠️ Jonli duetda faqat REYTINGDAGI TOP-10 talik ichidagi o'yinchilar qatnasha oladi! Avval umumiy o'yinlarda ball to'plab topga kiring.", show_alert=True)
        return

    if uid in DUET_QUEUE:
        await call.answer("⏳ Siz allaqachon navbatdasiz, raqib qidirilmoqda...", show_alert=True)
        return

    DUET_QUEUE.append(uid)
    await call.message.edit_text("🔍 **JONLI DUET QIDIRUVDA...**\n\nSizga munosib raqib izlanmoqda, iltimos kuting ⏳", reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()

    if len(DUET_QUEUE) >= 2:
        p1 = DUET_QUEUE.pop(0)
        p2 = DUET_QUEUE.pop(0)
        
        game = get_random_game()
        room_id = f"{p1}_{p2}_{int(time.time())}"
        ACTIVE_DUETS[room_id] = {
            "p1": p1,
            "p2": p2,
            "answer": game["ans"],
            "question": game["q"]
        }

        duet_text = f"⚔️ **JONLI DUET BOSHLANDI!** 🔥\n\n{game['q']}\n\n👇 Birinchi bo'lib to'g'ri javobni yuboring!"
        
        for pid in [p1, p2]:
            try:
                await bot.send_message(pid, duet_text, parse_mode="Markdown")
            except:
                pass

@router.callback_query(F.data == "today_rating")
async def cb_today_rating(call: CallbackQuery):
    sorted_users = sorted(USERS_DB.items(), key=lambda x: x[1]["score"], reverse=True)
    top10 = sorted_users[:10]
    
    text = "🏆 **REYTING TOP-10 (JONLI)** 📊\n\n"
    for idx, (u_id, u_data) in enumerate(top10):
        medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"🔹 {idx+1}."
        text += f"{medal} @{u_data['username']} — `{u_data['score']}` ball (`{u_data['wins_count']}` g'alaba)\n"

    uid = call.from_user.id
    my_data = USERS_DB.get(uid, {"score": 0})
    my_rank = "Topdan tashqari"
    for idx, (u_id, _) in enumerate(sorted_users):
        if u_id == uid:
            my_rank = idx + 1
            break

    text += f"\n━━━━━━━━━━━━━━━━━━━\n📍 **Sizning o'rningiz:** `{my_rank}-o'rin` (`{my_data['score']}` ball)"
    await call.message.edit_text(text, reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == "my_balance")
async def cb_my_balance(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.full_name, call.from_user.username)
    text = f"💎 **SHAXSIY HISOB YOKI BALANS** 💳\n\n💰 **Asosiy balans:** `{u['balance']} UZS`\n📈 **Jami ishlangan yutuqlar:** `{u['total_won']} UZS`"
    await call.message.edit_text(text, reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == "referral_menu")
async def cb_referral_menu(call: CallbackQuery, bot: Bot):
    uid = call.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={uid}"
    
    text = (
        f"👥 **DO'STLARNI TAKLIF QILISH (REFERAL)** 🔗\n\n"
        f"Har bir taklif qilgan do'stingiz uchun balansingizga qo'shimcha **100 UZS** qo'shiladi! 💸\n\n"
        f"🔗 **Sizning shaxsiy havolangiz:**\n`{ref_link}`\n\n"
        f"Do'stlaringizga ulashing va pul ishlang!"
    )
    await call.message.edit_text(text, reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == "my_profile")
async def cb_my_profile(call: CallbackQuery):
    u = get_user(call.from_user.id, call.from_user.full_name, call.from_user.username)
    league = get_league(u["score"])
    text = (
        f"👤 **FOYdALANUVCHI PROFILI** 🛡️\n\n"
        f"📌 **F.I.O:** {u['full_name']}\n"
        f"🔗 **Username:** @{u['username']}\n"
        f"🏆 **Daraja (Liga):** **{league}**\n"
        f"⭐ **Reyting ballari:** `{u['score']} ball`\n"
        f"🎯 **G'alabalar soni:** `{u['wins_count']}` ta\n"
        f"💎 **Balans:** `{u['balance']} UZS`"
    )
    await call.message.edit_text(text, reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == "rules")
async def cb_rules(call: CallbackQuery):
    await call.message.edit_text(texts.RULES, reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await call.answer()

# --- PUL CHIQARISH ---
@router.callback_query(F.data == "claim_prize")
async def cb_claim_prize(call: CallbackQuery, state: FSMContext):
    u = get_user(call.from_user.id)
    if u["balance"] <= 0:
        await call.answer("❌ Balansingizda mablag' yetarli emas!", show_alert=True)
        return
    
    await call.message.edit_text("💳 **KARTA RAQAMINI KIRITISH**\n\nKarta raqamingizni yuboring (Masalan: `8600 1234 5678 9012`):", reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await state.set_state(WithdrawStates.waiting_for_card)
    await call.answer()

@router.message(WithdrawStates.waiting_for_card)
async def process_card(message: Message, state: FSMContext):
    card = message.text.strip()
    if len(card) < 12:
        await message.answer("❌ Karta raqami xato. Qaytadan kiriting:")
        return
    await state.update_data(card=card)
    u = get_user(message.from_user.id)
    await message.answer(f"💰 **SUMMANI KIRITING**\n\nBalansingizda mavjud: `{u['balance']} UZS`", parse_mode="Markdown")
    await state.set_state(WithdrawStates.waiting_for_amount)

@router.message(WithdrawStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext, bot: Bot):
    try:
        amount = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Faqat raqam yozing:")
        return

    uid = message.from_user.id
    u = get_user(uid)
    if amount <= 0 or amount > u["balance"]:
        await message.answer("❌ Xato summa!")
        return

    data = await state.get_data()
    card = data.get("card")
    await state.clear()
    u["balance"] -= amount

    await message.answer("✅ **So'rov yuborildi!** Admin tez orada ko'rib chiqadi. 💸", reply_markup=kb.main_menu_kb())

    admin_text = (
        f"🚨 **YANGI PUL CHIQARISH SO'ROVI!** 💳\n\n"
        f"👤 **Ism:** {message.from_user.full_name}\n"
        f"🔗 **Username:** @{message.from_user.username}\n"
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
            await bot.send_message(uid, "🎉 Pul chiqarish so'rovingiz tasdiqlandi va kartangizga o'tkazib berildi! 💳💸")
        except:
            pass
    else:
        await call.message.edit_text(f"{call.message.text}\n\n❌ **HOLAT: RAD ETILDI** 🔴", parse_mode="Markdown")
        try:
            await bot.send_message(uid, "❌ Afsuski, pul chiqarish so'rovingiz rad etildi.")
        except:
            pass
    await call.answer("Bajarildi!")

# --- XABARLAR VA JONLI DUET / O'YINLARNI TEKSHIRISH ---
@router.message(F.text)
async def check_game_answer(message: Message, bot: Bot):
    uid = message.from_user.id
    text = message.text.strip()

    if CHANNELS_DB and not await check_channels_subscription(bot, uid):
        return

    user_ans = text.lower()

    # 1. Jonli duet javobini tekshirish
    matched_room = None
    for room_id, duet in list(ACTIVE_DUETS.items()):
        if uid in [duet["p1"], duet["p2"]]:
            matched_room = (room_id, duet)
            break

    if matched_room:
        room_id, duet = matched_room
        correct_answers = duet["answer"]
        is_correct = any(ans in user_ans for ans in correct_answers)

        winner_id = uid
        loser_id = duet["p2"] if uid == duet["p1"] else duet["p1"]

        if is_correct:
            # To'g'ri javob berdi
            w_user = get_user(winner_id)
            w_user["balance"] += 2000
            w_user["total_won"] += 2000
            w_user["wins_count"] += 1
            w_user["score"] += 1

            l_user = get_user(loser_id)
            l_user["last_duet_time"] = time.time()

            next_duet_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚔️ Keyingi raqibni topish", callback_data="live_duet")],
                [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")]
            ])

            try:
                await bot.send_message(
                    winner_id, 
                    "✅ **Javobingiz to'g'ri!** 🎉\n\n🎉 **Siz jonli duetda g'alaba qozondingiz!** 🏆\nBalansingizga `2 000 UZS` qo'shildi va reytingga `+1 ball` yozildi!", 
                    reply_markup=next_duet_kb, 
                    parse_mode="Markdown"
                )
                await bot.send_message(
                    loser_id, 
                    "❌ **Javobingiz hato!** Siz hato javob berdingiz, raqib to'g'ri topdi.\n\n⏳ Siz oxirgi duetda mag'lub bo'ldingiz! Keyingi o'yin 24 soat ichida qayta raqib qidirishingiz mumkin. Oldindan omad!", 
                    parse_mode="Markdown"
                )
            except:
                pass

            del ACTIVE_DUETS[room_id]
            return
        else:
            # Noto'g'ri javob berdi -> Raqibga g'alaba o'tadi
            w_user = get_user(loser_id)
            w_user["balance"] += 2000
            w_user["total_won"] += 2000
            w_user["wins_count"] += 1
            w_user["score"] += 1

            l_user = get_user(winner_id) # Joriy yuboruvchi yutqazdi
            l_user["last_duet_time"] = time.time()

            next_duet_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⚔️ Keyingi raqibni topish", callback_data="live_duet")],
                [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")]
            ])

            try:
                await bot.send_message(
                    winner_id, 
                    "❌ **Javobingiz hato!** Siz hato javob berdingiz.\n\n⏳ Siz oxirgi duetda mag'lub bo'ldingiz! Keyingi o'yin 24 soat ichida qayta raqib qidirishingiz mumkin. Oldindan omad!", 
                    parse_mode="Markdown"
                )
                await bot.send_message(
                    loser_id, 
                    "✅ Raqib xato javob berdi!\n\n🎉 **Siz jonli duetda g'alaba qozondingiz!** 🏆\nBalansingizga `2 000 UZS` qo'shildi va reytingga `+1 ball` yozildi!", 
                    reply_markup=next_duet_kb, 
                    parse_mode="Markdown"
                )
            except:
                pass

            del ACTIVE_DUETS[room_id]
            return

    # 2. Asosiy avtomatik o'yin javobini tekshirish
    if GAME_CONFIG["is_active"] and GAME_CONFIG["current_answer"]:
        correct_answers = GAME_CONFIG["current_answer"]
        if any(ans in user_ans for ans in correct_answers):
            GAME_CONFIG["is_active"] = False  
            u = get_user(uid, message.from_user.full_name, message.from_user.username)
            u["balance"] += 3000
            u["total_won"] += 3000
            u["wins_count"] += 1
            u["score"] += 1  

            win_text = (
                f"✅ **Javobingiz to'g'ri!**\n\n"
                f"🎉 **TABRIKLAYMIZ! G'OLIB ANIQLANDI!** 🏆\n\n"
                f"🥇 **G'olib:** @{u['username']} ({message.from_user.full_name})\n"
                f"🎁 **Mukofot:** `3 000 UZS` va reytingga `+1 ball` qo'shildi!\n\n"
                f"Keyingi o'yinni kuting 🚀"
            )
            await message.answer(win_text, parse_mode="Markdown")

            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, f"🏆 **O'yin g'olibi aniqlandi!**\n\n👤 {message.from_user.full_name} (@{u['username']})\n🆔 `{uid}`", parse_mode="Markdown")
                except:
                    pass
        else:
            # Agar asosiy o'yinda noto'g'ri javob yuborilsa
            await message.answer("❌ **Javobingiz hato!** Qaytadan urinib ko'ring.", parse_mode="Markdown")

# --- ADMIN PANEL ---
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🔧 **PROFESSIONAL ADMIN PANEL** 🛡️", reply_markup=kb.admin_panel_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_set_times")
async def cb_admin_set_times(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text("⏰ **1-o'yin vaqtini yuboring** (Masalan: `10:00`):", reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_time1)
    await call.answer()

@router.message(AdminStates.waiting_for_time1)
async def save_time1(message: Message, state: FSMContext):
    GAME_CONFIG["time1"] = message.text.strip()
    await message.answer("⏰ **2-o'yin vaqtini yuboring** (Masalan: `20:00`):", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_time2)

@router.message(AdminStates.waiting_for_time2)
async def save_time2(message: Message, state: FSMContext):
    GAME_CONFIG["time2"] = message.text.strip()
    await state.clear()
    await message.answer(f"✅ O'yin vaqtlari yangilandi:\n1️⃣ `{GAME_CONFIG['time1']}`\n2️⃣ `{GAME_CONFIG['time2']}`", reply_markup=kb.main_menu_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_add_channel")
async def cb_admin_add_channel(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text("📢 Majburiy kanal nomini yuboring:", reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_channel_title)
    await call.answer()

@router.message(AdminStates.waiting_for_channel_title)
async def save_ch_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("🔗 Kanal username'ini yoki ID'sini yuboring (Masalan: `@abevayn` yoki `-100123456789`):", parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_channel_url)

@router.message(AdminStates.waiting_for_channel_url)
async def save_ch_url(message: Message, state: FSMContext):
    data = await state.get_data()
    text_input = message.text.strip()
    
    # Havola yoki username'dan kanal ID/username'ini to'g'ri ajratib olish
    ch_id = text_input
    if "t.me/" in text_input:
        parts = text_input.split("t.me/")
        ch_username = "@" + parts[1].split("/")[0].strip()
        ch_id = ch_username
    elif not text_input.startswith("@") and not text_input.startswith("-100"):
        ch_id = "@" + text_input

    url = f"https://t.me/{ch_id.replace('@', '')}"
    CHANNELS_DB.append({"title": data["title"], "url": url, "id": ch_id})
    await state.clear()
    await message.answer(f"✅ Kanal muvaffaqiyatli qo'shildi: `{ch_id}`", reply_markup=kb.admin_panel_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_broadcast")
async def cb_admin_broadcast(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text("📢 Hammaga yuboriladigan xabarni kiriting:", reply_markup=kb.back_to_menu_kb(), parse_mode="Markdown")
    await state.set_state(AdminStates.waiting_for_broadcast)
    await call.answer()

@router.message(AdminStates.waiting_for_broadcast)
async def execute_broadcast(message: Message, state: FSMContext, bot: Bot):
    text = message.text
    await state.clear()
    count = 0
    
    # Agar USERS_DB bo'sh bo'lsa, xatolik chiqmasligi uchun yuboruvchining o'zini ham bazaga qo'shamiz
    get_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    
    for uid in list(USERS_DB.keys()):
        try:
            await bot.send_message(uid, text)
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass
    await message.answer(f"✅ Xabar `{count}` ta foydalanuvchiga yetkazildi!", reply_markup=kb.admin_panel_kb(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_force_start")
async def cb_admin_force_start(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    
    # Adminning o'zini ham bazaga kiritib qo'shamiz (bazalar bo'sh qolib ketmasligi uchun)
    get_user(call.from_user.id, call.from_user.full_name, call.from_user.username)
    
    await trigger_game(bot)
    await call.message.edit_text("🚀 O'yin majburiy boshlandi va barchaga savol yuborildi!", reply_markup=kb.admin_panel_kb(), parse_mode="Markdown")
    await call.answer()

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    await call.message.edit_text(
        f"📊 **STATISTIKA**\n\n👥 Foydalanuvchilar: `{len(USERS_DB)}` ta\n⏰ O'yin vaqtlari: `{GAME_CONFIG['time1']}` | `{GAME_CONFIG['time2']}`",
        reply_markup=kb.admin_panel_kb(),
        parse_mode="Markdown"
    )
    await call.answer()

async def trigger_game(bot: Bot):
    game = get_random_game()
    GAME_CONFIG["is_active"] = True
    GAME_CONFIG["current_answer"] = game["ans"]

    game_msg = f"🎮 **YANGI MINI-O'YIN BOSHLANDI!** ⚡\n\n{game['q']}\n\n👇 Botga birinchi bo'lib to'g'ri javobni yuboring!"

    for uid in list(USERS_DB.keys()):
        try:
            await bot.send_message(uid, game_msg, parse_mode="Markdown")
            await asyncio.sleep(0.04)
        except:
            pass

async def background_scheduler(bot: Bot):
    while True:
        now = datetime.now().strftime("%H:%M")
        if (now == GAME_CONFIG["time1"] or now == GAME_CONFIG["time2"]) and not GAME_CONFIG["is_active"]:
            await trigger_game(bot)
            await asyncio.sleep(60)
        await asyncio.sleep(30)
