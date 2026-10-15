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

حذف خودکار (برای هر اسلات جدا تنظیم می‌شود، فقط در گروه‌هایی کار می‌کند که اکانت
شما مالک یا ادمینِ دارای دسترسی «حذف پیام» است؛ در بقیه‌ی چت‌ها هیچ پیامی حذف نمی‌شود):
/self_del 2 own                 -> پیامی که اسلات 2 می‌فرستد بلافاصله پاک شود
/self_del 2 bot                 -> اولین پیامِ رباتیِ بعد از آن هم بلافاصله پاک شود
/self_del 2 both                -> هر دو
/self_del 2 off                 -> خاموش‌کردن حذف خودکار برای اسلات 2
/self_del 2 own 3               -> پیام خودت را ۳ ثانیه بعد پاک کن (اختیاری، ۰ تا ۶۰)
/self_del 2                     -> نمایش وضعیت حذف اسلات 2 و دسترسی فعلی
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

BOT_WAIT = 20                  # چند ثانیه منتظر پیامِ ربات بعد از ارسال می‌مانیم
PERM_TTL = 300                 # مدت نگه‌داشتن نتیجه‌ی بررسی دسترسی حذف (ثانیه)
MAX_OWN_DELAY = 60

_TASKS = {}   # (uid, chat_id, slot) -> asyncio.Task
_WATCH = {}   # (uid, chat_id) -> [(msg_id_ارسالی, deadline)]  منتظر پیامِ ربات بعدی
_PERM_CACHE = {}   # (uid, chat_id) -> (زمان, می‌تواند_حذف_کند)
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


def _enum_name(x):
    if x is None:
        return None
    name = getattr(x, "name", None) or str(x)
    return str(name).split(".")[-1].upper()


async def _can_delete(client, uid, chat_id, chat_type=None):
    """True فقط اگر چت گروه/سوپرگروه باشد و اکانت ما مالک یا ادمینِ دارای دسترسی حذف پیام باشد."""
    now = time.monotonic()
    hit = _PERM_CACHE.get((uid, chat_id))
    if hit and now - hit[0] < PERM_TTL:
        return hit[1]
    ok = False
    try:
        ctype = _enum_name(chat_type)
        if ctype is None:
            ctype = _enum_name((await client.get_chat(chat_id)).type)
        if ctype in ("GROUP", "SUPERGROUP"):
            member = await client.get_chat_member(chat_id, "me")
            st = _enum_name(getattr(member, "status", None))
            if st in ("OWNER", "CREATOR"):
                ok = True
            elif st == "ADMINISTRATOR":
                priv = getattr(member, "privileges", None) or member
                ok = bool(getattr(priv, "can_delete_messages", False))
    except Exception:
        ok = False
    _PERM_CACHE[(uid, chat_id)] = (now, ok)
    return ok


async def _safe_delete(client, uid, chat_id, msg_id):
    try:
        await client.delete_messages(chat_id, msg_id)
        return True
    except Exception as e:
        if type(e).__name__ in ("ChatAdminRequired", "MessageDeleteForbidden", "ChatWriteForbidden"):
            _PERM_CACHE[(uid, chat_id)] = (time.monotonic(), False)
        return False


async def _delayed_delete(client, uid, chat_id, msg_id, delay):
    await asyncio.sleep(delay)
    await _safe_delete(client, uid, chat_id, msg_id)


def _watch_add(uid, chat_id, msg_id):
    now = time.monotonic()
    lst = [w for w in _WATCH.get((uid, chat_id), []) if w[1] > now]
    lst.append((msg_id, now + BOT_WAIT))
    _WATCH[(uid, chat_id)] = lst[-5:]


async def _after_send(client, uid, chat_id, cfg, sent):
    """بعد از هر ارسالِ اسلات: طبق تنظیم همان اسلات، پیام خودمان را پاک می‌کند و/یا
    منتظر اولین پیامِ رباتیِ بعدی می‌ماند تا آن را هم پاک کند."""
    want_own, want_bot = bool(cfg.get("del_own")), bool(cfg.get("del_bot"))
    if sent is None or not (want_own or want_bot):
        return
    ctype = getattr(getattr(sent, "chat", None), "type", None)
    if not await _can_delete(client, uid, chat_id, ctype):
        return
    if want_bot:
        _watch_add(uid, chat_id, sent.id)
    if want_own:
        delay = int(cfg.get("del_delay") or 0)
        if delay > 0:
            asyncio.create_task(_delayed_delete(client, uid, chat_id, sent.id, delay))
        else:
            await _safe_delete(client, uid, chat_id, sent.id)


async def bot_reply_handler(client, message):
    """هر پیامِ رباتیِ ورودی در گروه: اگر بعد از ارسالِ یک اسلات (با حذفِ ربات روشن) رسیده
    باشد — یا ریپلای به همان پیام باشد — بلافاصله پاک می‌شود. فقط اولین پیام برای هر ارسال."""
    uid = client.me.id
    chat_id = message.chat.id
    key = (uid, chat_id)
    lst = _WATCH.get(key)
    if not lst:
        return
    now = time.monotonic()
    lst = [w for w in lst if w[1] > now]
    reply_to = getattr(message, "reply_to_message_id", None)
    hit = None
    for w in lst:   # قدیمی‌ترین ارسال اول
        if message.id <= w[0]:
            continue
        if reply_to is None or reply_to == w[0]:
            hit = w
            break
    if hit is None:
        if lst:
            _WATCH[key] = lst
        else:
            _WATCH.pop(key, None)
        return
    lst.remove(hit)
    if lst:
        _WATCH[key] = lst
    else:
        _WATCH.pop(key, None)
    if await _can_delete(client, uid, chat_id, getattr(message.chat, "type", None)):
        await _safe_delete(client, uid, chat_id, message.id)


_DEL_MODES = {
    "own": (True, False), "خودم": (True, False), "پیام": (True, False),
    "bot": (False, True), "ربات": (False, True),
    "both": (True, True), "هردو": (True, True), "هر_دو": (True, True),
    "off": (False, False), "خاموش": (False, False),
}


def _parse_del_args(arg_str):
    """-> (slot, mode-or-None, delay-or-None). mode یکی از کلیدهای _DEL_MODES یا None (فقط نمایش)."""
    toks = (arg_str or "").replace(":", " ").split()
    slot = 1
    if toks and toks[0].isdigit():
        slot = int(toks.pop(0))
        if not (1 <= slot <= MAX_SLOTS_PER_CHAT):
            raise ValueError(f"شماره‌ی اسلات باید بین ۱ تا {MAX_SLOTS_PER_CHAT} باشد.")
    if not toks:
        return slot, None, None
    mode = toks.pop(0).lower()
    if mode not in _DEL_MODES:
        raise ValueError(
            "حالت نامعتبر است.\n"
            "`/self_del 2 own` پیام خودِ اسلات\n"
            "`/self_del 2 bot` پیامِ رباتِ بعدی\n"
            "`/self_del 2 both` هر دو\n"
            "`/self_del 2 off` خاموش\n"
            "تأخیر اختیاری برای پیام خودت: `/self_del 2 own 3`"
        )
    delay = None
    if toks:
        m = re.fullmatch(r"(\d+)\s*(s|ثانیه)?", toks[0], re.I)
        if not m or not (0 <= int(m.group(1)) <= MAX_OWN_DELAY):
            raise ValueError(f"تأخیر باید عددی بین ۰ تا {MAX_OWN_DELAY} ثانیه باشد.")
        delay = int(m.group(1))
    return slot, mode, delay


def _del_txt(cfg):
    own, bot = bool(cfg.get("del_own")), bool(cfg.get("del_bot"))
    if not (own or bot):
        return "خاموش"
    parts = []
    if own:
        d = int(cfg.get("del_delay") or 0)
        parts.append("پیام خودم" + (f" (بعد از {d}ث)" if d else " (بلافاصله)"))
    if bot:
        parts.append("پیام رباتِ بعدی")
    return " + ".join(parts)


async def del_handler(client, message):
    g = _G
    uid = client.me.id
    chat_id = message.chat.id
    parts = (message.text or "").split(maxsplit=1)
    try:
        slot, mode, delay = _parse_del_args(parts[1] if len(parts) > 1 else "")
    except ValueError as e:
        return await message.reply_text(str(e))
    state = _state(g, uid)
    chat_state = state.get(str(chat_id))
    if isinstance(chat_state, dict):
        _migrate_chat_state(chat_state)
    cfg = chat_state.get(str(slot)) if isinstance(chat_state, dict) else None
    if not cfg:
        return await message.reply_text(f"اسلات {slot} در این چت روشن نیست. اول `/self_on {slot}:` را بزن.")
    if mode is not None:
        own, bot = _DEL_MODES[mode]
        cfg["del_own"], cfg["del_bot"] = own, bot
        if delay is not None:
            cfg["del_delay"] = delay
        if not own:
            cfg.pop("del_delay", None)
        if not (own or bot):
            cfg.pop("del_own", None)
            cfg.pop("del_bot", None)
        _save(g, uid, state)
    _PERM_CACHE.pop((uid, chat_id), None)
    can = await _can_delete(client, uid, chat_id, getattr(message.chat, "type", None))
    perm = ("✅ در این چت دسترسی حذف پیام دارم." if can else
            "⚠️ این چت گروه نیست یا دسترسی «حذف پیام» ندارم؛ تا آن را نگیرم هیچ پیامی پاک نمی‌شود.")
    await message.reply_text(f"**اسلات {slot} — حذف خودکار:** {_del_txt(cfg)}\n{perm}")


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
                sent = await client.send_message(chat_id, cfg.get("message") or DEFAULT_MESSAGE)
            except FloodWait as fw:
                await asyncio.sleep(int(getattr(fw, "value", 30) or 30) + 2)
                continue
            except Exception:
                return  # چت حذف شده / اخراج شده / دسترسی نداریم و... -> بی‌سروصدا متوقف شو
            try:
                await _after_send(client, uid, chat_id, cfg, sent)
            except Exception:
                pass    # خطای حذف نباید حلقه‌ی ارسال را بکشد
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
    prev = chat_state.get(str(slot)) or {}
    cfg = {"message": message, "since": time.time()}
    for k in ("del_own", "del_bot", "del_delay"):
        if prev.get(k):
            cfg[k] = prev[k]
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
            del_mark = f" — 🗑 {_del_txt(cfg)}" if (cfg.get("del_own") or cfg.get("del_bot")) else ""
            lines.append(f"  • اسلات {slot_s} — {timing_txt} — «{str(cfg.get('message', DEFAULT_MESSAGE))[:30]}»{del_mark}")
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
    client.add_handler(MessageHandler(del_handler, filters.me & filters.command("self_del", prefixes=["/", "."])), group=0)
    # گروه -20: قبل از هندلرهایی که StopPropagation می‌اندازند اجرا شود
    client.add_handler(MessageHandler(bot_reply_handler, filters.incoming & filters.bot & filters.group), group=-20)
