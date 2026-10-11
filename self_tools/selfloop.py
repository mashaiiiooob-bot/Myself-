"""
ارسال خودکار دوره‌ای پیام در یک چت (`/self_on`, `/self_off`, `/self_status`) — مثل
«تبچی» خودِ سلف، اما روی هر چتی قابل روشن/خاموش کردن، جدا و با ذخیره‌سازی.

/self_on                      -> روشن در همین چت (فاصله و متن پیش‌فرض)
/self_on 10m                  -> فاصله‌ی سفارشی
/self_on 10m سلام به همه       -> فاصله + متن سفارشی
/self_off                     -> خاموش در همین چت
/self_status                  -> فهرست چت‌های فعال این سلف
"""
import asyncio
import re
import time

from pyrogram import filters
from pyrogram.handlers import MessageHandler

try:
    from pyrogram.errors import FloodWait
except ImportError:
    class FloodWait(Exception):
        value = 30

DEFAULT_INTERVAL = 5 * 60
DEFAULT_MESSAGE = "میو"
MIN_INTERVAL = 60            # سقف پایین برای جلوگیری از اسپم/بن شدن حساب
MAX_CHATS_PER_SELF = 15      # سقف تعداد چت‌های هم‌زمان برای هر سلف

_TASKS = {}   # (uid, chat_id) -> asyncio.Task
_G = {}       # shared globals() of bot.py, captured once at register() time

_UNITS = {"s": 1, "m": 60, "h": 3600, "ثانیه": 1, "دقیقه": 60, "ساعت": 3600}


def _parse_interval(token):
    m = re.fullmatch(r"(\d+)\s*(s|m|h|ثانیه|دقیقه|ساعت)?", token or "", re.I)
    if not m:
        return None
    n = int(m.group(1))
    unit = (m.group(2) or "s").lower()
    return n * _UNITS.get(unit, 1)


def _state(g, uid):
    dm = g.get("data_manager")
    if dm is None:
        return {}
    d = dm.get_user_data(uid)
    s = d.get("self_loop")
    if not isinstance(s, dict):
        s = {}
        d["self_loop"] = s
    return s


def _save(g, uid, state):
    dm = g.get("data_manager")
    if dm is not None:
        dm.update_user_data(uid, {"self_loop": state})


def _active_gate(g, uid):
    status = g.get("SELF_ACTIVE_STATUS")
    return status is None or status.get(uid, True)


async def _loop(client, g, uid, chat_id):
    key = (uid, chat_id)
    try:
        while True:
            state = _state(g, uid)
            cfg = state.get(str(chat_id))
            if not cfg:
                return
            if not _active_gate(g, uid):
                await asyncio.sleep(10)
                continue
            try:
                await client.send_message(chat_id, cfg.get("message") or DEFAULT_MESSAGE)
            except FloodWait as fw:
                await asyncio.sleep(int(getattr(fw, "value", 30) or 30) + 2)
                continue
            except Exception:
                return  # chat deleted / kicked / forbidden etc. -> stop quietly
            await asyncio.sleep(max(MIN_INTERVAL, int(cfg.get("interval") or DEFAULT_INTERVAL)))
    except asyncio.CancelledError:
        pass
    finally:
        _TASKS.pop(key, None)


def _start(client, g, uid, chat_id, interval, message):
    key = (uid, chat_id)
    old = _TASKS.get(key)
    if old and not old.done():
        old.cancel()
    state = _state(g, uid)
    state[str(chat_id)] = {"interval": interval, "message": message, "since": time.time()}
    _save(g, uid, state)
    _TASKS[key] = asyncio.create_task(_loop(client, g, uid, chat_id))


def _stop(g, uid, chat_id):
    key = (uid, chat_id)
    t = _TASKS.pop(key, None)
    if t:
        t.cancel()
    state = _state(g, uid)
    existed = state.pop(str(chat_id), None) is not None
    _save(g, uid, state)
    return existed


async def on_handler(client, message):
    g = _G
    uid = client.me.id
    chat_id = message.chat.id
    key = (uid, chat_id)
    if key in _TASKS and not _TASKS[key].done():
        return await message.reply_text("**سلف میو روشنه 😎**")
    state = _state(g, uid)
    if len(state) >= MAX_CHATS_PER_SELF and str(chat_id) not in state:
        return await message.reply_text(f"❌ حداکثر {MAX_CHATS_PER_SELF} چت هم‌زمان مجاز است. اول چند تا را با `/self_off` خاموش کن.")
    parts = (message.text or "").split(maxsplit=2)
    interval, msg_text = DEFAULT_INTERVAL, DEFAULT_MESSAGE
    if len(parts) > 1:
        iv = _parse_interval(parts[1])
        if iv is None:
            return await message.reply_text("فرمت فاصله اشتباه است. مثال: `/self_on 10m سلام`")
        interval = max(MIN_INTERVAL, iv)
        if len(parts) > 2:
            msg_text = parts[2].strip() or DEFAULT_MESSAGE
    _start(client, g, uid, chat_id, interval, msg_text)
    await message.reply_text(f"**سلف میو روشن شد 🔥**\nفاصله: هر {interval} ثانیه")


async def off_handler(client, message):
    g = _G
    uid = client.me.id
    if not _stop(g, uid, message.chat.id):
        return await message.reply_text("**سلف میو خاموشه 💤**")
    await message.reply_text("**سلف میو خاموش شد 🛑**")


async def status_handler(client, message):
    g = _G
    uid = client.me.id
    state = _state(g, uid)
    if not state:
        return await message.reply_text("هیچ چت فعالی نداری.")
    lines = ["📋 **چت‌های فعال سلف میو:**", ""]
    for cid, cfg in state.items():
        lines.append(f"• `{cid}` — هر {cfg.get('interval', DEFAULT_INTERVAL)} ثانیه — «{str(cfg.get('message', DEFAULT_MESSAGE))[:30]}»")
    await message.reply_text("\n".join(lines))


async def resume(client, g):
    """بعد از هر بار استارت سلف، چت‌هایی که قبلاً روشن بوده‌اند دوباره فعال می‌شوند."""
    global _G
    _G = g or _G
    uid = client.me.id
    state = _state(g, uid)
    for cid_s, cfg in list(state.items()):
        try:
            cid = int(cid_s)
        except ValueError:
            continue
        key = (uid, cid)
        if key not in _TASKS:
            _TASKS[key] = asyncio.create_task(_loop(client, g, uid, cid))


def register(client):
    global _G
    _G = getattr(client, "g", None) or _G
    client.add_handler(MessageHandler(on_handler, filters.me & filters.command("self_on", prefixes=["/", "."])), group=0)
    client.add_handler(MessageHandler(off_handler, filters.me & filters.command("self_off", prefixes=["/", "."])), group=0)
    client.add_handler(MessageHandler(status_handler, filters.me & filters.command("self_status", prefixes=["/", "."])), group=0)
