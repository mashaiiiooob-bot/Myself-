"""
ارسال خودکار دوره‌ای پیام در یک چت، با چند «اسلات» مستقل در هر چت — هرکدام با
فاصله و متن خودش (مثل «تبچی» خودِ سلف، ولی قابل تنظیم روی هر چتی، جدا جدا).

فاصله می‌تواند یک عدد ثابت باشد، یا یک بازه (مثل 5m-7m) که هر بار یک مقدار
تصادفی و متفاوتِ داخل همان بازه انتخاب می‌شود (هیچ‌وقت دقیقاً روی دو سرِ بازه
نمی‌افتد) تا ریتم ارسال ثابت و قابل‌تشخیص نباشد.

/self_on                        -> اسلات 1 در همین چت، فاصله و متن پیش‌فرض
/self_on 10m                    -> اسلات 1، فاصله‌ی ثابت
/self_on 5m-7m                  -> اسلات 1، فاصله‌ی تصادفی بین ۵ تا ۷ دقیقه
/self_on 10m سلام به همه         -> اسلات 1، فاصله + متن سفارشی
/self_on 2: 5m-7m یخچال میویی    -> اسلات 2 (جدا از اسلات 1)، فاصله + متن خودش
/self_on 2:                     -> اسلات 2 با فاصله/متن پیش‌فرض

/self_off                       -> خاموش‌کردن همه‌ی اسلات‌های همین چت
/self_off 2                     -> خاموش‌کردن فقط اسلات 2 در همین چت
/self_status                    -> فهرست همه‌ی چت‌ها و اسلات‌های فعال این سلف
"""
import asyncio
import random
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
MIN_INTERVAL = 60              # سقف پایین برای جلوگیری از اسپم/بن شدن حساب
MIN_RANGE_GAP = 3              # کمترین فاصله‌ی مجاز بین دو سر بازه (تا نقطه‌ی داخلی واقعی وجود داشته باشد)
MAX_SLOTS_PER_CHAT = 5         # سقف تعداد اسلات هم‌زمان در یک چت
MAX_SLOTS_PER_SELF = 20        # سقف تعداد اسلات هم‌زمان در کل چت‌های این سلف

_TASKS = {}   # (uid, chat_id, slot) -> asyncio.Task
_G = {}       # shared globals() of bot.py, captured در register()/resume()

_UNITS = {"s": 1, "m": 60, "h": 3600, "ثانیه": 1, "دقیقه": 60, "ساعت": 3600}


def _parse_interval(token):
    m = re.fullmatch(r"(\d+)\s*(s|m|h|ثانیه|دقیقه|ساعت)?", token or "", re.I)
    if not m:
        return None
    n = int(m.group(1))
    unit = (m.group(2) or "s").lower()
    return n * _UNITS.get(unit, 1)


def _fmt_dur(sec):
    sec = int(sec)
    m, s = divmod(sec, 60)
    return f"{m}:{s:02d}"


def _parse_interval_spec(token):
    """یک فاصله‌ی ثابت ('10m') یا یک بازه‌ی نامنظم/جیتردار ('5m-7m') را می‌خواند.
    خروجی: {"fixed": ثانیه}  یا  {"lo": ثانیه, "hi": ثانیه}  یا  None اگر نامعتبر بود."""
    token = (token or "").strip()
    if "-" in token:
        lo_s, _, hi_s = token.partition("-")
        lo, hi = _parse_interval(lo_s), _parse_interval(hi_s)
        if lo is None or hi is None:
            return None
        if lo > hi:
            lo, hi = hi, lo
        lo = max(MIN_INTERVAL, lo)
        if hi - lo < MIN_RANGE_GAP:
            return None
        return {"lo": lo, "hi": hi}
    iv = _parse_interval(token)
    if iv is None:
        return None
    return {"fixed": max(MIN_INTERVAL, iv)}


def _next_delay(cfg):
    """فاصله‌ی واقعی تا ارسال بعدی: عدد ثابت، یا یک انتخاب تصادفیِ پیوسته (نه فقط چند حالت
    محدود/شمارشی، بلکه هر عدد اعشاری ممکن) از داخل بازه — هیچ‌وقت دقیقاً روی دو سر بازه
    نمی‌افتد، و از بی‌نهایت مقدار ممکن بین آن دو مرز انتخاب می‌شود."""
    if "lo" in cfg and "hi" in cfg:
        lo, hi = float(cfg["lo"]), float(cfg["hi"])
        if hi <= lo:
            return max(MIN_INTERVAL, lo)
        eps = min(0.25, (hi - lo) / 1000)  # تضمین می‌کند دقیقاً روی خودِ مرزها نیفتد
        return random.uniform(lo + eps, hi - eps)
    return max(MIN_INTERVAL, int(cfg.get("interval") or DEFAULT_INTERVAL))


def _parse_on_args(arg_str):
    """-> (slot, interval_spec-or-None, message-or-None) ؛ None یعنی «همان قبلی یا پیش‌فرض بماند».
    interval_spec یا {"fixed": ثانیه} است یا {"lo":..,"hi":..} برای حالت تصادفیِ بازه‌ای.
    در خطای فرمت، ValueError با پیام فارسی قابل‌نمایش می‌اندازد."""
    s = (arg_str or "").strip()
    slot = 1
    m = re.match(r"^(\d{1,2}):\s*", s)
    if m:
        slot = int(m.group(1))
        if not (1 <= slot <= MAX_SLOTS_PER_CHAT):
            raise ValueError(f"شماره‌ی اسلات باید بین ۱ تا {MAX_SLOTS_PER_CHAT} باشد.")
        s = s[m.end():]
    if not s:
        return slot, None, None
    parts = s.split(maxsplit=1)
    spec = _parse_interval_spec(parts[0])
    if spec is None:
        raise ValueError(
            "فرمت فاصله اشتباه است.\n"
            "فاصله‌ی ثابت: `/self_on 10m سلام`\n"
            "فاصله‌ی نامنظم (تصادفی داخل بازه، برای جلوگیری از ریتم ثابت): `/self_on 5m-7m سلام`\n"
            f"برای اسلات دوم: `/self_on 2: 5m-7m یخچال میویی`\n"
            f"(هر دو سر بازه باید حداقل {MIN_RANGE_GAP} ثانیه فاصله داشته باشند)"
        )
    message = parts[1].strip() if len(parts) > 1 else None
    return slot, spec, message


def _migrate_chat_state(chat_state):
    """سازگاری با فرمت قدیمی (یک اسلات تک، بدون شماره) اگر از نسخه‌ی قبلی باقی مانده باشد."""
    if "interval" in chat_state and "message" in chat_state:
        old = dict(chat_state)
        chat_state.clear()
        chat_state["1"] = old


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


async def _loop(client, g, uid, chat_id, slot):
    key = (uid, chat_id, slot)
    try:
        while True:
            state = _state(g, uid)
            chat_state = state.get(str(chat_id))
            if not isinstance(chat_state, dict):
                return
            _migrate_chat_state(chat_state)
            cfg = chat_state.get(str(slot))
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
                return  # چت حذف شده / اخراج شده / دسترسی نداریم و... -> بی‌سروصدا متوقف شو
            await asyncio.sleep(_next_delay(cfg))
    except asyncio.CancelledError:
        pass
    finally:
        _TASKS.pop(key, None)


def _start(client, g, uid, chat_id, slot, interval_spec, message):
    key = (uid, chat_id, slot)
    old = _TASKS.get(key)
    if old and not old.done():
        old.cancel()
    state = _state(g, uid)
    chat_state = state.setdefault(str(chat_id), {})
    _migrate_chat_state(chat_state)
    cfg = {"message": message, "since": time.time()}
    if "lo" in interval_spec:
        cfg["lo"], cfg["hi"] = interval_spec["lo"], interval_spec["hi"]
    else:
        cfg["interval"] = interval_spec["fixed"]
    chat_state[str(slot)] = cfg
    _save(g, uid, state)
    _TASKS[key] = asyncio.create_task(_loop(client, g, uid, chat_id, slot))


def _total_active_slots(state):
    return sum(len(v) for v in state.values() if isinstance(v, dict))


async def on_handler(client, message):
    g = _G
    uid = client.me.id
    chat_id = message.chat.id
    parts = (message.text or "").split(maxsplit=1)
    arg_str = parts[1] if len(parts) > 1 else ""
    try:
        slot, interval_spec, msg_text = _parse_on_args(arg_str)
    except ValueError as e:
        return await message.reply_text(str(e))

    key = (uid, chat_id, slot)
    already_on = key in _TASKS and not _TASKS[key].done()
    if already_on and interval_spec is None and msg_text is None:
        return await message.reply_text(f"**اسلات {slot} همین چت از قبل روشنه 😎**")

    state = _state(g, uid)
    chat_state = state.setdefault(str(chat_id), {})
    _migrate_chat_state(chat_state)
    is_new_slot = str(slot) not in chat_state

    if is_new_slot:
        if len(chat_state) >= MAX_SLOTS_PER_CHAT:
            return await message.reply_text(f"❌ حداکثر {MAX_SLOTS_PER_CHAT} اسلات هم‌زمان در هر چت مجاز است. اول یکی را با `/self_off [شماره]` خاموش کن.")
        if _total_active_slots(state) >= MAX_SLOTS_PER_SELF:
            return await message.reply_text(f"❌ حداکثر {MAX_SLOTS_PER_SELF} اسلات هم‌زمان (در کل چت‌ها) مجاز است.")

    existing = chat_state.get(str(slot), {})
    if interval_spec is not None:
        final_spec = interval_spec
    elif "lo" in existing:
        final_spec = {"lo": existing["lo"], "hi": existing["hi"]}
    else:
        final_spec = {"fixed": int(existing.get("interval") or DEFAULT_INTERVAL)}
    final_message = msg_text if msg_text is not None else (existing.get("message") or DEFAULT_MESSAGE)
    _start(client, g, uid, chat_id, slot, final_spec, final_message)

    if "lo" in final_spec:
        timing_txt = f"بین {_fmt_dur(final_spec['lo'])} تا {_fmt_dur(final_spec['hi'])} (هر بار تصادفی و متفاوت)"
    else:
        timing_txt = f"هر {_fmt_dur(final_spec['fixed'])}"
    await message.reply_text(
        f"**اسلات {slot} روشن شد 🔥**\nفاصله: {timing_txt}\nمتن: «{final_message}»"
    )


async def off_handler(client, message):
    g = _G
    uid = client.me.id
    chat_id = message.chat.id
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""

    state = _state(g, uid)
    chat_state = state.get(str(chat_id))
    if not isinstance(chat_state, dict) or not chat_state:
        return await message.reply_text("**این چت اسلات فعالی نداره 💤**")
    _migrate_chat_state(chat_state)

    if arg:
        if not arg.isdigit():
            return await message.reply_text("فرمت اشتباه است.\nمثال: `/self_off 2` یا فقط `/self_off` برای خاموش‌کردن همه‌ی اسلات‌های این چت.")
        slot = int(arg)
        if str(slot) not in chat_state:
            return await message.reply_text(f"اسلات {slot} در این چت فعال نیست.")
        key = (uid, chat_id, slot)
        t = _TASKS.pop(key, None)
        if t:
            t.cancel()
        chat_state.pop(str(slot), None)
        if not chat_state:
            state.pop(str(chat_id), None)
        _save(g, uid, state)
        return await message.reply_text(f"**اسلات {slot} خاموش شد 🛑**")

    n = 0
    for slot_s in list(chat_state.keys()):
        key = (uid, chat_id, int(slot_s))
        t = _TASKS.pop(key, None)
        if t:
            t.cancel()
        n += 1
    state.pop(str(chat_id), None)
    _save(g, uid, state)
    await message.reply_text(f"**{n} اسلات در این چت خاموش شد 🛑**")


async def status_handler(client, message):
    g = _G
    uid = client.me.id
    state = _state(g, uid)
    lines = ["📋 **اسلات‌های فعال سلف میو:**", ""]
    found = False
    for cid_s, chat_state in state.items():
        if not isinstance(chat_state, dict) or not chat_state:
            continue
        _migrate_chat_state(chat_state)
        if not chat_state:
            continue
        found = True
        lines.append(f"💬 چت `{cid_s}`:")
        for slot_s, cfg in sorted(chat_state.items(), key=lambda kv: int(kv[0])):
            if "lo" in cfg:
                timing_txt = f"بین {_fmt_dur(cfg['lo'])} تا {_fmt_dur(cfg['hi'])}"
            else:
                timing_txt = f"هر {_fmt_dur(cfg.get('interval', DEFAULT_INTERVAL))}"
            lines.append(f"  • اسلات {slot_s} — {timing_txt} — «{str(cfg.get('message', DEFAULT_MESSAGE))[:30]}»")
    if not found:
        return await message.reply_text("هیچ چت فعالی نداری.")
    await message.reply_text("\n".join(lines))


async def resume(client, g):
    """بعد از هر بار استارت سلف، اسلات‌هایی که قبلاً روشن بوده‌اند دوباره فعال می‌شوند."""
    global _G
    _G = g or _G
    uid = client.me.id
    state = _state(g, uid)
    for cid_s, chat_state in list(state.items()):
        if not isinstance(chat_state, dict):
            continue
        _migrate_chat_state(chat_state)
        try:
            cid = int(cid_s)
        except ValueError:
            continue
        for slot_s in list(chat_state.keys()):
            try:
                slot = int(slot_s)
            except ValueError:
                continue
            key = (uid, cid, slot)
            if key not in _TASKS:
                _TASKS[key] = asyncio.create_task(_loop(client, g, uid, cid, slot))


def register(client):
    global _G
    _G = getattr(client, "g", None) or _G
    client.add_handler(MessageHandler(on_handler, filters.me & filters.command("self_on", prefixes=["/", "."])), group=0)
    client.add_handler(MessageHandler(off_handler, filters.me & filters.command("self_off", prefixes=["/", "."])), group=0)
    client.add_handler(MessageHandler(status_handler, filters.me & filters.command("self_status", prefixes=["/", "."])), group=0)
