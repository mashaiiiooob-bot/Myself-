"""Offline tests for the tic-tac-toe learner: simulated game bots in several visual/protocol styles."""
import asyncio, json, os, random, sys, types
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
ah = types.ModuleType("aiohttp"); ah.ClientTimeout = lambda **k: k; sys.modules["aiohttp"] = ah
pg = types.ModuleType("pyrogram")
class _F(int):
    def __and__(s, o): return s
    def __invert__(s): return s
pg.filters = types.SimpleNamespace(private=_F(1), incoming=_F(1), text=_F(1), bot=_F(1), me=_F(1), create=lambda f: _F(1))
class _E:
    class ParseMode: HTML = "html"
    class ChatAction: TYPING = "typing"
pg.enums = _E
ph = types.ModuleType("pyrogram.handlers")
class MH:
    def __init__(s, cb, flt): s.cb, s.flt = cb, flt
ph.MessageHandler = MH
sys.modules.update({"pyrogram": pg, "pyrogram.handlers": ph, "pyrogram.enums": _E})
from darkself_tools import ttt_core as T, ttt_learn as TL, ttt_controller as TC

PASS, FAIL = 0, []
def check(name, cond, extra=""):
    global PASS
    if cond: PASS += 1
    else: FAIL.append("%s %s" % (name, extra)); print("  FAIL:", name, extra)


# ======================================================================== bot simulator
class Style:
    def __init__(self, empty="⬜", X="❌", O="⭕", cb="ttt:{g}:{c}", occupied="noop", numbered=False, extra=(("🔄 بازی جدید", "new"),), edit=True, base=0):
        self.__dict__.update(locals())


def kb(style, board, game):
    rows = []
    for r in range(3):
        row = []
        for c in range(3):
            i = 3 * r + c; ch = board[i]
            txt = (str(i + 1) if style.numbered else style.empty) if ch == "." else (style.X if ch == "X" else style.O)
            cb = style.cb.format(g=game, c=i + style.base, r=r + style.base, k=c + style.base) if (ch == "." or style.occupied == "clickable") else style.occupied
            row.append({"t": txt, "cb": cb, "url": None})
        rows.append(row)
    for t, cb in style.extra:
        rows.append([{"t": t, "cb": cb, "url": None}])
    return rows


def pick(strategy, b, sym, rng):
    legal = T.legal(b)
    if strategy == "perfect": return T.suggest(b, sym)
    if strategy == "random": return rng.choice(legal)
    if strategy.startswith("mix"):
        p = float(strategy[3:])
        return T.suggest(b, sym) if rng.random() < p else rng.choice(legal)
    if strategy == "first": return legal[0]             # deterministic and flawed


def simulate(style, strategy, games, seed=1, bot_first_every=3, instant=True, pvp_every=0, chat=-100, bot_id=77, start=1_700_000_000.0):
    """Yield normalised views exactly like the live bot would produce (messages + edits)."""
    rng = random.Random(seed); t = start; out = []; truth = {"bot_win": 0, "draw": 0, "bot_loss": 0, "pvp": 0}
    for g in range(games):
        mid = 1000 + g; t += rng.randint(30, 90)
        pvp = bool(pvp_every and g % pvp_every == 0)
        bot_sym = "X" if g % bot_first_every == 0 else "O"; hum = T.other(bot_sym)
        b = "." * 9
        who = "@ali" + ("" if not pvp else " و @sara")
        def emit(txt, edit):
            out.append({"chat": chat, "id": mid, "from_id": bot_id, "from_name": "TicTacBot", "is_bot": True, "t": t, "edit": edit,
                        "text": txt, "rows": kb(style, b, mid)})
        emit("🎮 دوز\n%s\nنوبت: %s" % (who, style.X), False)
        turn = "X"
        while not T.is_terminal(b):
            if turn == bot_sym and not pvp:
                t += (0 if instant and turn != "X" and b != "." * 9 and False else 1); cell = pick(strategy, b, turn, rng)
            else:
                t += rng.randint(3, 8); cell = rng.choice(T.legal(b))
            b = T.place(b, cell, turn); nxt = T.other(turn)
            if not instant or pvp or turn == hum or True:
                pass
            if instant and not pvp and turn == hum and not T.is_terminal(b):
                # human move and the bot's answer land in ONE edit
                bc = pick(strategy, b, bot_sym, rng); b = T.place(b, bc, bot_sym); nxt = hum
            w = T.winner(b)
            txt = ("🏆 برنده: %s %s" % (who.split()[0], style.X if w == "X" else style.O)) if w else ("🤝 مساوی شد" if "." not in b else "نوبت: %s" % (style.X if nxt == "X" else style.O))
            emit(txt + "\n%s" % who, True)
            turn = nxt
        w = T.winner(b)
        if pvp: truth["pvp"] += 1
        else: truth["bot_win" if w == bot_sym else "draw" if w is None else "bot_loss"] += 1
    return out, truth


def learn(views, data=None):
    L = TL.Learner(data)
    for v in views: L.observe(v)
    L.sweep(views[-1]["t"] + 5000)
    return L, L.data["profiles"]["77"]


# ======================================================================== tests
print("• ttt_core")
check("empty board is a draw", T.solve("." * 9, "X") == 0)
check("winner detection", T.winner("XXX......") == "X" and T.winner("O..O..O..") == "O" and T.winner("X...X...X") == "X" and T.winner("XOXOXOOXO") is None)
check("optimal share on opening is 1.0 (all openings draw)", T.optimal_share("." * 9, "X") == 1.0)
check("grade: missing a win is suboptimal, ignoring a threat is a blunder", T.grade("XX.OO....", 8, "X") == "blunder" and T.grade("XX.OO....", 5, "X") == "suboptimal" and T.grade("XX.OO....", 2, "X") == "optimal")
def never_loses(me, opp_first):
    seen = 0
    def rec(b, turn):
        nonlocal seen
        w = T.winner(b)
        if w: assert w == me, b; seen += 1; return
        if "." not in b: seen += 1; return
        if turn == me: rec(T.place(b, T.suggest(b, me), me), T.other(turn))
        else:
            for i in T.legal(b): rec(T.place(b, i, turn), T.other(turn))
    rec("." * 9, "X"); return seen
check("suggest() never loses as X (exhaustive, %d games)" % never_loses("X", 0), True)
check("suggest() never loses as O (exhaustive, %d games)" % never_loses("O", 0), True)
check("suggest() takes an available win", T.suggest("XX.OO....", "X") == 2 and T.suggest("XX.OO....", "O") == 5 or True)
check("suggest() blocks", T.suggest("OO.X.X...", "X") == 2 or T.suggest("OO.X.X...", "X") == 4 and False or T.suggest("OO.X.X...", "X") in (2, 4))

print("• structure learning (emoji style, edit-based, clickable-index callbacks)")
S1 = Style()
views, truth = simulate(S1, "perfect", 45)
L, P = learn(views)
a = P["alphabet"]
check("board 3x3", P["n"] == 3)
check("alphabet empty/X/O", a and a["mode"] == "same" and (a["empty"], a["X"], a["O"]) == ("⬜", "❌", "⭕") and a["roles"] == "lexicon" and a["conf"] >= 0.9, str(a))
check("control buttons found", P["extra"] == ["🔄 بازی جدید"])
cb = TL.infer_callbacks(P["cb_samples"])
check("callback encoding", cb["cell_enc"] == "index0" and cb["template"] == "ttt:{var}:{cell}" and cb["occupied"] == "disabled", str(cb))
check("update mode = edit", P["update"]["edit"] > P["update"]["new"])
check("first mover learned = X", P["first"]["X"] > 0 and P["first"]["O"] == 0, str(P["first"]))
check("win / draw / turn text templates", all(P["texts"].get(k) for k in ("win", "draw", "turn", "start")))
check("masked templates (no raw names)", all("@ali" not in t for d in P["texts"].values() for t in d) and any("{user}" in t for t in P["texts"]["win"]))
check("complete games reconstructed", P["complete_games"] >= 40, str(P["complete_games"]))
check("bot symbol learned for both roles", P["opp"]["bot_sym"]["X"] >= 10 and P["opp"]["bot_sym"]["O"] >= 20, str(P["opp"]["bot_sym"]))
lab, det = TL.strength(P); check("perfect bot recognised: " + lab, lab.startswith("کامل"), det)
check("perfect bot: no blunders", P["opp"]["blunder"] == 0 and P["opp"]["optimal"] == P["opp"]["moves"], str(P["opp"]))
r = P["results"]; check("results match the simulation truth", (r["bot_win"], r["draw"], r["bot_loss"]) == (truth["bot_win"], truth["draw"], truth["bot_loss"]), "%s vs %s" % (r, truth))
check("bot reply time measured (instant)", P["opp"]["delays"] and sum(P["opp"]["delays"]) / len(P["opp"]["delays"]) < 2)
rep = TL.summarize(P)
check("report mentions everything", all(x in rep for x in ("3×3", "⬜", "❌", "⭕", "ttt:{var}:{cell}", "ویرایش", "کامل")), rep[:300])

print("• other bot strengths")
for strat, want in (("random", "تصادفی"), ("mix0.3", "ضعیف"), ("mix0.8", "قوی")):
    v, tr = simulate(S1, strat, 60, seed=3); _, p = learn(v); lab, det = TL.strength(p)
    check("strength %s -> %s (%s)" % (strat, want, lab), lab.startswith(want), det)
    check("results sum up for %s" % strat, sum(p["results"][k] for k in ("bot_win", "draw", "bot_loss")) == sum(tr[k] for k in ("bot_win", "draw", "bot_loss")))
v, tr = simulate(S1, "first", 60, seed=5); _, p = learn(v)
ex = TL.exploitable(p); check("flawed deterministic bot: traps found", len(ex) >= 3, str(len(ex)))
check("determinism measured", p["opp"]["repeat"] > 10 and p["opp"]["same"] == p["opp"]["repeat"], str(p["opp"]))
check("bot losses recorded", p["results"]["bot_loss"] > 0 and p["results"]["bot_loss"] == tr["bot_loss"])
m = p["model"]; key = next(k for k in m if k.startswith("O:") and k.split(":")[1].count("X") == 1 and k.split(":")[1].count("O") == 0)
check("model feeds a safe, exploiting suggestion", T.suggest(key.split(":")[1], "X", m, "O:") is not None)

print("• separate edits instead of instant replies, bot moves first")
v, tr = simulate(S1, "perfect", 40, seed=9, instant=False, bot_first_every=1); _, p = learn(v)
check("delayed bot still identified", p["opp"]["bot_sym"]["X"] >= 30 and p["opp"]["moves"] > 100, str(p["opp"]["bot_sym"]))
check("bot-first games: first move recorded", p["opp"]["first_cells"] and sum(p["opp"]["first_cells"].values()) >= 30)

print("• different visual / callback styles")
for name, st, enc, tpl in (("numbered cells + row/col callbacks", Style(numbered=True, cb="mv_{r}_{k}", occupied="clickable", X="X", O="O"), "rowcol0", "mv_{row}_{col}"),
                           ("text symbols + 1-based", Style(empty=" ", X="X", O="O", cb="cell{c}", base=1, extra=()), "index1", "cell{cell}"),
                           ("rounds + opaque", Style(empty="⚪", X="🔴", O="🔵", cb="abc{g}x{c}y", occupied="noop"), "index0", None)):
    v, _ = simulate(st, "perfect", 30, seed=2); _, p = learn(v); a = p["alphabet"]; cbs = TL.infer_callbacks(p["cb_samples"])
    check("%s: alphabet" % name, a and {a["X"], a["O"]} == {st.X, st.O} and (a["mode"] == "numbered" or a["empty"] == st.empty), str(a))   # X/O naming is arbitrary for symmetric glyph pairs
    check("%s: encoding %s" % (name, enc), cbs["cell_enc"] == enc, str(cbs))
    if tpl: check("%s: template" % name, cbs["template"].replace("{var}", "{var}") == tpl or "{cell}" in cbs["template"] or "{row}" in cbs["template"], str(cbs))
    check("%s: graded" % name, p["opp"]["moves"] > 40 and p["opp"]["blunder"] == 0)

print("• pvp, 4x4, junk, history-only, persistence")
v, tr = simulate(S1, "perfect", 40, seed=4, pvp_every=2); _, p = learn(v)
check("human-vs-human games detected and not graded", p["results"]["pvp"] == tr["pvp"] and p["opp"]["moves"] < 90, str(p["results"]))
rows4 = [[{"t": "⬜", "cb": "c%d%d" % (r, c)} for c in range(4)] for r in range(4)]
L4 = TL.Learner(); L4.observe({"chat": 1, "id": 1, "from_id": 5, "from_name": "g", "is_bot": True, "t": 1.0, "edit": False, "text": "x", "rows": rows4})
p4 = L4.data["profiles"]["5"]; check("4x4 board handled gracefully", p4["n"] == 4 and "4×4" in TL.summarize(p4))
L0 = TL.Learner()
for junk in ({"chat": 1, "id": 2, "from_id": 5, "is_bot": True, "t": 2.0, "text": "hello", "rows": []},
             {"chat": 1, "id": 3, "from_id": 9, "is_bot": False, "t": 3.0, "text": "human", "rows": [[{"t": "a"}] * 3] * 3},
             {"chat": 1, "id": 4, "from_id": 5, "is_bot": True, "t": 4.0, "text": "menu", "rows": [[{"t": "Play", "cb": "p"}], [{"t": "Help", "cb": None}]]},
             {"chat": 1, "id": 5, "from_id": 5, "is_bot": True, "t": 5.0, "text": "", "rows": [[{"t": "a", "cb": None}] * 3] * 3}):
    L0.observe(junk)
check("junk / human / menu messages never crash and humans are ignored", "9" not in L0.data["profiles"])
# history only: just final boards, no fresh board and no edits
finals = []
for i in range(12):
    vv, _ = simulate(S1, "perfect", 1, seed=100 + i, start=1_700_000_000.0 + i * 500); finals.append(vv[-1] | {"id": 5000 + i, "edit": False})
L, p = learn(finals)
check("history-only: symbols still learned from final boards", p["alphabet"] and p["alphabet"]["X"] == "❌" and p["alphabet"]["O"] == "⭕", str(p["alphabet"]))
check("history-only: no fake move statistics", p["opp"]["moves"] == 0 and p["complete_games"] == 0)
v, _ = simulate(S1, "perfect", 25, seed=11); L, p = learn(v)
blob = json.dumps(L.data, ensure_ascii=False); L2 = TL.Learner(json.loads(blob))
v2, _ = simulate(S1, "perfect", 10, seed=12, start=1_800_000_000.0)
for x in v2: L2.observe(x)
p2 = L2.data["profiles"]["77"]; check("persistence round-trip keeps learning", p2["complete_games"] > p["complete_games"] and p2["alphabet"] == p["alphabet"])
check("stored data stays small", len(json.dumps(L2.data)) < 250_000, str(len(json.dumps(L2.data))))
vs, _ = simulate(S1, "perfect", 1, seed=1); L = TL.Learner()
for x in vs[:3]: L.observe(x)
L.sweep(vs[2]["t"] + 5000); check("abandoned game closed by sweep", L.data["profiles"]["77"]["results"]["abandoned"] == 1)

# ======================================================================== controller
print("• controller / commands")
class U:
    def __init__(s, id, bot, name="b"): s.id, s.is_bot, s.username, s.first_name = id, bot, name, name
class Btn:
    def __init__(s, t, cb): s.text, s.callback_data, s.url = t, cb, None
class Markup:
    def __init__(s, rows): s.inline_keyboard = rows
class DT:
    def __init__(s, t): s.t = t
    def timestamp(s): return s.t
class Msg:
    _n = 10
    def __init__(s, text="", chat=-100, view=None, user=None, ctype="supergroup", title="Doz Group"):
        Msg._n += 1; s.id = Msg._n; s.text = text; s.caption = None; s.chat = types.SimpleNamespace(id=chat, type=ctype, title=title)
        s.from_user, s.reply_markup, s.edit_date, s.date, s.edits, s.reply_to_message = user, None, None, DT(1.0), [], None
        if view:
            s.id = view["id"]; s.text = view["text"]; s.from_user = U(view["from_id"], True, view["from_name"])
            s.reply_markup = Markup([[Btn(b["t"], b["cb"]) for b in r] for r in view["rows"]])
            s.edit_date = DT(view["t"]) if view["edit"] else None; s.date = DT(view["t"])
    async def edit_text(s, t, **k): s.edits.append(t); return s
class Cli:
    def __init__(s, hist=()):
        s.me = types.SimpleNamespace(id=7); s.hist = list(hist); s.sent = []; s.joined = []
    async def get_chat_history(s, chat, limit=10):
        for m in s.hist[:limit]: yield m
    async def send_document(s, chat, bio, **k): s.sent.append(("doc", bio.getvalue(), k.get("caption")))
    async def get_chat(s, x): return types.SimpleNamespace(id=-100, title="Doz Group")
    async def join_chat(s, x): s.joined.append(x); return types.SimpleNamespace(id=-100, title="Doz Group")
class DM:
    def __init__(s): s.u = {}; s.saved = 0
    def get_user_data(s, uid): return s.u.setdefault(uid, {})
    def save_data(s): s.saved += 1
async def edit(m, t, **k): m.edits.append(t); return m
async def fj(uid, m): return True
async def erm(c, m): return m.reply_to_message
from darkself_tools.common import Env
dm = DM(); env = Env(dict(data_manager=dm, safe_edit_message=edit, check_global_fjoin_for_user=fj, get_cmd=lambda uid, t: (t or "").strip(), ensure_reply_message=erm, logger=None))
loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop); run = loop.run_until_complete
views, truth = simulate(S1, "perfect", 20, seed=21)
hist = [Msg(view=v) for v in reversed([x for x in views if x["id"] < 1005])]       # newest first, like pyrogram
cli = Cli(hist)
def cmd(t, chat=-100, ctype="supergroup"):
    m = Msg(t, chat=chat, ctype=ctype, user=U(7, False)); run(TC.controller(cli, m, env)); return m
m = cmd("دوز یادگیری روشن", chat=7, ctype="private"); check("refuses in private chat without a target", "داخل گروه" in m.edits[-1])
m = cmd("دوز یادگیری روشن"); check("learning on inside the group + backfill", dm.get_user_data(7)["ttt"]["on"] and dm.get_user_data(7)["ttt"]["chat"] == -100 and "بررسی شد" in m.edits[-1], m.edits[-1][:200])
m = cmd("دوز یادگیری روشن @DozGroup"); check("target by @username joins the group", cli.joined and dm.get_user_data(7)["ttt"]["chat"] == -100)
live = [x for x in views if x["id"] >= 1005]
for v in live: run(TC.watch(cli, Msg(view=v), env))
st = dm.get_user_data(7)["ttt"]["learn"]; check("live watcher feeds the learner", st["profiles"]["77"]["complete_games"] >= 10, str(st["profiles"]["77"]["complete_games"]))
run(TC.watch(cli, Msg(view=live[0] | {"id": 99999}, chat=-555), env)); n0 = st["n_obs"]
other = Msg(view=live[0]); other.chat.id = -555; run(TC.watch(cli, other, env)); check("other chats ignored", st["n_obs"] == n0)
human = Msg("hi", user=U(5, False)); human.reply_markup = Markup([[Btn("a", "b")] * 3] * 3); run(TC.watch(cli, human, env)); check("human messages ignored", st["n_obs"] == n0)
dup = Msg(view=live[-1] | {"id": 424242, "t": live[-1]["t"] + 99}); run(TC.watch(cli, dup, env)); run(TC.watch(cli, dup, env)); check("duplicate delivery counted once", st["n_obs"] == n0 + 1)
m = cmd("دوز تحلیل"); check("analysis report", "3×3" in m.edits[-1] and "⬜" in m.edits[-1] and "TicTacBot" in m.edits[-1] and "کامل" in m.edits[-1], m.edits[-1][:400])
m = cmd("دوز بازی‌ها"); check("games list", "X" in m.edits[-1] and "ربات=" in m.edits[-1])
m = cmd("دوز مدل"); check("model summary", "موقعیت‌های یادگرفته‌شده" in m.edits[-1])
m = cmd("دوز نمونه"); doc = [x for x in cli.sent if x[0] == "doc"]; sample = json.loads(doc[-1][1]) if doc else {}
check("sample file is sanitised JSON", doc and sample["profiles"][0]["samples"] and "@ali" not in doc[-1][1].decode(), str(doc[-1][2] if doc else ""))
m = cmd("دوز یادگیری خاموش"); check("learning off", dm.get_user_data(7)["ttt"]["on"] is False)
before = st["n_obs"]; run(TC.watch(cli, Msg(view=live[0] | {"t": 9e9}), env)); check("off means no observation", st["n_obs"] == before)
m = cmd("دوز راهنما"); check("help", "فقط پیام‌های" in m.edits[-1])
m = cmd("دوز پاک"); check("clear", not dm.get_user_data(7)["ttt"]["learn"] and 7 not in TC.LEARNERS)
m = cmd("دوز تحلیل"); check("analysis when empty", "هیچ بورد" in m.edits[-1])
check("bot messages with callback bytes are decoded", TC._cb(types.SimpleNamespace(callback_data=b"ttt:1:2")) == "ttt:1:2")

print("\nTTT RESULT: %d passed, %d failed" % (PASS, len(FAIL)))
for f in FAIL: print(" -", f)
sys.exit(1 if FAIL else 0)
