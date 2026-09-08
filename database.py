# database.py
import aiosqlite
import time
from config import DB_PATH, DEFAULT_START_LIMIT, DEFAULT_GAME_TIMES, CHANNEL_USERNAME

_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    balance INTEGER DEFAULT 0,
    total_winnings INTEGER DEFAULT 0,
    created_at INTEGER,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_type TEXT,
    date TEXT,
    start_time TEXT,
    status TEXT DEFAULT 'pending'   -- pending | open | finished
);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    user_id INTEGER,
    score INTEGER,
    rank INTEGER
);

CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    card_number TEXT,
    status TEXT DEFAULT 'pending',  -- pending | paid | rejected
    created_at INTEGER,
    paid_at INTEGER
);

CREATE TABLE IF NOT EXISTS sponsors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT,
    url TEXT,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,     -- @kanal_username
    title TEXT,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    user_id INTEGER,
    joined_at INTEGER
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_CREATE_TABLES)
        # default settings
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('start_limit', ?)",
            (str(DEFAULT_START_LIMIT),),
        )
        await db.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES ('game_times', ?)",
            (",".join(DEFAULT_GAME_TIMES),),
        )
        await db.commit()
        # .env'da CHANNEL_USERNAME berilgan bo'lsa, uni birinchi majburiy kanal sifatida qo'shamiz
        if CHANNEL_USERNAME:
            cur = await db.execute("SELECT COUNT(*) FROM channels")
            row = await cur.fetchone()
            if row[0] == 0:
                await db.execute(
                    "INSERT OR IGNORE INTO channels (username, title, active) VALUES (?, ?, 1)",
                    (CHANNEL_USERNAME, "Asosiy kanal"),
                )
                await db.commit()


# ---------------------------------------------------------------
# USERS
# ---------------------------------------------------------------
async def get_or_create_user(telegram_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = await cur.fetchone()
        if user:
            await db.execute(
                "UPDATE users SET username = ?, first_name = ? WHERE telegram_id = ?",
                (username, first_name, telegram_id),
            )
            await db.commit()
            return dict(user)
        await db.execute(
            "INSERT INTO users (telegram_id, username, first_name, created_at) VALUES (?, ?, ?, ?)",
            (telegram_id, username, first_name, int(time.time())),
        )
        await db.commit()
        cur = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = await cur.fetchone()
        return dict(user)


async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_all_active_user_ids():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT telegram_id FROM users WHERE is_active = 1")
        rows = await cur.fetchall()
        return [r[0] for r in rows]


async def count_users():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        row = await cur.fetchone()
        return row[0]


async def add_balance(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ?, total_winnings = total_winnings + ? WHERE telegram_id = ?",
            (amount, amount, telegram_id),
        )
        await db.commit()


async def deduct_balance(telegram_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE telegram_id = ?",
            (amount, telegram_id),
        )
        await db.commit()


# ---------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------
async def get_setting(key: str, default: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cur.fetchone()
        return row[0] if row else default


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await db.commit()


async def get_start_limit() -> int:
    val = await get_setting("start_limit", "1000")
    return int(val)


async def get_game_times() -> list:
    val = await get_setting("game_times", "10:00,20:00")
    return [t.strip() for t in val.split(",") if t.strip()]


# ---------------------------------------------------------------
# GAMES / PARTICIPANTS
# ---------------------------------------------------------------
async def create_game(game_type: str, date: str, start_time: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO games (game_type, date, start_time, status) VALUES (?, ?, ?, 'pending')",
            (game_type, date, start_time),
        )
        await db.commit()
        return cur.lastrowid


async def get_pending_game():
    """Hozircha ochilmagan, kutayotgan (pending) o'yin"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM games WHERE status = 'pending' ORDER BY id DESC LIMIT 1")
        row = await cur.fetchone()
        return dict(row) if row else None


async def get_open_game():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM games WHERE status = 'open' ORDER BY id DESC LIMIT 1")
        row = await cur.fetchone()
        return dict(row) if row else None


async def set_game_status(game_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE games SET status = ? WHERE id = ?", (status, game_id))
        await db.commit()


async def add_participant(game_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id FROM participants WHERE game_id = ? AND user_id = ?", (game_id, user_id)
        )
        exists = await cur.fetchone()
        if exists:
            return
        await db.execute(
            "INSERT INTO participants (game_id, user_id, joined_at) VALUES (?, ?, ?)",
            (game_id, user_id, int(time.time())),
        )
        await db.commit()


async def count_participants(game_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM participants WHERE game_id = ?", (game_id,))
        row = await cur.fetchone()
        return row[0]


async def has_joined(game_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id FROM participants WHERE game_id = ? AND user_id = ?", (game_id, user_id)
        )
        row = await cur.fetchone()
        return row is not None


# ---------------------------------------------------------------
# SCORES
# ---------------------------------------------------------------
async def has_played(game_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id FROM scores WHERE game_id = ? AND user_id = ?", (game_id, user_id)
        )
        row = await cur.fetchone()
        return row is not None


async def add_score(game_id: int, user_id: int, score: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO scores (game_id, user_id, score) VALUES (?, ?, ?)",
            (game_id, user_id, score),
        )
        await db.commit()


async def get_top3(game_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT s.user_id, s.score, u.username, u.first_name "
            "FROM scores s JOIN users u ON u.telegram_id = s.user_id "
            "WHERE s.game_id = ? ORDER BY s.score DESC LIMIT 3",
            (game_id,),
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def get_user_rank_and_score(game_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id, score FROM scores WHERE game_id = ? ORDER BY score DESC", (game_id,)
        )
        rows = await cur.fetchall()
        for idx, row in enumerate(rows, start=1):
            if row[0] == user_id:
                return idx, row[1]
        return None, None


# ---------------------------------------------------------------
# WITHDRAWALS
# ---------------------------------------------------------------
async def create_withdrawal(user_id: int, amount: int, card_number: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO withdrawals (user_id, amount, card_number, status, created_at) "
            "VALUES (?, ?, ?, 'pending', ?)",
            (user_id, amount, card_number, int(time.time())),
        )
        await db.commit()
        return cur.lastrowid


async def get_withdrawal(withdrawal_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM withdrawals WHERE id = ?", (withdrawal_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def set_withdrawal_status(withdrawal_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        paid_at = int(time.time()) if status == "paid" else None
        await db.execute(
            "UPDATE withdrawals SET status = ?, paid_at = ? WHERE id = ?",
            (status, paid_at, withdrawal_id),
        )
        await db.commit()


async def get_pending_withdrawals():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM withdrawals WHERE status = 'pending' ORDER BY id DESC")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------
# MAJBURIY OBUNA KANALLARI
# ---------------------------------------------------------------
async def add_channel(username: str, title: str = ""):
    username = username.strip()
    if not username.startswith("@"):
        username = "@" + username
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO channels (username, title, active) VALUES (?, ?, 1) "
            "ON CONFLICT(username) DO UPDATE SET active = 1, title = excluded.title",
            (username, title),
        )
        await db.commit()


async def remove_channel(channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE channels SET active = 0 WHERE id = ?", (channel_id,))
        await db.commit()


async def get_active_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM channels WHERE active = 1 ORDER BY id")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------
# SPONSORS
# ---------------------------------------------------------------
async def add_sponsor(name: str, username: str, url: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO sponsors (name, username, url, active) VALUES (?, ?, ?, 1)",
            (name, username, url),
        )
        await db.commit()


async def get_active_sponsors():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM sponsors WHERE active = 1")
        rows = await cur.fetchall()
        return [dict(r) for r in rows]
