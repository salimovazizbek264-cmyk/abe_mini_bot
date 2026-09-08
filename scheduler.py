# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

import database as db
import texts
import keyboards as kb
from config import TIMEZONE, GAME_WINDOW_MINUTES

scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def open_scheduled_game(bot):
    """Belgilangan vaqtda ishtirokchi yig'ish oynasini ochadi"""
    pending = await db.get_pending_game()
    if not pending:
        times = await db.get_game_times()
        now_str = datetime.datetime.now().strftime("%H:%M")
        start_time = now_str if not times else times[0]
        game_id = await db.create_game("mixed", str(datetime.date.today()), start_time)
    else:
        game_id = pending["id"]

    current = await db.count_participants(game_id)
    limit = await db.get_start_limit()

    user_ids = await db.get_all_active_user_ids()
    for uid in user_ids:
        try:
            text = texts.NEXT_GAME_PENDING.format(
                current=current, limit=limit, remaining=max(limit - current, 0), game_time="hozir"
            )
            await bot.send_message(uid, text, reply_markup=kb.join_game_kb())
        except Exception:
            continue


async def close_game_window(bot):
    """O'yin oynasini yopadi, TOP-3'ni e'lon qiladi, adminga xabar beradi"""
    open_game = await db.get_open_game()
    if not open_game:
        return

    top3 = await db.get_top3(open_game["id"])
    await db.set_game_status(open_game["id"], "finished")

    if not top3:
        return

    from config import PRIZE_1, PRIZE_2, PRIZE_3, ADMIN_ID
    prizes = [PRIZE_1, PRIZE_2, PRIZE_3]

    lines_for_broadcast = []
    medals = ["🥇", "🥈", "🥉"]
    for i, row in enumerate(top3):
        uname = f"@{row['username']}" if row["username"] else row["first_name"]
        await db.add_balance(row["user_id"], prizes[i])
        lines_for_broadcast.append((uname, row["score"]))

    text = texts.GAME_RESULT_BROADCAST.format(
        user1=lines_for_broadcast[0][0] if len(lines_for_broadcast) > 0 else "—",
        score1=lines_for_broadcast[0][1] if len(lines_for_broadcast) > 0 else 0,
        user2=lines_for_broadcast[1][0] if len(lines_for_broadcast) > 1 else "—",
        score2=lines_for_broadcast[1][1] if len(lines_for_broadcast) > 1 else 0,
        user3=lines_for_broadcast[2][0] if len(lines_for_broadcast) > 2 else "—",
        score3=lines_for_broadcast[2][1] if len(lines_for_broadcast) > 2 else 0,
    )

    user_ids = await db.get_all_active_user_ids()
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
        except Exception:
            continue

    try:
        await bot.send_message(ADMIN_ID, "🏁 O'yin yakunlandi, g'oliblarga ballar qo'shildi.\n\n" + text)
    except Exception:
        pass


async def setup_scheduler(bot):
    times = await db.get_game_times()
    for t in times:
        hour, minute = t.split(":")
        scheduler.add_job(
            open_scheduled_game,
            CronTrigger(hour=int(hour), minute=int(minute), timezone=TIMEZONE),
            args=[bot],
            id=f"open_{t}",
            replace_existing=True,
        )
        close_hour = int(hour)
        close_minute = int(minute) + GAME_WINDOW_MINUTES
        if close_minute >= 60:
            close_minute -= 60
            close_hour = (close_hour + 1) % 24
        scheduler.add_job(
            close_game_window,
            CronTrigger(hour=close_hour, minute=close_minute, timezone=TIMEZONE),
            args=[bot],
            id=f"close_{t}",
            replace_existing=True,
        )
    scheduler.start()
