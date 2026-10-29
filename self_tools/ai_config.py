"""Per-user AI configuration (persisted), personas, conversation memory and quota."""
import copy, datetime, time
from collections import OrderedDict

PERSONAS = OrderedDict([
    ("default", ("پیش‌فرض", "تو «دارک‌سلف»، دستیار هوشمند فارسی‌زبانِ صاحب این حساب هستی. دقیق، کوتاه و خودمونی جواب بده. "
                 "اگر کاربر فارسی نوشت فارسی و اگر انگلیسی نوشت انگلیسی جواب بده. اگر مطمئن نیستی صادقانه بگو.")),
    ("coder", ("برنامه‌نویس", "تو یک مهندس نرم‌افزار ارشد هستی. کد تمیز و کامل بنویس، داخل بلوک ``` بگذار، "
               "قبل از کد یک خط توضیح بده و بعدش نکات مهم یا خطاهای محتمل را کوتاه بگو.")),
    ("teacher", ("معلم", "تو یک معلم صبور هستی. مفهوم را از ساده شروع کن، مثال بزن، و در پایان یک سوال کوتاه برای سنجش بپرس.")),
    ("writer", ("نویسنده", "تو یک ویراستار و نویسندهٔ حرفه‌ای فارسی هستی. متن روان، زیبا و بدون غلط بنویس یا اصلاح کن.")),
    ("analyst", ("تحلیلگر", "تو تحلیلگر دقیقی هستی. ابتدا نتیجه را در یک خط بگو، بعد دلیل‌ها و ریسک‌ها را در فهرست کوتاه بیاور.")),
    ("friend", ("رفیق", "تو یک دوست صمیمی و بامزه هستی. خودمونی و با شوخی ملایم حرف بزن، ولی اطلاعاتت درست باشد.")),
    ("short", ("خیلی کوتاه", "حداکثر دو جمله جواب بده. بدون مقدمه.")),
])

TONES = {"رسمی": "لحن رسمی و مؤدبانه", "دوستانه": "لحن دوستانه و صمیمی", "کوتاه": "کوتاه‌تر و فشرده‌تر",
         "مودبانه": "بسیار مؤدبانه", "شوخ": "با شوخ‌طبعی ملایم", "ساده": "ساده‌تر برای فهم همه"}

DEFAULTS = {
    "persona": "default", "custom_persona": "", "stream": True, "search": True, "footer": True,
    "provider": "auto", "keys": {}, "models": {}, "custom": {},
    "facts": [], "daily_limit": 200, "quota": {"day": "", "used": 0}, "stats": {"calls": 0, "tokens_in": 0, "tokens_out": 0},
    "chats": {},
    "auto": {"enabled": False, "label": True, "label_text": "🤖 دستیار هوشمند", "note": "",
             "handoff_min": 15, "max_per_hour": 10, "allow": [], "deny": [], "notify": True},
}
MAX_FACTS, MAX_CHATS = 40, 150
_CACHE = {}


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(out.get(k), dict) and isinstance(v, dict) and k not in ("keys", "models", "custom", "chats"):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def get_cfg(env, uid):
    if uid in _CACHE:
        return _CACHE[uid]
    saved = {}
    try:
        saved = env.data_manager.get_user_data(uid).get("ai") or {}
    except Exception:
        pass
    _CACHE[uid] = _merge(DEFAULTS, saved)
    return _CACHE[uid]


def save_cfg(env, uid):
    try:
        env.data_manager.update_user_data(uid, {"ai": _CACHE[uid]})
    except Exception:
        pass


def chat_cfg(cfg, chat_id):
    c = cfg["chats"].get(str(chat_id))
    if c is None:
        if len(cfg["chats"]) >= MAX_CHATS:
            cfg["chats"].pop(next(iter(cfg["chats"])))
        c = cfg["chats"][str(chat_id)] = {}
    return c


def persona_name(cfg, chat_id=None):
    p = (chat_cfg(cfg, chat_id).get("persona") if chat_id is not None else None) or cfg["persona"]
    return p


def system_prompt(env, cfg, chat_id=None, extra=""):
    p = persona_name(cfg, chat_id)
    base = cfg["custom_persona"] if p == "custom" and cfg["custom_persona"] else PERSONAS.get(p, PERSONAS["default"])[1]
    parts = [base, now_line()]
    if cfg["facts"]:
        parts.append("اطلاعاتی که دربارهٔ صاحب حساب می‌دانی:\n" + "\n".join("- " + f for f in cfg["facts"]))
    if extra:
        parts.append(extra)
    return "\n\n".join(parts)


def now_line():
    try:
        from zoneinfo import ZoneInfo
        n = datetime.datetime.now(ZoneInfo("Asia/Tehran"))
    except Exception:
        n = datetime.datetime.utcnow() + datetime.timedelta(hours=3, minutes=30)
    try:
        import jdatetime
        j = jdatetime.datetime.fromgregorian(datetime=n)
        return "اکنون (تهران): %s %s — %s" % (j.strftime("%Y/%m/%d"), n.strftime("%H:%M"), n.strftime("%Y-%m-%d"))
    except Exception:
        return "اکنون (تهران): " + n.strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------- quota
def quota_check(cfg, cost=1):
    today = datetime.date.today().isoformat()
    q = cfg["quota"]
    if q["day"] != today:
        q["day"], q["used"] = today, 0
    return q["used"] + cost <= int(cfg["daily_limit"]), int(cfg["daily_limit"]) - q["used"]


def quota_use(cfg, cost=1, tin=0, tout=0):
    quota_check(cfg, 0)
    cfg["quota"]["used"] += cost
    s = cfg["stats"]
    s["calls"] += 1; s["tokens_in"] += tin; s["tokens_out"] += tout


# ---------------------------------------------------------------- memory
class Memory:
    """Rolling per-(user,chat) conversation with automatic compaction by summarisation."""
    BUDGET, KEEP = 7000, 6

    def __init__(self):
        self.turns, self.summary, self.ts = [], "", time.time()

    def size(self):
        return len(self.summary) + sum(len(t["content"]) for t in self.turns)

    def add(self, role, content):
        self.turns.append({"role": role, "content": content[:3000]})
        self.ts = time.time()

    def messages(self):
        out = []
        if self.summary:
            out.append({"role": "system", "content": "خلاصهٔ گفتگوی قبلی: " + self.summary})
        return out + list(self.turns)

    def needs_compaction(self):
        return self.size() > self.BUDGET and len(self.turns) > self.KEEP

    def split_old(self):
        old, self.turns = self.turns[:-self.KEEP], self.turns[-self.KEEP:]
        return old


_MEM = {}


def memory(uid, chat_id):
    k = (uid, chat_id)
    if len(_MEM) > 400:                                    # evict the oldest 100 idle conversations
        for key, _ in sorted(_MEM.items(), key=lambda kv: kv[1].ts)[:100]:
            _MEM.pop(key, None)
    return _MEM.setdefault(k, Memory())


def forget(uid, chat_id):
    return _MEM.pop((uid, chat_id), None) is not None
