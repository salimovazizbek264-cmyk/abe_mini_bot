# games.py
import random
import time

# Har bir generator (savol_matni, [variantlar], to'g'ri_variant_index) qaytaradi

def game_tez_javob():
    pairs = [
        ("2 + 2 x 2 = ?", ["6", "8", "4", "10"], 0),
        ("O'zbekiston poytaxti?", ["Samarqand", "Toshkent", "Buxoro", "Andijon"], 1),
        ("Yilda nechta oy bor?", ["10", "11", "12", "13"], 2),
    ]
    q, opts, correct = random.choice(pairs)
    return f"🧠 TEZ JAVOB\n\n{q}", opts, correct


def game_sonni_top():
    target = random.randint(1, 20)
    options = {target}
    while len(options) < 4:
        options.add(random.randint(1, 20))
    options = list(options)
    random.shuffle(options)
    correct = options.index(target)
    return f"🔢 SONNI TOP\n\nYashirin son: {target} ✅ (pastdagi to'g'ri raqamni bosing)", [str(o) for o in options], correct


def game_farqni_top():
    base = random.choice(["🟢", "🔵", "🟡", "🟣"])
    diff = random.choice(["⚪️", "⚫️", "🟠", "🔴"])
    options = [base, base, base, base]
    correct = random.randint(0, 3)
    options[correct] = diff
    return "👀 FARQNI TOP\n\nBoshqacha belgini toping:", options, correct


def game_togri_tugma():
    correct = random.randint(0, 3)
    options = ["❌", "❌", "❌", "❌"]
    options[correct] = "✅"
    return "🟢 TO'G'RI TUGMA\n\nFaqat bitta to'g'ri tugma bor:", options, correct


def game_emojini_top():
    sets = [
        (["🍎", "🍎", "🍎", "🍏"], 3, "Boshqacha mevani toping"),
        (["🐱", "🐱", "🐶", "🐱"], 2, "Boshqacha hayvonni toping"),
        (["⚽️", "⚽️", "⚽️", "🏀"], 3, "Boshqacha to'pni toping"),
    ]
    options, correct, desc = random.choice(sets)
    return f"🧩 EMOJINI TOP\n\n{desc}:", options, correct


def game_harfni_top():
    target = random.choice("ABCDEFGH")
    options = [target]
    alphabet = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c != target]
    options += random.sample(alphabet, 3)
    random.shuffle(options)
    correct = options.index(target)
    return f"🔤 HARFNI TOP\n\nQuyidagi harflardan '{target}' harfini toping:", options, correct


def game_xotira():
    seq = "".join(random.choice("🔺🔻⭐️🔷") for _ in range(3))
    options = [seq]
    chars = "🔺🔻⭐️🔷"
    while len(options) < 4:
        fake = "".join(random.choice(chars) for _ in range(3))
        if fake not in options:
            options.append(fake)
    random.shuffle(options)
    correct = options.index(seq)
    return f"🧠 XOTIRA\n\nBu ketma-ketlikni eslab qoling:\n{seq}\n\n(pastdan xuddi shu ketma-ketlikni tanlang)", options, correct


def game_target():
    correct = random.randint(0, 3)
    options = ["⚪️", "⚪️", "⚪️", "⚪️"]
    options[correct] = "🎯"
    return "🎯 TARGET\n\nTo'g'ri targetni bosing:", options, correct


def game_challenge():
    a, b = random.randint(1, 9), random.randint(1, 9)
    correct_val = a + b
    options = {correct_val}
    while len(options) < 4:
        options.add(correct_val + random.randint(-3, 3))
    options = list(options)
    random.shuffle(options)
    correct = options.index(correct_val)
    return f"⚡ 10 SONIYALIK CHALLENGE\n\n{a} + {b} = ?", [str(o) for o in options], correct


def game_tez_bos():
    correct = random.randint(0, 3)
    options = ["⬜️", "⬜️", "⬜️", "⬜️"]
    options[correct] = "🟥"
    return "⚡ TEZ BOS\n\nQizil tugmani birinchi bo'lib bosing:", options, correct


GAME_GENERATORS = [
    game_tez_bos,
    game_tez_javob,
    game_sonni_top,
    game_farqni_top,
    game_togri_tugma,
    game_emojini_top,
    game_harfni_top,
    game_xotira,
    game_target,
    game_challenge,
]


def get_random_round():
    """Tasodifiy o'yin turini tanlaydi va savol/variant/tog'ri javobni qaytaradi"""
    generator = random.choice(GAME_GENERATORS)
    question, options, correct_index = generator()
    return question, options, correct_index


def calculate_score(is_correct: bool, elapsed_seconds: float) -> int:
    """Tez va to'g'ri javob ko'proq ball beradi"""
    if not is_correct:
        return 0
    base = 100
    penalty = min(int(elapsed_seconds * 8), 90)  # sekinlashgan sari ball kamayadi
    return max(base - penalty, 10)
