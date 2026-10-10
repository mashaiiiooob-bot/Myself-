import re
import asyncio
import time
from pyrogram import filters
from pyrogram.handlers import MessageHandler
ACTIVE_TASKS = {}
MAX_SECONDS = 7 * 86400

def _parse_time(s):
    """پارس زمان مثل 10s، 5m، 2h، 1d"""
    m = re.match('^(\\d+)\\s*([smhd])$', s.lower())
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)
    mult = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
    return n * mult

def _fmt_duration(sec):
    if sec < 60:
        return f'{sec} ثانیه'
    if sec < 3600:
        return f'{sec // 60} دقیقه'
    if sec < 86400:
        return f'{sec // 3600} ساعت'
    return f'{sec // 86400} روز'

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=2)
    if len(parts) < 3:
        return await message.reply_text('⏰ **Reminder**\n\n**فرمت:** `/remind 10s متن یادآوری`\n\n**واحدها:**\n• `s` — ثانیه\n• `m` — دقیقه\n• `h` — ساعت\n• `d` — روز\n\n**مثال:**\n`/remind 30m جلسه`\n`/remind 2h استراحت`\n\n**توقف:** `/stop`')
    time_str = parts[1]
    text = parts[2]
    uid = message.from_user.id
    chat_id = message.chat.id
    seconds = _parse_time(time_str)
    if not seconds or seconds <= 0:
        return await message.reply_text('❌ فرمت زمان اشتباه. نمونه: `10s`, `5m`, `2h`, `1d`')
    if seconds > MAX_SECONDS:
        return await message.reply_text(f'❌ حداکثر {_fmt_duration(MAX_SECONDS)}')

    async def remind_task():
        try:
            await asyncio.sleep(seconds)
            await client.send_message(chat_id, f'⏰ **یادآوری!**\n\n📝 {text}\n\n⏱ _بعد از {_fmt_duration(seconds)}_')
        except asyncio.CancelledError:
            return
        except Exception:
            return
    task = asyncio.create_task(remind_task())
    ACTIVE_TASKS.setdefault(uid, []).append(task)
    ACTIVE_TASKS[uid] = [t for t in ACTIVE_TASKS[uid] if not t.done()]
    await message.reply_text(f'⏰ **یادآوری تنظیم شد**\n\n📝 {text}\n⏱ {_fmt_duration(seconds)} دیگه\n📊 تسک\u200cهای فعال تو: `{len(ACTIVE_TASKS[uid])}`\n\n_برای توقف: `/stop`_')

async def stop_handler(client, message):
    uid = message.from_user.id
    tasks = ACTIVE_TASKS.get(uid, [])
    active = [t for t in tasks if not t.done()]
    if not active:
        return await message.reply_text('✅ تسک فعالی نداری')
    for t in active:
        t.cancel()
    ACTIVE_TASKS[uid] = []
    await message.reply_text(f'🛑 **{len(active)} تسک متوقف شد**')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('remind', prefixes=['/', '.'])), group=0)
    client.add_handler(MessageHandler(stop_handler, filters.me & filters.command('stop', prefixes=['/', '.'])), group=0)
