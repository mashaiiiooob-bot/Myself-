"""`دوز ...` commands: point the learner at a group, let it read the bot's board messages, show what it learned.
Only messages sent by BOTS are analysed; human messages are never stored."""
import asyncio, html, io, json, re, time
from . import ttt_learn as TL
from .common import Env, head, parse_mode_html, fa_digits

LEARNERS = {}                      # uid -> Learner (in-memory tracks, persisted profiles)
LAST_SAVE = {}
BACKFILL = 400


def _state(env, uid):
    d = env.data_manager.get_user_data(uid)
    s = d.setdefault("ttt", {})
    s.setdefault("on", False); s.setdefault("chat", None); s.setdefault("title", "")
    s.setdefault("learn", {})
    return s


def learner(env, uid):
    if uid not in LEARNERS:
        LEARNERS[uid] = TL.Learner(_state(env, uid)["learn"])
    return LEARNERS[uid]


def _save(env, uid, force=False):
    now = time.time()
    if force or now - LAST_SAVE.get(uid, 0) > 20:
        LAST_SAVE[uid] = now
        try:
            env.data_manager.save_data()
        except Exception:                                        # noqa: BLE001
            pass


def _cb(b):
    cb = getattr(b, "callback_data", None)
    if isinstance(cb, bytes):
        cb = cb.decode("utf-8", "ignore")
    return cb


def view_of(m):
    """pyrogram Message -> the plain dict the learner understands (None if it is not a bot board message)."""
    u = getattr(m, "from_user", None)
    if not u or not getattr(u, "is_bot", False):
        return None
    kb = getattr(getattr(m, "reply_markup", None), "inline_keyboard", None)
    rows = [[{"t": getattr(b, "text", "") or "", "cb": _cb(b), "url": getattr(b, "url", None)} for b in r] for r in (kb or [])]
    t = getattr(m, "edit_date", None) or getattr(m, "date", None)
    t = t.timestamp() if hasattr(t, "timestamp") else float(t or time.time())
    return {"chat": m.chat.id, "id": m.id, "from_id": u.id, "from_name": getattr(u, "username", None) or getattr(u, "first_name", "") or "",
            "is_bot": True, "t": t, "edit": bool(getattr(m, "edit_date", None)), "text": (getattr(m, "text", None) or getattr(m, "caption", None) or ""), "rows": rows}


def is_target(env, client, m):
    s = _state(env, client.me.id)
    return bool(s["on"] and s["chat"] and m.chat and m.chat.id == s["chat"])


async def watch(client, message, env):
    """Live observer (new messages + edits). Cheap: ignores everything that is not a bot keyboard in the target chat."""
    uid = client.me.id
    if not is_target(env, client, message):
        return
    v = view_of(message)
    if not v or not v["rows"]:
        return
    key = (v["chat"], v["id"], v["t"], v["text"][:40])
    seen = getattr(watch, "_seen", None)
    if seen is None:
        seen = watch._seen = {}
    if seen.get(uid) == key:                                       # same event delivered by two handlers
        return
    seen[uid] = key
    try:
        learner(env, uid).observe(v)
        _save(env, uid)
    except Exception as e:                                         # noqa: BLE001 - the observer must never disturb the client
        env.log("ttt: observe failed: %s", str(e)[:80])


async def backfill(client, env, uid, chat_id, limit=BACKFILL):
    """Read the chat history once: final boards, symbols, result texts (intermediate states are not in history)."""
    L = learner(env, uid)
    n = 0
    rows = []
    async for m in client.get_chat_history(chat_id, limit=limit):
        rows.append(m)
    for m in reversed(rows):
        v = view_of(m)
        if v and v["rows"]:
            L.observe(v); n += 1
    _save(env, uid, True)
    return n


async def resolve_chat(client, arg):
    arg = (arg or "").strip()
    link = re.match(r"^(?:https?://)?t\.me/(?:joinchat/|\+)([\w-]+)$", arg)
    try:
        if link:
            chat = await client.join_chat(arg if arg.startswith("http") else "https://" + arg)
        elif arg.startswith("@") or re.match(r"^(?:https?://)?t\.me/\w+$", arg):
            name = arg.rstrip("/").split("/")[-1].lstrip("@")
            try:
                chat = await client.get_chat(name)
            except Exception:                                      # noqa: BLE001
                chat = await client.join_chat(name)
            else:
                try:
                    await client.join_chat(name)                   # no-op when already a member
                except Exception:                                  # noqa: BLE001
                    pass
        elif re.match(r"^-?\d+$", arg):
            chat = await client.get_chat(int(arg))
        else:
            return None
        return chat
    except Exception:                                              # noqa: BLE001
        return None


async def controller(client, message, env):
    uid = client.me.id
    if not await env.check_global_fjoin_for_user(uid, message):
        return
    cmd = env.get_cmd(uid, message.text or "")
    m = re.match(r"^(?:دوز|ttt)(?:\s+(\S+))?(?:\s+(.*))?$", (cmd or "").strip(), re.S | re.I)
    if not m:
        return
    sub = (m.group(1) or "راهنما").lower()
    sub2, _, rest = (m.group(2) or "").strip().partition(" ")
    s = _state(env, uid)
    say = lambda t, **k: env.safe_edit_message(message, head("TIC-TAC-TOE") + t, parse_mode=parse_mode_html(), disable_web_page_preview=True)
    L = learner(env, uid)

    if sub in ("یادگیری", "learn"):
        act = sub2.lower()
        if act in ("روشن", "on", "شروع"):
            target = rest.strip()
            if target:
                chat = await resolve_chat(client, target)
                if not chat:
                    return await say("❌ گروه پیدا نشد یا عضو نشد. آدرس را به شکل <code>@username</code>، لینک دعوت یا آیدی عددی بده — یا داخل خود گروه فقط <code>دوز یادگیری روشن</code> بزن.")
                cid, title = chat.id, getattr(chat, "title", "") or str(chat.id)
            else:
                if getattr(message.chat, "type", None) in ("private", "bot") or str(getattr(message.chat, "type", "")).lower().endswith(("private", "bot")):
                    return await say("📌 داخل گروهِ بازی بنویس <code>دوز یادگیری روشن</code> یا آدرس گروه را بده: <code>دوز یادگیری روشن @group</code>")
                cid, title = message.chat.id, getattr(message.chat, "title", "") or str(message.chat.id)
            s.update(on=True, chat=cid, title=title)
            await say("⏳ در حال خواندن %d پیام آخر <b>%s</b>…" % (BACKFILL, html.escape(title)))
            try:
                n = await backfill(client, env, uid, cid)
            except Exception as e:                                  # noqa: BLE001
                n = 0
                env.log("ttt: backfill failed: %s", str(e)[:80])
            _save(env, uid, True)
            return await say("✅ یادگیری روشن شد: <b>%s</b>\n📥 %d پیام بورد از تاریخچه بررسی شد.\n👀 از این لحظه هر بازی‌ای که ربات اونجا انجام بدهد زنده دنبال می‌شود (فقط پیام‌های ربات‌ها).\n\nنتیجه: <code>دوز تحلیل</code> · نمونهٔ خام: <code>دوز نمونه</code>" % (html.escape(title), n))
        if act in ("خاموش", "off", "توقف"):
            s["on"] = False; _save(env, uid, True)
            return await say("⏸ یادگیری خاموش شد. داده‌ها نگه داشته شد (<code>دوز پاک</code> برای حذف).")
        return await say("<code>دوز یادگیری روشن</code> (داخل گروه) · <code>دوز یادگیری روشن @group</code> · <code>دوز یادگیری خاموش</code>")

    if sub in ("تحلیل", "analysis", "وضعیت", "status"):
        profs = [p for p in L.data["profiles"].values() if p["boards_seen"]]
        head_ = "📡 گروه: <b>%s</b> · %s · %d بورد\n\n" % (html.escape(s["title"] or "—"), "روشن" if s["on"] else "خاموش", L.data["n_obs"])
        if not profs:
            return await say(head_ + "هنوز هیچ بورد ربات‌ی دیده نشده. یک بازی در گروه شروع کنید (یا بگذارید آدم‌ها بازی کنند) و دوباره بزنید.\nشروع: <code>دوز یادگیری روشن</code>")
        return await say(head_ + "\n\n".join(TL.summarize(p) for p in profs)[:3600])

    if sub in ("نمونه", "sample"):
        profs = [p for p in L.data["profiles"].values() if p["samples"]]
        if not profs:
            return await say("نمونه‌ای نیست؛ اول یادگیری را روشن کن و یک بازی ببین.")
        data = {"profiles": [{"bot": p["name"], "n": p["n"], "alphabet": p["alphabet"], "samples": p["samples"], "texts": p["texts"],
                              "first": p["first"], "extra": p["extra"], "update": p["update"]} for p in profs], "games": L.data["games"][-10:]}
        bio = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=1).encode()); bio.name = "ttt_sample.json"
        await client.send_document(message.chat.id, bio, caption="🧪 نمونهٔ خام ساختار ربات (بدون متن پیام آدم‌ها) — برای بهبود تحلیل می‌شود برای من فرستاد")
        return await say("✓ فایل نمونه فرستاده شد")

    if sub in ("بازی‌ها", "بازیها", "games"):
        gs = [g for g in L.data["games"] if g.get("complete")][-8:]
        if not gs:
            return await say("هنوز بازی کاملی (از اول تا آخر) ثبت نشده.")
        out = []
        for g in reversed(gs):
            seq = " ".join("%s%d" % (sym, c + 1) for sym, c in g["moves"])
            res = "مساوی" if not g["winner"] else "برنده %s" % g["winner"]
            who = "ربات=%s" % g["bot_sym"] if g["bot_sym"] else ("آدم/آدم" if g["pvp"] else "ربات؟")
            out.append("• <code>%s</code>\n   %s · %s" % (seq, res, who))
        return await say("🎞 <b>آخرین بازی‌ها</b>\n" + "\n".join(out))

    if sub in ("مدل", "model"):
        profs = [p for p in L.data["profiles"].values() if p["model"]]
        if not profs:
            return await say("هنوز مدلی ساخته نشده.")
        p = profs[0]
        ex = TL.exploitable(p)[:8]
        return await say("🧬 مدل رفتاری <b>%s</b>\nموقعیت‌های یادگرفته‌شده: <b>%d</b>\n🪤 تله‌ها: <b>%d</b>%s" % (
            html.escape(p["name"] or str(p["id"])), len(p["model"]), len(TL.exploitable(p)),
            ("\n" + "\n".join("• %s → خانه %d (%d بار)" % (k, c + 1, n) for k, c, n in ex)) if ex else ""))

    if sub in ("پاک", "clear", "reset"):
        s["learn"].clear(); LEARNERS.pop(uid, None); _save(env, uid, True)
        return await say("🧹 همهٔ داده‌های یادگیری پاک شد.")

    await say("🎓 <b>یادگیری ربات دوز</b>\n\n<code>دوز یادگیری روشن</code> — داخل گروهِ بازی؛ یا <code>دوز یادگیری روشن @group</code> / لینک دعوت\n<code>دوز یادگیری خاموش</code>\n"
              "<code>دوز تحلیل</code> — ساختار صفحه، نمادها، callback، متن‌ها، سرعت و قدرت ربات\n<code>دوز بازی‌ها</code> — آخرین بازی‌های بازسازی‌شده\n<code>دوز مدل</code> — رفتار یادگرفته‌شده و تله‌ها\n"
              "<code>دوز نمونه</code> — فایل خام ساختار (برای اشکال‌یابی)\n<code>دوز پاک</code> — حذف داده‌ها\n\n"
              "فقط پیام‌های <b>ربات‌ها</b> بررسی می‌شود؛ نه پیام آدم‌ها. این بخش فقط یاد می‌گیرد و چیزی کلیک یا ارسال نمی‌کند.")


# Register tic-tac-toe learner handlers.
def register(client):
    from pyrogram import filters
    from pyrogram.handlers import MessageHandler

    env = Env(getattr(client, "g", {}) or {})

    async def command_handler(c, message):
        return await controller(c, message, env)

    async def board_watcher(c, message):
        return await watch(c, message, env)

    command_filter = (
        filters.me
        & filters.text
        & filters.regex(
            r"^(?:[/.]\s*)?(?:دوز|ttt)(?:\s|$)",
            flags=re.I,
        )
    )

    client.add_handler(
        MessageHandler(command_handler, command_filter)
    )

    client.add_handler(
        MessageHandler(board_watcher, filters.all),
        group=-99,
    )
