"""Pure, dependency-light logic behind the utility commands (unit-tested offline)."""
import ast, datetime as dt, hashlib, json, math, operator, re, secrets, string
from .common import fa_digits

# ---------------------------------------------------------------- calc
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {n: getattr(math, n) for n in ("sqrt", "sin", "cos", "tan", "asin", "acos", "atan", "log", "log10", "exp",
                                        "floor", "ceil", "fabs", "factorial", "radians", "degrees")}
_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}
MAX_ABS = 10 ** 100


def _ev(n, depth=0):
    if depth > 40:
        raise ValueError("عبارت خیلی تو در تو است")
    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
        if not math.isfinite(n.value) or abs(n.value) > MAX_ABS:
            raise ValueError("عدد نامعتبر یا خیلی بزرگ")
        return n.value
    if isinstance(n, ast.Name) and n.id in _CONSTS:
        return _CONSTS[n.id]
    if isinstance(n, ast.UnaryOp) and type(n.op) in _OPS:
        return _OPS[type(n.op)](_ev(n.operand, depth + 1))
    if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
        a, b = _ev(n.left, depth + 1), _ev(n.right, depth + 1)
        op = type(n.op)
        if op is ast.Pow and (abs(b) > 100 or abs(a) > 10 ** 12):
            raise ValueError("توان خیلی بزرگ است")
        if op in (ast.Div, ast.FloorDiv, ast.Mod) and b == 0:
            raise ValueError("تقسیم بر صفر")
        r = _OPS[op](a, b)
        if isinstance(r, complex) or not math.isfinite(r) or abs(r) > MAX_ABS:
            raise ValueError("نتیجه نامعتبر یا خیلی بزرگ")
        return r
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS and not n.keywords and 0 < len(n.args) <= 2:
        args = [_ev(x, depth + 1) for x in n.args]
        if n.func.id == "factorial" and (args[0] > 170 or args[0] < 0 or args[0] != int(args[0])):
            raise ValueError("فاکتوریل فقط برای صحیح ۰ تا ۱۷۰")
        return _FUNCS[n.func.id](*([int(args[0])] if n.func.id == "factorial" else args))
    raise ValueError("عبارت غیرمجاز")


def calculate(expr):
    s = fa_digits(expr.strip()).replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**").replace("٫", ".")
    s = re.sub(r"(?<=\d),(?=\d{3}\b)", "", s)
    if not s or len(s) > 300:
        raise ValueError("عبارت خالی یا خیلی بلند")
    return _ev(ast.parse(s, mode="eval").body)


def fmt_num(x):
    if isinstance(x, float) and x == int(x) and abs(x) < 1e15:
        x = int(x)
    return ("{:,}".format(x) if isinstance(x, int) else ("%.10g" % x))


# ---------------------------------------------------------------- units / world clock (tables come from the original tools)
from .data_tables import CITIES, QUICK_CITIES, UNITS as _UNITS

_TEMP = {"c": "c", "celsius": "c", "سانتیگراد": "c", "f": "f", "fahrenheit": "f", "فارنهایت": "f", "k": "k", "kelvin": "k", "کلوین": "k"}


def convert(x, a, b):
    a, b = a.lower().strip(), b.lower().strip()
    if a in _TEMP and b in _TEMP:
        a, b = _TEMP[a], _TEMP[b]
        c = x if a == "c" else (x - 32) * 5 / 9 if a == "f" else x - 273.15
        return c if b == "c" else c * 9 / 5 + 32 if b == "f" else c + 273.15
    for table in _UNITS.values():
        if a in table and b in table:
            return x * table[a] / table[b]
    raise ValueError("واحد ناشناخته یا نامتجانس")


_CAT = (("length", "📐 طول"), ("weight", "⚖️ وزن"), ("volume", "🧴 حجم"), ("area", "📦 مساحت"),
        ("speed", "🏎 سرعت"), ("digital", "💾 داده"), ("time", "⏱ زمان"))


def units_text():
    rows = ["%s: %s" % (title, " ".join(list(_UNITS[k])[:8])) for k, title in _CAT]
    return "\n".join(rows + ["🌡 دما: c f k"])


UNIT_HELP = units_text()


def resolve_tz(name):
    n = (name or "").strip()
    return CITIES.get(n.lower()) or CITIES.get(n) or (n if "/" in n else None)


def cities_text():
    seen, rows = set(), []
    for name, tz in sorted(CITIES.items(), key=lambda kv: kv[1]):
        if tz not in seen:
            seen.add(tz)
            rows.append(name)
    return rows


# ---------------------------------------------------------------- passwords / hash / b64 / json
SETS = {"l": string.ascii_lowercase, "u": string.ascii_uppercase, "d": string.digits, "s": "!@#$%^&*()-_=+[]{};:,.?"}


def make_password(length=16, sets="luds"):
    sets = [s for s in dict.fromkeys(sets.lower()) if s in SETS]
    if not sets:
        raise ValueError("حداقل یکی از l u d s")
    if not 6 <= length <= 128:
        raise ValueError("طول باید ۶ تا ۱۲۸ باشد")
    pool = "".join(SETS[s] for s in sets)
    out = [secrets.choice(SETS[s]) for s in sets] + [secrets.choice(pool) for _ in range(length - len(sets))]
    secrets.SystemRandom().shuffle(out)
    return "".join(out)


def entropy_bits(length, sets):
    return length * math.log2(sum(len(SETS[s]) for s in set(sets) if s in SETS) or 1)


ALGS = ("md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s", "sha3_256")


def pretty_json(text):
    return json.dumps(json.loads(text), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- age / bmi
def parse_birth(s):
    m = re.match(r"^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$", fa_digits(s.strip()))
    if not m:
        raise ValueError("قالب: ۱۳۷۵/۰۵/۱۰ یا 1996-08-01")
    y, mo, d = map(int, m.groups())
    if y < 1700:                                                 # Jalali
        try:
            import jdatetime
            return jdatetime.date(y, mo, d).togregorian()
        except ImportError:
            raise ValueError("برای تاریخ شمسی `pip install jdatetime` لازم است")
    return dt.date(y, mo, d)


def age_info(birth, today=None):
    today = today or dt.date.today()
    if birth > today:
        raise ValueError("تاریخ تولد در آینده است")
    y = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    mo = (today.month - birth.month - (today.day < birth.day)) % 12
    nxt = birth.replace(year=today.year) if not (birth.month == 2 and birth.day == 29) else dt.date(today.year, 3, 1)
    if nxt < today:
        nxt = nxt.replace(year=today.year + 1) if not (birth.month == 2 and birth.day == 29) else dt.date(today.year + 1, 3, 1)
    return {"years": y, "months": mo, "days": (today - birth).days, "next_in": (nxt - today).days}


def bmi_info(w, h_cm):
    if not (20 <= w <= 400 and 90 <= h_cm <= 250):
        raise ValueError("وزن ۲۰ تا ۴۰۰ کیلو و قد ۹۰ تا ۲۵۰ سانتی‌متر")
    b = w / ((h_cm / 100) ** 2)
    cat = "کمبود وزن" if b < 18.5 else "نرمال" if b < 25 else "اضافه وزن" if b < 30 else "چاقی"
    lo, hi = 18.5 * (h_cm / 100) ** 2, 24.9 * (h_cm / 100) ** 2
    return b, cat, lo, hi


# ---------------------------------------------------------------- reminders
def parse_delay(s):
    s = fa_digits(s.strip().lower())
    units = {"s": 1, "ث": 1, "m": 60, "د": 60, "h": 3600, "س": 3600, "d": 86400, "ر": 86400}
    parts = re.findall(r"(\d+(?:\.\d+)?)\s*([smhdثدسر])", s)
    if not parts or "".join(a + b for a, b in re.findall(r"(\d+(?:\.\d+)?)\s*([smhdثدسر])", s)).replace(" ", "") != s.replace(" ", ""):
        raise ValueError("زمان مثل 30s ، 10m ، 2h ، 1d یا ترکیبی 1h30m (ث/د/س/ر هم می‌شود)")
    total = sum(float(n) * units[u] for n, u in parts)
    if not 5 <= total <= 90 * 86400:
        raise ValueError("بین ۵ ثانیه تا ۹۰ روز")
    return total


def human_delta(sec):
    sec = int(sec)
    d, r = divmod(sec, 86400); h, r = divmod(r, 3600); m, s = divmod(r, 60)
    return " و ".join(x for x in ("%d روز" % d if d else "", "%d ساعت" % h if h else "", "%d دقیقه" % m if m else "", "%d ثانیه" % s if s and not d and not h else "") if x) or "چند لحظه"


# ---------------------------------------------------------------- wiki
async def wiki_summary(session, q):
    import aiohttp
    for lang in ("fa", "en"):
        base = "https://%s.wikipedia.org/w/api.php" % lang
        async with session.get(base, params={"action": "query", "list": "search", "srsearch": q, "srlimit": 1, "format": "json"},
                               timeout=aiohttp.ClientTimeout(total=10)) as r:
            res = (await r.json(content_type=None))["query"]["search"]
        if not res:
            continue
        async with session.get(base, params={"action": "query", "prop": "extracts|info", "exintro": 1, "explaintext": 1,
                                             "titles": res[0]["title"], "format": "json", "inprop": "url"},
                               timeout=aiohttp.ClientTimeout(total=10)) as r:
            page = next(iter((await r.json(content_type=None))["query"]["pages"].values()))
        return "%s\n%s\n%s" % (page.get("title", ""), (page.get("extract", "") or "")[:1800], page.get("fullurl", ""))
    return "چیزی پیدا نشد."
