from pyrogram import filters
from pyrogram.handlers import MessageHandler

_UP, _LO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"
_SC = dict(zip(_LO, "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"))


def _math(up, lo, dg, exc=None):
    m = {}
    for i, c in enumerate(_UP):
        m[c] = chr(up + i) if up else c
    for i, c in enumerate(_LO):
        m[c] = chr(lo + i) if lo else c
    for i, c in enumerate("0123456789"):
        if dg:
            m[c] = chr(dg + i)
    m.update(exc or {})
    return m


_STYLES = [
    ("bold", _math(0x1D400, 0x1D41A, 0x1D7CE)),
    ("italic", _math(0x1D434, 0x1D44E, 0, {"h": "ℎ"})),
    ("bold italic", _math(0x1D468, 0x1D482, 0x1D7CE)),
    ("script", _math(0x1D49C, 0x1D4B6, 0, {"B": "ℬ", "E": "ℰ", "F": "ℱ", "H": "ℋ", "I": "ℐ", "L": "ℒ", "M": "ℳ", "R": "ℛ", "e": "ℯ", "g": "ℊ", "o": "ℴ"})),
    ("double-struck", _math(0x1D538, 0x1D552, 0x1D7D8, {"C": "ℂ", "H": "ℍ", "N": "ℕ", "P": "ℙ", "Q": "ℚ", "R": "ℝ", "Z": "ℤ"})),
    ("monospace", _math(0x1D670, 0x1D68A, 0x1D7F6)),
    ("sans bold", _math(0x1D5D4, 0x1D5EE, 0x1D7EC)),
    ("fullwidth", {**{c: chr(0xFF21 + i) for i, c in enumerate(_UP)}, **{c: chr(0xFF41 + i) for i, c in enumerate(_LO)}, **{c: chr(0xFF10 + i) for i, c in enumerate("0123456789")}}),
    ("circled", {**{c: chr(0x24B6 + i) for i, c in enumerate(_UP)}, **{c: chr(0x24D0 + i) for i, c in enumerate(_LO)}}),
    ("small caps", dict(_SC)),
]


def convert(text, idx):
    m = _STYLES[idx][1]
    return "".join(m.get(c, c) for c in text)


async def handler(client, message):
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""
    num = None
    if arg:
        first, _, rest = arg.partition(" ")
        if first.isdigit() and rest.strip():
            num, arg = int(first), rest.strip()
    if not arg and message.reply_to_message:
        arg = (message.reply_to_message.text or message.reply_to_message.caption or "").strip()
    if not arg:
        return await message.reply_text("**فرمت:** `/font متن` یا `/font 3 متن`\n(فقط حروف انگلیسی و اعداد تبدیل می‌شوند)")
    arg = arg[:200]
    if num is not None:
        if not 1 <= num <= len(_STYLES):
            return await message.reply_text(f"❌ شماره‌ی استایل بین 1 تا {len(_STYLES)} است.")
        return await message.reply_text(convert(arg, num - 1))
    lines = [f"🔤 **{i + 1}.** {convert(arg, i)}" for i in range(len(_STYLES))]
    await message.reply_text("\n".join(lines) + "\n\nبرای یک استایل: `/font 3 متن`")


def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command("font", prefixes=["/", "."])), group=0)
