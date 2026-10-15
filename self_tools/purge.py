"""
حذف x پیام اخیر یک گروه.

حذف 20 پیام اخیر        (یا: حذف ۲۰ پیام اخیر / حذف 20 پیام)
/purge 20  ·  .purge 20

- فقط در گروه/سوپرگروهی کار می‌کند که اکانت شما مالک یا ادمینِ دارای دسترسی
  «حذف پیام» است؛ در چت خصوصی، کانال یا گروهِ بدون دسترسی هیچ پیامی پاک نمی‌شود.
- «x پیام اخیر» یعنی x پیامِ قبل از خودِ دستور؛ خودِ دستور هم پاک می‌شود.
- سقف ایمن برای هر بار اجرا: MAX_PURGE پیام (جلوگیری از اشتباهِ تایپی مثل ۵۰۰۰۰).
- گزارش «N پیام حذف شد» چند ثانیه بعد خودش پاک می‌شود.
"""
import asyncio

from pyrogram import filters
from pyrogram.handlers import MessageHandler

try:
    from pyrogram.errors import FloodWait
except ImportError:
    class FloodWait(Exception):
        value = 30

from .selfloop import _can_delete, _PERM_CACHE, _enum_name

MAX_PURGE = 500        # سقف تعداد پیام در هر بار اجرا
BATCH = 100            # تلگرام در هر درخواست حداکثر ۱۰۰ پیام را پاک می‌کند
REPORT_TTL = 4         # ثانیه تا پاک‌شدنِ پیام گزارش

_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_RUNNING = set()       # (uid, chat_id) — جلوگیری از اجرای هم‌زمان در یک چت


def _parse_count(text):
    """'حذف ۲۰ پیام اخیر' / '/purge 20' -> 20 ؛ نامعتبر -> None."""
    import re
    t = (text or "").strip().translate(_DIGITS)
    m = re.fullmatch(r"حذف\s+(\d+)\s+پیام(?:\s+اخیر)?", t) or \
        re.fullmatch(r"[/.]purge\s+(\d+)", t, re.I)
    return int(m.group(1)) if m else None


async def _reply_temp(message, text):
    try:
        r = await message.reply_text(text)
    except Exception:
        return

    async def _later():
        await asyncio.sleep(REPORT_TTL)
        try:
            await r.delete()
        except Exception:
            pass
    asyncio.create_task(_later())


async def _delete_ids(client, chat_id, ids):
    """ids را دسته‌ای پاک می‌کند؛ تعداد واقعاً حذف‌شده را برمی‌گرداند."""
    deleted = 0
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i + BATCH]
        for attempt in (1, 2):
            try:
                res = await client.delete_messages(chat_id, chunk)
                deleted += res if isinstance(res, int) else len(chunk)
                break
            except FloodWait as fw:
                if attempt == 2:
                    break
                await asyncio.sleep(int(getattr(fw, "value", 30) or 30) + 1)
            except Exception:
                break
    return deleted


async def handler(client, message):
    n = _parse_count(message.text)
    if n is None:
        return
    uid = client.me.id
    chat_id = message.chat.id

    if n < 1 or n > MAX_PURGE:
        return await _reply_temp(message, f"❌ تعداد باید بین ۱ تا {MAX_PURGE} باشد.")
    if _enum_name(getattr(message.chat, "type", None)) not in ("GROUP", "SUPERGROUP"):
        return await _reply_temp(message, "❌ این دستور فقط داخل گروه کار می‌کند.")
    _PERM_CACHE.pop((uid, chat_id), None)      # همیشه دسترسیِ لحظه‌ی اجرا را بسنج
    if not await _can_delete(client, uid, chat_id, message.chat.type):
        return await _reply_temp(message, "⚠️ در این گروه دسترسی «حذف پیام» ندارم؛ چیزی پاک نشد.")
    key = (uid, chat_id)
    if key in _RUNNING:
        return await _reply_temp(message, "⏳ یک حذف دیگر در همین گروه در حال انجام است.")

    _RUNNING.add(key)
    try:
        # فقط پیام‌های قبل از خودِ دستور (پیام‌های تازه‌تر که در این فاصله آمده‌اند دست نمی‌خورند)
        ids = []
        async for m in client.get_chat_history(chat_id, limit=n, offset_id=message.id):
            ids.append(m.id)
        done = await _delete_ids(client, chat_id, ids)
        try:
            await client.delete_messages(chat_id, message.id)      # خودِ دستور
        except Exception:
            pass
    finally:
        _RUNNING.discard(key)

    note = f"🧹 {done} پیام حذف شد."
    if done < len(ids):
        note += f"\n⚠️ {len(ids) - done} پیام حذف نشد."
    try:
        r = await client.send_message(chat_id, note)
    except Exception:
        return

    async def _later():
        await asyncio.sleep(REPORT_TTL)
        try:
            await r.delete()
        except Exception:
            pass
    asyncio.create_task(_later())


def register(client):
    pattern = filters.regex(r"^\s*حذف\s+[\d۰-۹٠-٩]+\s+پیام(\s+اخیر)?\s*$")
    client.add_handler(MessageHandler(handler, filters.me & filters.text & (pattern | filters.command("purge", prefixes=["/", "."]))), group=0)
