# games_db.py
import random

GAMES_POOL = [
    # Karrali jadvali
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **7 × 8 = ?**", "ans": ["56"]},
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **9 × 9 = ?**", "ans": ["81"]},
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **6 × 7 = ?**", "ans": ["42"]},
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **12 × 5 = ?**", "ans": ["60"]},
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **8 × 4 = ?**", "ans": ["32"]},
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **13 × 3 = ?**", "ans": ["39"]},
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **15 × 4 = ?**", "ans": ["60"]},
    {"q": "🧠 **Tezkor matematika!**\n\nHisoblang: **11 × 11 = ?**", "ans": ["121"]},

    # Emoji va mantiqiy topishmoqlar
    {"q": "🧩 **Emoji topishmoq!**\n\n🍎 + 🍎 + 🍎 = 15\n🍎 + 🍌 + 🍌 = 11\n🍌 + 🍇 + 🍇 = 9\n\nSavol: **🍇 = ?**", "ans": ["3"]},
    {"q": "🧩 **Mantiqiy savol!**\n\nQaysi oyda 28 kun bor? (To'liq so'z bilan yozing)", "ans": ["hamma oylarda", "barcha oylarda", "hamma oydayam"]},
    {"q": "🧩 **Emoji topishmoq!**\n\n🚗 + 🚗 = 10\n🚗 + 🚲 = 7\n\nSavol: **🚲 = ?**", "ans": ["2"]},
    {"q": "🧩 **Mantiqiy savol!**\n\n1 ta olmani teng ikkiga bo'lsak, nechta olma bo'ladi?", "ans": ["1", "bitta"]},
    {"q": "🧩 **Topishmoq:**\n\nQo'lda to'rtta, cho'ntakda nechta? (Toping)", "ans": ["barmoq", "barmoqlar"]},
    
    # Tezkor hisob-kitoblar
    {"q": "⚡ **Hisob-kitob:**\n\n(50 + 50) × 2 - 100 = ?", "ans": ["100"]},
    {"q": "⚡ **Hisob-kitob:**\n\n100 / 4 + 25 = ?", "ans": ["50"]},
    {"q": "⚡ **Hisob-kitob:**\n\n25 × 4 - 50 = ?", "ans": ["50"]},
    {"q": "⚡ **Topishmoq:**\n\nO'zbekistonning poytaxti qaysi shahar?", "ans": ["toshkent", "tashkent"]},
    {"q": "⚡ **Topishmoq:**\n\nDunyodagi eng katta okean qaysi?", "ans": ["tinch okeani", "tinch"]},
    {"q": "⚡ **Topishmoq:**\n\n1 soatda necha soniya bor?", "ans": ["3600", "3600 soniya"]},
    {"q": "⚡ **Mantiqiy savol:**\n\nUchta mushuk 3 ta sichqonni 3 minutda tutsa, 1 ta mushuk 1 ta sichqonni necha minutda tutadi?", "ans": ["3", "3 minut"]}
]

def get_random_game():
    return random.choice(GAMES_POOL)
