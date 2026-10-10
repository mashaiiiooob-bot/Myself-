import re
import time
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.handlers import MessageHandler
_COUNT_CD = {}
_COUNT_SEC = 3

async def count_handler(client, message):
    uid = message.from_user.id
    now = time.time()
    if uid in _COUNT_CD and now - _COUNT_CD[uid] < _COUNT_SEC:
        return await message.reply_text(f'⏳ صبر: {_COUNT_SEC - (now - _COUNT_CD[uid]):.1f}s')
    _COUNT_CD[uid] = now
    parts = (message.text or '').split(maxsplit=1)
    text = parts[1] if len(parts) > 1 else ''
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not text:
        return await message.reply_text('**فرمت:** `/count متن`')
    chars = len(text)
    chars_ns = len(text.replace(' ', '').replace('\n', ''))
    words = len(text.split())
    lines = len(text.splitlines())
    sents = len(re.split('[.!?؟]+', text.strip()))
    await message.reply_text(f'🔢 **آمار متن**\n\n📝 کاراکتر: `{chars:,}`\n📝 بدون فاصله: `{chars_ns:,}`\n📚 کلمه: `{words:,}`\n📄 خط: `{lines:,}`\n💬 جمله: `{sents:,}`')

async def age_handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply_text('**فرمت:** `/age 2005/8/21` یا `/age 1384/5/30`')
    ds = parts[1].strip()
    m = re.match('^(\\d{4})[/\\-.](\\d{1,2})[/\\-.](\\d{1,2})$', ds)
    if not m:
        return await message.reply_text('❌ فرمت اشتباه')
    y, mo, d = map(int, m.groups())
    if y < 1500:
        try:
            import jdatetime
            g = jdatetime.date(y, mo, d).togregorian()
            birth = datetime(g.year, g.month, g.day)
        except ImportError:
            return await message.reply_text('❌ `pip install jdatetime`')
        except Exception:
            return await message.reply_text('❌ تاریخ شمسی اشتباه')
    else:
        try:
            birth = datetime(y, mo, d)
        except Exception:
            return await message.reply_text('❌ تاریخ اشتباه')
    now = datetime.now()
    delta = now - birth
    td = delta.days
    ts = int(delta.total_seconds())
    years = now.year - birth.year
    months = now.month - birth.month
    days = now.day - birth.day
    if days < 0:
        months -= 1
        pm = now.replace(day=1) - timedelta(days=1)
        days += pm.day
    if months < 0:
        years -= 1
        months += 12
    breaths = ts // 60 * 15
    beats = ts // 60 * 70
    await message.reply_text(f'🎂 **سن**\n\n📅 تولد: `{ds}`\n🎈 سن: `{years} سال و {months} ماه و {days} روز`\n\n📊 **آمار:**\n• روز: `{td:,}`\n• ساعت: `{ts // 3600:,}`\n• دقیقه: `{ts // 60:,}`\n• نفس: `~{breaths:,}`\n• ضربان: `~{beats:,}`')

def register(client):
    client.add_handler(MessageHandler(count_handler, filters.me & filters.command('count', prefixes=['/', '.'])), group=0)
    client.add_handler(MessageHandler(age_handler, filters.me & filters.command('age', prefixes=['/', '.'])), group=0)
