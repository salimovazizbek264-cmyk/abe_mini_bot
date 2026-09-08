# texts.py — ABE VAYN MINI GAME barcha matnlari

WELCOME = """🎮 ABE VAYN MINI GAME ga xush kelibsiz!

⏳ Bu yerda ketgan vaqtingizga achinmaysiz.
Biz sizni zeriktirmaymiz! 🔥

Har kuni 2 MARTA yangi mini-o'yin bo'ladi!

Har bir o'yinda TOP-3 ishtirokchi sovrin oladi:

🥇 1-O'RIN — 3 000 so'm 💰
🥈 2-O'RIN — 2 000 so'm 💰
🥉 3-O'RIN — 1 000 so'm 💰

O'yinga kirish bepul.
Pul tikish yoki depozit qilish talab qilinmaydi.

🏆 Balki bugungi g'olib aynan SIZ bo'larsiz?"""


SUBSCRIBE_REQUIRED = """📢 O'yinda qatnashish uchun quyidagi kanal(lar)ga obuna bo'ling.

Obuna bo'lgach "✅ OBUNANI TEKSHIRISH" tugmasini bosing."""


NEXT_GAME_PENDING = """🔥 KEYINGI O'YIN

👥 Ishtirokchilar: {current} / {limit}
⏳ Yana {remaining} ta ishtirokchi kerak.

🕙 Bugungi o'yin: {game_time}"""


GAME_UNLOCKED_BROADCAST = """🚀 YETARLI ISHTIROKCHI YIG'ILDI!

🔥 O'YIN BOSHLANMOQDA!

Tayyor turing. Bugun TOP-3 kim bo'ladi? 👀"""


TODAY_RATING = """🏆 BUGUNGI REYTING

🥇 {user1} — {score1} ball
🥈 {user2} — {score2} ball
🥉 {user3} — {score3} ball

📍 Sizning o'rningiz: {my_rank}-o'rin ({my_score} ball)

⏳ Keyingi o'yin: {next_game_time}"""


MY_BALANCE = """💰 MENING BALANSIM

Jami yutuq: {total_amount} so'm
To'langan: {paid_amount} so'm
To'lanmagan (yechib olish mumkin): {unpaid_amount} so'm"""


MY_PROFILE = """👤 PROFIL

Ism: {full_name}
Username: @{username}
Ro'yxatdan o'tgan sana: {joined_date}
Jami g'alabalar: {total_wins} so'm"""


RULES = """ℹ️ QOIDALAR

1️⃣ O'yin bepul, hech qanday to'lov talab qilinmaydi
2️⃣ Har kuni 2 marta o'yin bo'ladi
3️⃣ TOP-3 ishtirokchi sovrin oladi
4️⃣ G'oliblar botda e'lon qilinadi
5️⃣ Sovrinlarni admin qo'lda, karta orqali to'laydi

Omad tilaymiz! 🍀"""


GAME_RESULT_BROADCAST = """🏁 O'YIN YAKUNLANDI!

🥇 1. {user1} — {score1} ball
🥈 2. {user2} — {score2} ball
🥉 3. {user3} — {score3} ball

💰 Sovrinlar:
1-o'rin: 3 000 so'm
2-o'rin: 2 000 so'm
3-o'rin: 1 000 so'm

Tabriklaymiz, g'oliblar! 🎉"""


ADMIN_FORCE_START_CONFIRM = """✅ O'yin qo'lda ishga tushirildi.
Barcha ishtirokchilarga xabar yuborildi."""


# --- Pulni chiqarish ---
WITHDRAW_ASK_CARD = """💳 Pulni olish uchun karta raqamingizni yuboring.

Masalan: 8600 1234 5678 9012"""

WITHDRAW_ASK_AMOUNT = """✅ Karta qabul qilindi.

💰 Balansingiz: {balance} so'm

Qancha summani yechib olmoqchisiz? Miqdorni raqamda yozing (masalan: 3000)"""

WITHDRAW_REQUEST_SENT = """✅ So'rovingiz qabul qilindi!

Summa: {amount} so'm

Admin tez orada ko'rib chiqib, to'lovni amalga oshiradi. Tasdiqlangach sizga xabar keladi."""

ADMIN_NEW_WITHDRAWAL = """💰 YANGI TO'LOV SO'ROVI

👤 Foydalanuvchi: {username}
🆔 ID: {user_id}
💳 Karta: {card_masked}
💰 Summa: {amount} so'm"""

WITHDRAW_PAID_USER_MSG = """✅ TO'LOV TASDIQLANDI

{username}, sizning {amount} so'mlik yutug'ingiz hisobingizga muvaffaqiyatli o'tkazildi.

Keyingi o'yinlarda omad! 🎮🏆"""

WITHDRAW_REJECTED_USER_MSG = """❌ TO'LOV SO'ROVI RAD ETILDI

{username}, so'rovingiz admin tomonidan rad etildi. Aniqlik uchun admin bilan bog'laning."""
