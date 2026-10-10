from pyrogram import filters
from pyrogram.handlers import MessageHandler

_G = {}
_MEM = {}
MAX_LEN = 500


def _dm():
    return _G.get("data_manager")


def get_persona(uid):
    """Custom system prompt used by /ai (empty string when none)."""
    try:
        dm = _dm()
        if dm is not None:
            return str(dm.get_user_data(uid).get("ai_prompt") or "")
    except Exception:
        pass
    return _MEM.get(uid, "")


def _set(uid, text):
    _MEM[uid] = text
    dm = _dm()
    if dm is not None:
        dm.update_user_data(uid, {"ai_prompt": text})


async def handler(client, message):
    uid = client.me.id
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""
    if not arg and message.reply_to_message:
        arg = (message.reply_to_message.text or message.reply_to_message.caption or "").strip()
    cur = get_persona(uid)
    if not arg:
        return await message.reply_text(
            "🎭 **پرامپت هوش مصنوعی (`/ai`)**\n\n"
            + (f"فعلی:\n`{cur}`\n\n" if cur else "فعلاً تنظیم نشده.\n\n")
            + "**تنظیم:** `/prompt تو یک دستیار شوخ‌طبع هستی`\n**حذف:** `/prompt reset`")
    if arg.lower() in ("reset", "off", "clear", "حذف", "پاک"):
        _set(uid, "")
        return await message.reply_text("🗑 پرامپت حذف شد.")
    if len(arg) > MAX_LEN:
        return await message.reply_text(f"❌ حداکثر {MAX_LEN} کاراکتر.")
    _set(uid, arg)
    await message.reply_text(f"✅ پرامپت ذخیره شد و از این به بعد در `/ai` استفاده می‌شود.\n\n`{arg}`")


def register(client):
    global _G
    _G = getattr(client, "g", None) or {}
    client.add_handler(MessageHandler(handler, filters.me & filters.command("prompt", prefixes=["/", "."])), group=0)
