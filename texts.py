# texts.py
# ABE VAYN MINI GAME — barcha bot matnlari shu yerda saqlanadi

WELCOME = """🎮 ABE VAYN MINI GAME ga xush kelibsiz!

⏳ Bu yerda ketgan vaqtingizga achinmaysiz.
Biz sizni zeriktirmaymiz! 🔥

Har kuni 2 MARTA yangi mini-o'yin bo'ladi:

🕙 10:00
🕗 20:00

Har bir o'yinda TOP-3 ishtirokchi sovrin oladi:

🥇 1-O'RIN — 3 000 so'm 💰
🥈 2-O'RIN — 2 000 so'm 💰
🥉 3-O'RIN — 1 000 so'm 💰

🎯 Jami bugungi sovrin: 6 000 so'm

O'yinga kirish bepul.
Pul tikish yoki depozit qilish talab qilinmaydi.

🏆 Balki bugungi g'olib aynan SIZ bo'larsiz?

Quyidagi tugmani bosing va bugungi challenge'ni boshlang 👇"""


NEXT_GAME_PENDING = """🔥 KEYINGI O'YIN

👥 Ishtirokchilar: {current} / 1000

⏳ Yana {remaining} ta ishtirokchi kerak.

🕙 Bugungi o'yin: {game_time}"""


GAME_UNLOCKED_BROADCAST = """🚀 1000 TA ISHTIROKCHI YIG'ILDI!

🔥 O'YIN BOSHLANMOQDA!

Tayyor turing. Bugun TOP-3 kim bo'ladi? 👀"""


TODAY_RATING = """🏆 BUGUNGI REYTING

🥇 @{user1} — {score1} ball
🥈 @{user2} — {score2} ball
🥉 @{user3} — {score3} ball

📍 Sizning o'rningiz: {my_rank}-o'rin ({my_score} ball)

⏳ Keyingi o'yin: {next_game_time}"""


MY_BALANCE = """💰 MENING BALANSIM

Jami yutuq: {total_amount} so'm
Bugungi o'yinlar: {games_played}
Kutilayotgan to'lovlar: {pending_amount} so'm

📤 Sovrinni olish uchun "SOVRINNI OLISH" tugmasini bosing"""


MY_PROFILE = """👤 PROFIL

Ism: {full_name}
Username: @{username}
Ro'yxatdan o'tgan sana: {joined_date}
Jami g'alabalar: {total_wins}
Eng yaxshi natija: {best_result}"""


CLAIM_PRIZE = """📤 SOVRINNI OLISH

Tabriklaymiz! 🎉
Sovringizni olish uchun admin bilan bog'laning: @{admin_username}

Sizning ID: {user_id}
Yutgan summa: {amount} so'm"""


RULES = """ℹ️ QOIDALAR

1️⃣ O'yin bepul, hech qanday to'lov talab qilinmaydi
2️⃣ Har kuni 2 marta: 10:00 va 20:00
3️⃣ TOP-3 ishtirokchi sovrin oladi
4️⃣ G'oliblar kanalda e'lon qilinadi
5️⃣ Sovrinlar admin tomonidan qo'lda to'lanadi

Omad tilaymiz! 🍀"""


GAME_RESULT_BROADCAST = """🏁 BUGUNGI O'YIN TUGADI!

🥇 1-O'RIN: @{user1} — 3 000 so'm 💰
🥈 2-O'RIN: @{user2} — 2 000 so'm 💰
🥉 3-O'RIN: @{user3} — 1 000 so'm 💰

🎉 Tabriklaymiz, g'oliblar!
Sovrinni admin tez orada yuboradi.

🕗 Keyingi o'yin: {next_game_time}"""


ADMIN_FORCE_START_CONFIRM = """✅ O'yin qo'lda ishga tushirildi.

Majburiy 1000 ishtirokchi tekshiruvi bypass qilindi.
Barcha foydalanuvchilarga xabar yuborildi."""