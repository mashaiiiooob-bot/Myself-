from pyrogram import filters
from pyrogram.handlers import MessageHandler


def _flag(v):
    return "✅" if v else "❌"


async def _resolve_user(client, message):
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""
    if not arg and message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    if not arg:
        return "me"
    arg = arg.replace("https://t.me/", "").replace("t.me/", "").lstrip("@").strip()
    return int(arg) if arg.lstrip("-").isdigit() else arg


async def handler(client, message):
    try:
        u = await client.get_users(await _resolve_user(client, message))
    except Exception as e:
        return await message.reply_text(f"❌ کاربر پیدا نشد.\n`{type(e).__name__}`")
    bio = ""
    try:
        bio = (await client.get_chat(u.id)).bio or ""
    except Exception:
        pass
    name = " ".join(x for x in (u.first_name, u.last_name) if x) or "—"
    uname = f"@{u.username}" if u.username else "—"
    status = str(u.status).split(".")[-1].lower() if getattr(u, "status", None) else "—"
    lines = [
        "👤 **اطلاعات کاربر**", "",
        f"🆔 آیدی: `{u.id}`",
        f"📛 نام: {name}",
        f"🔗 یوزرنیم: {uname}",
        f"🤖 ربات: {_flag(u.is_bot)}   ⭐ پریمیوم: {_flag(getattr(u, 'is_premium', False))}",
        f"✔️ تأییدشده: {_flag(getattr(u, 'is_verified', False))}   ⚠️ اسکم: {_flag(getattr(u, 'is_scam', False))}   🎭 فیک: {_flag(getattr(u, 'is_fake', False))}",
        f"🕒 وضعیت: {status}",
        f"🌐 DC: {getattr(u, 'dc_id', None) or '—'}",
    ]
    if bio:
        lines += ["", f"📝 بیو: {bio[:300]}"]
    if u.username:
        lines += ["", f"https://t.me/{u.username}"]
    await message.reply_text("\n".join(lines), disable_web_page_preview=True)


def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command(["userinfo", "whois"], prefixes=["/", "."])), group=0)
