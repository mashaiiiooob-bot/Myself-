"""Learns how a tic-tac-toe *bot* behaves, only by watching its messages in a chat.

Input  : normalised message views (see `view_of` in ttt_controller) – only bot messages with inline keyboards matter.
Learns : board geometry · cell symbols · who moves first · callback_data encoding · how the board is updated ·
         turn / win / draw message templates · the bot's speed, determinism and playing strength (graded by an
         exact solver) · an opponent model (position -> bot reply) that a future player can exploit.
It never clicks anything and never sends messages; playing is a separate, later step."""
import re, statistics, time
from collections import Counter
from . import ttt_core as T

X_GLYPHS = {"❌", "✖️", "✖", "X", "x", "✗", "❎", "✘", "×"}
O_GLYPHS = {"⭕", "⭕️", "O", "o", "🔴", "⚪", "🅾", "🅾️", "○", "◯", "0", "🔵"}
MAX_RECENT, MAX_MODEL, MAX_GAMES, STALE = 120, 1500, 40, 900
LEX = {"win": r"برنده|برد|win|won|winner|🏆|🎉|پیروز", "draw": r"مساوی|تساوی|draw|tie|\bdraw\b",
       "turn": r"نوبت|turn|move|حرکت", "start": r"شروع|start|new game|بازی جدید",
       "timeout": r"زمان|timeout|expired|منقضی|time's up"}
BOT_WORDS = re.compile(r"ربات|bot|computer|کامپیوتر|🤖|\bai\b", re.I)


# ----------------------------------------------------------------------------- board extraction
def find_board(rows):
    """-> {'n', 'cells': [(text, cb)] row-major, 'extra': [texts]} or None. Square block of n×n buttons, n=3..5."""
    for n in (3, 4, 5):
        for r0 in range(0, len(rows) - n + 1):
            blk = rows[r0:r0 + n]
            if all(len(r) == n for r in blk):
                cells = [(b["t"], b.get("cb")) for r in blk for b in r]
                extra = [b["t"] for i, r in enumerate(rows) if not (r0 <= i < r0 + n) for b in r]
                return {"n": n, "cells": cells, "extra": extra}
    return None


def mask(text, alph=None):
    t = re.sub(r"https?://\S+", "{url}", text or "")
    t = re.sub(r"@\w{3,}", "{user}", t)
    t = re.sub(r"\d+", "{n}", t)
    for g in set(filter(None, [(alph or {}).get("X"), (alph or {}).get("O")])):
        t = t.replace(g, "{" + ("X" if g == (alph or {}).get("X") else "O") + "}")
    t = re.sub(r"[ \t]+", " ", t).strip()
    return " ⏎ ".join(l.strip() for l in t.split("\n") if l.strip())[:170]


# ----------------------------------------------------------------------------- alphabet
def infer_alphabet(boards):
    """boards: list of 9-tuples of cell texts. -> {'mode','empty','X','O','roles','conf'} (values may be None)."""
    out = {"mode": None, "empty": None, "X": None, "O": None, "roles": None, "conf": 0.0}
    if not boards:
        return out
    boards = [b for b in boards if len(b) == 9]
    if not boards:
        return out
    # numbered empty cells: every cell shows its own position (1..9 or 0..8)
    for base in (1, 0):
        lab = tuple(str(i + base) for i in range(9))
        hits = sum(1 for b in boards if sum(1 for i, x in enumerate(b) if x == lab[i]) >= 4)
        if hits >= 1:
            marks = Counter(x for b in boards for i, x in enumerate(b) if x != lab[i])
            ms = [m for m, _ in marks.most_common(2)]
            out.update(mode="numbered", empty=base, conf=0.8)
            _assign_roles(out, ms, boards)
            return out
    total = Counter(x for b in boards for x in b)
    distinct = [t for t, _ in total.most_common(4)]
    fresh = [b[0] for b in boards if len(set(b)) == 1]
    e = Counter(fresh).most_common(1)[0][0] if fresh else None
    if e is None and len(distinct) == 3:
        best, best_ok = None, -1
        for cand in distinct:
            a, c = [t for t in distinct if t != cand]
            ok = sum(1 for b in boards if abs(b.count(a) - b.count(c)) <= 1)
            if ok > best_ok or (ok == best_ok and total[cand] > total[best]):
                best, best_ok = cand, ok
        if best_ok == len(boards):
            e = best
            out["conf"] = 0.6
    if e is None:
        return out
    out.update(mode="same", empty=e, conf=max(out["conf"], 0.9 if fresh else 0.6))
    _assign_roles(out, [t for t in distinct if t != e][:2], boards)
    return out


def _assign_roles(out, syms, boards):
    xs = [s for s in syms if s in X_GLYPHS]
    os_ = [s for s in syms if s in O_GLYPHS]
    if xs and os_:
        out.update(X=xs[0], O=os_[0], roles="lexicon")
    elif len(syms) == 2 and (xs or os_):
        known = xs[0] if xs else os_[0]
        rest = [s for s in syms if s != known][0]
        out.update(X=known if xs else rest, O=rest if xs else known, roles="lexicon")
    elif len(syms) == 2:
        out.update(X=syms[0], O=syms[1], roles="guess")
    elif len(syms) == 1:
        s = syms[0]
        out.update(X=s if s not in O_GLYPHS else None, O=s if s in O_GLYPHS else None, roles="partial")
        if out["X"] is None and out["O"] is None:
            out["X"] = s


def to_state(texts, alph):
    """9 cell texts -> 'XO.' string, or None when the alphabet does not explain every cell."""
    if not alph or not alph.get("mode") or len(texts) != 9:
        return None
    out = []
    for i, t in enumerate(texts):
        if alph["mode"] == "numbered" and t == str(i + alph["empty"]) or alph["mode"] == "same" and t == alph["empty"]:
            out.append(".")
        elif t == alph.get("X"):
            out.append("X")
        elif t == alph.get("O"):
            out.append("O")
        else:
            return None
    return "".join(out)


# ----------------------------------------------------------------------------- callback encoding
def infer_callbacks(samples):
    """samples: [{'cbs': [9 strings], 'state': '..X..O...'}]. -> {'template', 'cell_enc', 'occupied'}"""
    res = {"template": None, "cell_enc": None, "occupied": "unknown"}
    pieces = lambda s: re.findall(r"\d+|\D+", s)
    good = [s for s in samples if s.get("cbs") and all(isinstance(c, str) and c for c in s["cbs"]) and len(s["cbs"]) == 9]
    if not good:
        return res
    ref = next((s for s in good if s.get("state") == "." * 9), good[0])
    toks = [pieces(c) for c in ref["cbs"]]
    if len({len(t) for t in toks}) != 1:
        return res
    L = len(toks[0])
    cell_tokens, enc = [], None
    for k in range(L):
        vals = [t[k] for t in toks]
        if all(v.isdigit() for v in vals) and len(set(vals)) > 1:
            cell_tokens.append(k)
    numeric = {k: [int(toks[i][k]) for i in range(9)] for k in cell_tokens}
    for k, vals in numeric.items():
        for off, name in ((0, "index0"), (1, "index1")):
            if vals == [i + off for i in range(9)]:
                enc = (name, [k])
    if enc is None:
        rows_, cols_ = [(i // 3) for i in range(9)], [(i % 3) for i in range(9)]
        for k1, v1 in numeric.items():
            for k2, v2 in numeric.items():
                for off, name in ((0, "rowcol0"), (1, "rowcol1")):
                    if k1 != k2 and v1 == [r + off for r in rows_] and v2 == [c + off for c in cols_]:
                        enc = (name, [k1, k2])
    if enc is None:
        res["cell_enc"] = "opaque"
        return res
    res["cell_enc"] = enc[0]
    other_vary = set()
    for k in range(L):
        if k in enc[1]:
            continue
        seen = {pieces(c)[k] for s in good for c in s["cbs"] if len(pieces(c)) == L}
        if len(seen) > 1:
            other_vary.add(k)
    names = ["{cell}"] if len(enc[1]) == 1 else ["{row}", "{col}"]
    tpl = []
    for k, p in enumerate(toks[0]):
        tpl.append(names[enc[1].index(k)] if k in enc[1] else "{var}" if k in other_vary else p)
    res["template"] = "".join(tpl)
    # are occupied cells still clickable (same callback as when empty) or replaced by a dummy?
    def same_shape(i, cb):
        t = pieces(cb)
        if len(t) != L:
            return False
        for k in range(L):
            if k in enc[1]:
                if t[k] != toks[i][k]:
                    return False
            elif k not in other_vary and t[k] != toks[0][k]:
                return False
        return True
    same = diff = 0
    for s in good:
        st = s.get("state")
        if not st or st == "." * 9:
            continue
        for i, ch in enumerate(st):
            if ch != ".":
                if same_shape(i, s["cbs"][i]):
                    same += 1
                else:
                    diff += 1
    res["occupied"] = "clickable" if same and not diff else "disabled" if diff and not same else "mixed" if same and diff else "unknown"
    return res


# ----------------------------------------------------------------------------- the learner
def new_profile(bot_id, name):
    return {"id": bot_id, "name": name, "n": 3, "alphabet": None, "first": {"X": 0, "O": 0}, "extra": [], "recent": [],
            "cb_samples": [], "texts": {}, "update": {"edit": 0, "new": 0}, "samples": [],
            "opp": {"moves": 0, "optimal": 0, "blunder": 0, "suboptimal": 0, "base_sum": 0.0, "var_sum": 0.0, "first_cells": {},
                    "repeat": 0, "same": 0, "delays": [], "bot_sym": {"X": 0, "O": 0}},
            "results": {"bot_win": 0, "draw": 0, "bot_loss": 0, "pvp": 0, "unknown": 0, "abandoned": 0},
            "model": {}, "games_seen": 0, "boards_seen": 0, "complete_games": 0, "last_terminal": 0}


class Learner:
    def __init__(self, data=None):
        self.data = data if data is not None else {}          # keep the caller's dict: it is what gets persisted
        self.data.setdefault("profiles", {}); self.data.setdefault("games", []); self.data.setdefault("n_obs", 0)
        self.tracks = {}
        self.events = []

    # -------- public
    def profile(self, bot_id, name=""):
        p = self.data["profiles"].setdefault(str(bot_id), new_profile(bot_id, name))
        if name:
            p["name"] = name
        return p

    def observe(self, v):
        """v: normalised message view. Returns a list of events (strings) for logging/tests."""
        ev = []
        self.sweep(v["t"])
        if not v.get("is_bot"):
            return ev
        prof = self.profile(v["from_id"], v.get("from_name", ""))
        b = find_board(v.get("rows") or [])
        if not b:
            self._followup(prof, v)
            return ev
        self.data["n_obs"] += 1
        prof["boards_seen"] += 1
        prof["n"] = b["n"]
        prof["extra"] = b["extra"][:6]
        texts = tuple(c[0] for c in b["cells"])
        cbs = [c[1] for c in b["cells"]]
        if b["n"] != 3:
            self._sample(prof, v, texts, cbs)
            return ev
        if not prof["recent"] or prof["recent"][-1] != list(texts):
            prof["recent"].append(list(texts)); del prof["recent"][:-MAX_RECENT]
        if prof["alphabet"] is None or prof["alphabet"].get("conf", 0) < 0.9 or prof["alphabet"].get("X") is None or prof["alphabet"].get("O") is None:
            alph = infer_alphabet([tuple(x) for x in prof["recent"]])
            if alph["mode"]:
                prof["alphabet"] = alph
        alph = prof["alphabet"]
        state = to_state(texts, alph)
        self._sample(prof, v, texts, cbs, state)
        if state is None:
            return ev
        key = (v["chat"], v["id"])
        tr = self.tracks.get(key)
        if tr is None:
            tr = self.tracks[key] = {"bot": v["from_id"], "t0": v["t"], "states": [], "moves": [], "complete": state == "." * 9,
                                      "broken": False, "last": v["t"], "text": v.get("text") or "", "done": False, "pvp": False}
            prof["games_seen"] += 1
            if v.get("edit") is False:
                prof["update"]["new"] += 1
        elif v.get("edit"):
            prof["update"]["edit"] += 1
        if tr["done"]:
            return ev
        tr["last"], tr["text"] = v["t"], v.get("text") or tr["text"]
        prev = tr["states"][-1][1] if tr["states"] else None
        if prev is not None and state != prev:
            if state == "." * 9 and prev != state:                      # board reset in the same message: new game
                self._finish(prof, tr, v["t"], "reset"); ev.append("reset")
                self.tracks[key] = tr = {"bot": v["from_id"], "t0": v["t"], "states": [], "moves": [], "complete": True,
                                          "broken": False, "last": v["t"], "text": v.get("text") or "", "done": False, "pvp": False}
                prof["games_seen"] += 1
                prev = None
            else:
                mv = self._derive(prof, prev, state, tr["states"][-1][0], v["t"], tr)
                if mv is None:
                    tr["broken"] = True
                else:
                    tr["moves"] += mv
        if prev is None or state != prev:
            tr["states"].append((v["t"], state))
        label = ("win" if T.winner(state) else "draw") if T.is_terminal(state) else ("start" if state == "." * 9 else "turn")
        self._text(prof, label, v.get("text") or "", alph)
        if T.is_terminal(state) and not tr["done"]:
            self._finish(prof, tr, v["t"], "terminal"); ev.append("finished")
        return ev

    def sweep(self, now):
        for k, tr in list(self.tracks.items()):
            if tr["done"] and now - tr["last"] > 600:
                del self.tracks[k]
            elif not tr["done"] and now - tr["last"] > STALE:
                prof = self.profile(tr["bot"])
                self._finish(prof, tr, now, "stale")
                self.tracks.pop(k, None)

    # -------- internals
    def _sample(self, prof, v, texts, cbs, state=None):
        s = {"texts": list(texts), "cbs": cbs, "state": state, "text": mask(v.get("text") or "", prof["alphabet"]), "edit": bool(v.get("edit")),
             "extra": prof["extra"]}
        prof["samples"] = (prof["samples"] + [s])[-3:]
        if all(isinstance(c, str) and c for c in cbs):
            prof["cb_samples"] = [x for x in prof["cb_samples"] if x["cbs"] != cbs][-11:] + [{"cbs": cbs, "state": state}]

    def _text(self, prof, label, text, alph):
        if not text.strip():
            return
        tpl = mask(text, alph)
        d = prof["texts"].setdefault(label, {})
        d[tpl] = d.get(tpl, 0) + 1
        if len(d) > 12:
            for k in sorted(d, key=d.get)[:len(d) - 12]:
                d.pop(k)

    def _followup(self, prof, v):
        txt = (v.get("text") or "").strip()
        if txt and prof["last_terminal"] and 0 <= v["t"] - prof["last_terminal"] <= 10:
            self._text(prof, "followup", txt, prof["alphabet"])

    def _first(self, prof):
        f = prof["first"]
        return "O" if f["O"] > f["X"] else "X"

    def _derive(self, prof, prev, new, t_prev, t_new, tr):
        if any(prev[i] != "." and prev[i] != new[i] for i in range(9)):
            return None
        marks = [(i, new[i]) for i in range(9) if prev[i] == "." and new[i] != "."]
        if not marks or len(marks) > 2:
            return None
        first = self._first(prof)
        if prev == "." * 9 and len(marks) >= 1 and tr["complete"]:
            prof["first"][marks[0][1] if len(marks) == 1 else T.to_move(prev, first) or first] += 1
            first = self._first(prof)
        mover = T.to_move(prev, first)
        if mover is None:
            return None
        if len(marks) == 1:
            i, s = marks[0]
            if s != mover:
                return None
            return [{"cell": i, "sym": s, "before": prev, "dt": max(0.0, t_new - t_prev), "instant": False}]
        (i1, s1), (i2, s2) = marks
        if s1 == s2:
            return None
        if s1 != mover:
            (i1, s1), (i2, s2) = (i2, s2), (i1, s1)
        mid = T.place(prev, i1, s1)
        return [{"cell": i1, "sym": s1, "before": prev, "dt": max(0.0, t_new - t_prev), "instant": False},
                {"cell": i2, "sym": s2, "before": mid, "dt": 0.0, "instant": True}]

    def _bot_symbol(self, moves, t0, tr):
        """The bot is the side that answers (almost) instantly; humans need seconds to think."""
        fast = {"X": [], "O": []}
        for m in moves:
            fast[m["sym"]].append(m["instant"] or m["dt"] <= 2.0)
        r = {s: (sum(f) / len(f) if f else None) for s, f in fast.items()}
        if r["X"] is not None and r["O"] is not None and abs(r["X"] - r["O"]) >= 0.5:
            return "X" if r["X"] > r["O"] else "O"
        return None

    def _finish(self, prof, tr, now, why):
        if tr["done"]:
            return
        tr["done"] = True
        last = tr["states"][-1][1] if tr["states"] else None
        w = T.winner(last) if last else None
        terminal = bool(last) and T.is_terminal(last)
        if terminal:
            prof["last_terminal"] = now
        if not terminal:
            prof["results"]["abandoned"] += 1
            return
        mentions = set(re.findall(r"@\w{3,}", tr["text"] or ""))
        pvp = len(mentions - {"@" + (prof.get("name") or "").lstrip("@")}) >= 2
        usable = tr["complete"] and not tr["broken"] and tr["moves"]
        game = {"bot": prof["id"], "t": int(now), "moves": [(m["sym"], m["cell"]) for m in tr["moves"]] if usable else None,
                "winner": w, "complete": bool(usable), "pvp": pvp, "bot_sym": None}
        if usable:
            prof["complete_games"] += 1
        bot = None
        if pvp:
            prof["results"]["pvp"] += 1
        elif usable:
            bot = self._bot_symbol(tr["moves"], tr["t0"], tr)
            if bot:
                prof["opp"]["bot_sym"][bot] += 1
                game["bot_sym"] = bot
                prof["results"]["bot_win" if w == bot else "draw" if w is None else "bot_loss"] += 1
                self._grade(prof, tr["moves"], bot)
            else:
                prof["results"]["unknown"] += 1
        else:
            prof["results"]["unknown"] += 1
        g = self.data["games"]
        g.append(game); del g[:-MAX_GAMES]

    def _grade(self, prof, moves, bot):
        o = prof["opp"]
        for m in moves:
            if m["sym"] != bot:
                continue
            b, c = m["before"], m["cell"]
            gr = T.grade(b, c, bot)
            o["moves"] += 1
            o["optimal" if gr == "optimal" else "blunder" if gr == "blunder" else "suboptimal"] += 1
            p = T.optimal_share(b, bot)
            o["base_sum"] += p; o["var_sum"] += p * (1 - p)
            if b == "." * 9:
                o["first_cells"][str(c)] = o["first_cells"].get(str(c), 0) + 1
            key = "%s:%s" % (bot, b)
            row = prof["model"].get(key)
            if row:
                o["repeat"] += 1
                if max(row, key=row.get) == str(c):
                    o["same"] += 1
            prof["model"].setdefault(key, {})
            prof["model"][key][str(c)] = prof["model"][key].get(str(c), 0) + 1
            if not m["instant"]:
                o["delays"] = (o["delays"] + [round(m["dt"], 1)])[-200:]
            else:
                o["delays"] = (o["delays"] + [0.0])[-200:]
        if len(prof["model"]) > MAX_MODEL:
            for k in sorted(prof["model"], key=lambda k: sum(prof["model"][k].values()))[:len(prof["model"]) - MAX_MODEL]:
                prof["model"].pop(k)


# ----------------------------------------------------------------------------- analysis / report
def strength(prof):
    """-> (label, detail) — compares the bot's optimal-move rate with a purely random player."""
    o = prof["opp"]
    n = o["moves"]
    if n < 8:
        return "نامشخص", "هنوز فقط %d حرکت ربات بررسی شده؛ حداقل ۸ حرکت (چند بازی کامل) لازم است" % n
    rate = o["optimal"] / n
    exp, var = o["base_sum"], max(o["var_sum"], 1e-9)
    z = (o["optimal"] - exp) / (var ** 0.5)
    if rate >= 0.97:
        return "کامل (تقریباً هیچ‌وقت اشتباه نمی‌کند)", "%.0f%% حرکت‌ها بهینه · بهترین نتیجهٔ ممکن برای ما مساوی است" % (rate * 100)
    if z < 1.5:
        return "تصادفی", "%.0f%% بهینه؛ شانسی (%.0f%%) تفاوتی ندارد" % (rate * 100, exp / n * 100)
    if o["blunder"] / n > 0.12:
        return "ضعیف (اشتباهات جدی)", "%.0f%% بهینه، %d اشتباه جدی در %d حرکت" % (rate * 100, o["blunder"], n)
    return "قوی ولی قابل‌شکست", "%.0f%% بهینه؛ گاهی اشتباه می‌کند" % (rate * 100)


def exploitable(prof):
    """Positions where the bot repeatedly makes the same non-optimal reply (traps a player can reuse)."""
    out = []
    for key, row in prof["model"].items():
        sym, pos = key.split(":")
        cell, cnt = max(row.items(), key=lambda kv: kv[1])
        if cnt >= 2 and T.grade(pos, int(cell), sym) != "optimal":
            out.append((key, int(cell), cnt))
    return sorted(out, key=lambda x: -x[2])


def summarize(prof):
    """Persian human-readable report for one bot profile."""
    L = ["🤖 <b>%s</b> · %d بورد دیده‌شده · %d بازی کامل" % (prof.get("name") or prof["id"], prof["boards_seen"], prof["complete_games"])]
    a = prof["alphabet"]
    if prof["n"] != 3:
        L.append("⚠️ صفحه %d×%d است؛ تحلیل قدرت فقط برای ۳×۳ انجام می‌شود." % (prof["n"], prof["n"]))
    L.append("📐 صفحه: <b>%d×%d</b>%s" % (prof["n"], prof["n"], (" · دکمه‌های کنترلی: " + "، ".join(prof["extra"])) if prof["extra"] else ""))
    if a and a.get("mode"):
        empt = ("شماره‌ی خانه (%d…)" % a["empty"]) if a["mode"] == "numbered" else "«%s»" % a["empty"]
        L.append("🔣 خانهٔ خالی: %s · X: «%s» · O: «%s» (%s، اطمینان %.0f%%)" % (empt, a.get("X"), a.get("O"), a.get("roles") or "?", a["conf"] * 100))
    else:
        L.append("🔣 نمادها هنوز مشخص نشده‌اند (یک بازی تازه یا چند بورد دیگر لازم است)")
    f = prof["first"]
    if f["X"] + f["O"]:
        L.append("🥇 شروع‌کننده: %s (%d بازی)" % (("X" if f["X"] >= f["O"] else "O"), f["X"] + f["O"]))
    cb = infer_callbacks(prof["cb_samples"])
    if cb["cell_enc"]:
        L.append("🔗 callback: <code>%s</code> · کدگذاری خانه: %s · خانهٔ پرشده: %s" % (cb["template"] or "—", cb["cell_enc"], cb["occupied"]))
    u = prof["update"]
    if u["edit"] + u["new"]:
        L.append("♻️ به‌روزرسانی بورد: %s" % ("ویرایش همان پیام" if u["edit"] >= u["new"] else "ارسال پیام جدید"))
    t = prof["texts"]
    for label, fa in (("start", "شروع"), ("turn", "نوبت"), ("win", "برد"), ("draw", "مساوی"), ("followup", "پیام بعد از بازی")):
        if t.get(label):
            tpl = max(t[label], key=t[label].get)
            L.append("💬 %s: <code>%s</code>" % (fa, tpl.replace("<", "&lt;")))
    o, r = prof["opp"], prof["results"]
    lab, det = strength(prof)
    L.append("🧠 قدرت ربات: <b>%s</b>\n   %s" % (lab, det))
    if o["moves"]:
        dl = [d for d in o["delays"]]
        L.append("⏱ تأخیر پاسخ ربات: میانه %.1f ثانیه" % statistics.median(dl) if dl else "")
        if o["repeat"]:
            L.append("🔁 تکرارپذیری: در %d موقعیت تکراری، %d بار همان جواب را داد (%.0f%%)" % (o["repeat"], o["same"], o["same"] / o["repeat"] * 100))
        if o["first_cells"]:
            L.append("🎯 اولین حرکت ربات: " + "، ".join("خانه %d (%d)" % (int(c) + 1, n) for c, n in sorted(o["first_cells"].items(), key=lambda kv: -kv[1])[:3]))
    L.append("🏁 نتایج: ربات برد %d · مساوی %d · ربات باخت %d · آدم‌ با آدم %d · نامشخص %d" % (r["bot_win"], r["draw"], r["bot_loss"], r["pvp"], r["unknown"]))
    ex = exploitable(prof)
    if ex:
        L.append("🪤 تله‌های قابل‌استفاده: %d موقعیت که ربات همیشه اشتباه جواب می‌دهد" % len(ex))
    need = []
    if not (a and a.get("mode")): need.append("نمادها")
    if prof["complete_games"] < 5: need.append("حداقل ۵ بازی کامل از اول تا آخر")
    if o["moves"] < 20: need.append("حرکات بیشتر برای سنجش قدرت")
    if need:
        L.append("📚 برای یادگیری کامل‌تر لازم است: " + "، ".join(need))
    else:
        L.append("✅ دادهٔ کافی برای ساخت بازیکن جمع شده است.")
    return "\n".join(x for x in L if x)
