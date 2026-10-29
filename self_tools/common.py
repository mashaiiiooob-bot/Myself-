"""Shared helpers. Every module talks to the bot only through `Env` (the bot's globals)."""
import asyncio, html, re, time

HEAD = "✦ <b>𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙</b> ✦  ·  {}\n━━━━━━━━━━━━━━━━━━\n"
LIMIT = 3900


class Env:
    """Thin accessor over the bot module globals (`globals()` of the bot file)."""

    def __init__(self, g):
        self.g = g

    def __getattr__(self, name):
        try:
            return self.g[name]
        except KeyError:
            raise AttributeError(name)

    def get(self, name, default=None):
        return self.g.get(name, default)

    def log(self, msg, *a):
        lg = self.g.get("logger")
        if lg:
            try:
                lg.info(msg, *a)
            except Exception:
                pass


def head(title):
    return HEAD.format(html.escape(title))


def md_to_html(text):
    """LLM markdown -> Telegram-safe HTML. Code is protected first, so tags never nest badly."""
    keep = []

    def stash(m):
        keep.append(m)
        return "\x00%d\x00" % (len(keep) - 1)

    t = re.sub(r"```(?:[\w+-]*)\n?(.*?)```", lambda m: stash(("pre", m.group(1))), text or "", flags=re.S)
    t = re.sub(r"`([^`\n]+)`", lambda m: stash(("code", m.group(1))), t)
    t = html.escape(t, quote=False)
    t = re.sub(r"^#{1,6}\s*(.+)$", r"<b>\1</b>", t, flags=re.M)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t, flags=re.S)
    t = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)

    def back(m):
        kind, body = keep[int(m.group(1))]
        body = html.escape(body.strip("\n") if kind == "pre" else body, quote=False)
        return "<%s>%s</%s>" % (kind, body, kind)

    return re.sub(r"\x00(\d+)\x00", back, t)


def chunk(text, size=LIMIT):
    """Split on paragraph/line boundaries; never inside a word if avoidable."""
    out, cur = [], ""
    for para in (text or "").split("\n"):
        while len(para) > size:
            cut = para.rfind(" ", 0, size) or size
            cut = size if cut <= 0 else cut
            if cur:
                out.append(cur); cur = ""
            out.append(para[:cut]); para = para[cut:].lstrip()
        if len(cur) + len(para) + 1 > size:
            out.append(cur); cur = para
        else:
            cur = (cur + "\n" + para) if cur else para
    if cur or not out:
        out.append(cur)
    return out


def parse_mode_html():
    try:
        from pyrogram import enums
        return enums.ParseMode.HTML
    except Exception:
        return "html"


class Streamer:
    """Progressive message editing with throttling (typing effect)."""

    def __init__(self, env, message, title="AI", min_gap=1.4, min_delta=45):
        self.env, self.message, self.title = env, message, title
        self.min_gap, self.min_delta = min_gap, min_delta
        self.text, self._last_t, self._last_len, self._lock = "", 0.0, 0, asyncio.Lock()
        self.target = message

    async def _edit(self, body, footer=""):
        txt = head(self.title) + md_to_html(body)[: LIMIT - 200] + footer
        res = await self.env.safe_edit_message(self.target, txt, parse_mode=parse_mode_html())
        if res is not None:
            self.target = res
        return res

    async def push(self, piece):
        if piece is None:                       # provider restarted: forget partial text
            self.text, self._last_len = "", 0
            return
        self.text += piece
        now = time.monotonic()
        if now - self._last_t < self.min_gap or len(self.text) - self._last_len < self.min_delta:
            return
        if self._lock.locked():
            return
        async with self._lock:
            self._last_t, self._last_len = now, len(self.text)
            await self._edit(self.text + " ▌")

    async def finish(self, body, footer=""):
        parts = chunk(body)
        await self._edit(parts[0], footer if len(parts) == 1 else "")
        for i, extra in enumerate(parts[1:], 2):
            try:
                await self.target.reply_text(md_to_html(extra) + (footer if i == len(parts) else ""),
                                             parse_mode=parse_mode_html())
            except Exception:
                pass

    async def status(self, text):
        await self.env.safe_edit_message(self.target, head(self.title) + html.escape(text),
                                         parse_mode=parse_mode_html())


def fa_digits(s):
    return str(s).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))


def raw_out(env, uid, chat_id, text):
    """Tell the bot's outgoing-message modifier (bold / spoiler / auto-translate...) to leave the next message to
    this chat alone — used for text that must stay exactly as written (game commands, assistant replies)."""
    d = env.get("DS_RAW_OUT")
    if d is None:
        return
    plain = re.sub(r"[*_`~|\[\]]", "", text or "").strip()
    d[(uid, chat_id)] = (time.time() + 20, plain[:10])
