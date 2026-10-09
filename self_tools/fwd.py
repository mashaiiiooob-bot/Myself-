import asyncio
import time

from pyrogram import filters
from pyrogram.handlers import MessageHandler

MAX_TARGETS = 5          # per command
MAX_PER_HOUR = 20        # total forwards per hour (all commands)
DELAY = 2.0              # seconds between forwards
_LOG = []                # timestamps of recent forwards


def _quota():
    now = time.time()
    _LOG[:] = [t for t in _LOG if now - t < 3600]
    return MAX_PER_HOUR - len(_LOG)


def _parse(arg):
    out = []
    for tok in arg.replace("،", " ").split():
        tok = tok.replace("https://t.me/", "").replace("t.me/", "").lstrip("@").strip("/")
        if not tok:
            continue
        out.append(int(tok) if tok.lstrip("-").isdigit() else ("me" if tok.lower() == "me" else tok))
    return out


async def handler(client, message):
    rep = message.reply_to_message
    parts = (message.text or "").split(maxsplit=1)
    targets = _parse(parts[1]) if len(parts) > 1 else []
    if not rep or not targets:
        return await message.reply_text(
            "📨 **فوروارد**\n\nروی پیام ریپلای کن و بنویس:\n`/fwd @chat1 @chat2`\n"
            f"(حداکثر {MAX_TARGETS} مقصد در هر دستور، {MAX_PER_HOUR} فوروارد در ساعت، با فاصله‌ی چند ثانیه)")
    if len(targets) > MAX_TARGETS:
        return await message.reply_text(f"❌ حداکثر {MAX_TARGETS} مقصد در هر دستور.")
    if _quota() < len(targets):
        return await message.reply_text(f"⏳ سقف ساعتی فوروارد پر شده ({MAX_PER_HOUR}). بعداً امتحان کن.")
    ok, bad = [], []
    for i, t in enumerate(dict.fromkeys(targets)):
        if i:
            await asyncio.sleep(DELAY)
        try:
            await client.forward_messages(chat_id=t, from_chat_id=message.chat.id, message_ids=rep.id)
            _LOG.append(time.time())
            ok.append(str(t))
        except Exception as e:
            name = type(e).__name__
            bad.append(f"{t} ({name})")
            if name == "FloodWait":
                bad.append("⛔ به‌خاطر FloodWait بقیه متوقف شد")
                break
    lines = [f"📨 **نتیجه‌ی فوروارد**\n", f"✅ موفق: {len(ok)}" + (f" — {', '.join(ok)}" if ok else "")]
    if bad:
        lines.append("❌ ناموفق: " + "، ".join(bad))
    await message.reply_text("\n".join(lines))


def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command("fwd", prefixes="/.")), group=0)
