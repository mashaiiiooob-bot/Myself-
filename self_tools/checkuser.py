import re
from pyrogram import filters
from pyrogram.handlers import MessageHandler

_RX = re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,31}$")


async def handler(client, message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply_text("**فرمت:** `/checkuser @username`")
    name = parts[1].strip().replace("https://t.me/", "").replace("t.me/", "").lstrip("@")
    if not _RX.match(name) or name.endswith("_") or "__" in name:
        return await message.reply_text("❌ یوزرنیم نامعتبر است (۵ تا ۳۲ حرف، با حرف شروع شود، فقط حروف انگلیسی، عدد و _).")
    try:
        chat = await client.get_chat(name)
    except Exception as e:
        en = type(e).__name__
        if en in ("UsernameNotOccupied", "UsernameInvalid", "PeerIdInvalid"):
            return await message.reply_text(f"🟢 `@{name}` به‌نظر آزاد است.\n_(ممکن است رزرو یا برای فروش باشد؛ در تنظیمات تلگرام تأیید نهایی کنید.)_")
        return await message.reply_text(f"⚠️ بررسی انجام نشد: `{en}`")
    kind = str(chat.type).split(".")[-1].lower()
    title = chat.title or " ".join(x for x in (getattr(chat, "first_name", None), getattr(chat, "last_name", None)) if x) or "—"
    await message.reply_text(f"🔴 `@{name}` گرفته شده است.\n🧩 نوع: {kind}\n📛 نام: {title}")


def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command("checkuser", prefixes="/.")), group=0)
