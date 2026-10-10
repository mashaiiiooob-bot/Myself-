from pyrogram import filters
from pyrogram.handlers import MessageHandler


def _target(message):
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""
    if not arg:
        return message.chat.id
    arg = arg.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "").lstrip("@").strip("/")
    if arg.startswith("+") or arg.startswith("joinchat"):
        return arg  # invite links need the full link
    return int(arg) if arg.lstrip("-").isdigit() else arg


def _type_name(chat):
    return str(chat.type).split(".")[-1].lower()


async def _show(client, message, want):
    try:
        t = _target(message)
        chat = await client.get_chat(t)
    except Exception as e:
        return await message.reply_text(f"❌ چت پیدا نشد یا دسترسی ندارم.\n`{type(e).__name__}`")
    kind = _type_name(chat)
    icon = "📢" if kind == "channel" else "👥" if kind in ("group", "supergroup") else "👤"
    lines = [f"{icon} **{'اطلاعات کانال' if want == 'channel' else 'اطلاعات گروه'}**", "",
             f"📛 عنوان: {chat.title or chat.first_name or '—'}",
             f"🆔 آیدی: `{chat.id}`",
             f"🧩 نوع: {kind}",
             f"🔗 یوزرنیم: {('@' + chat.username) if chat.username else '—'}"]
    if getattr(chat, "members_count", None) is not None:
        lines.append(f"👥 اعضا: {chat.members_count:,}")
    if getattr(chat, "linked_chat", None):
        lines.append(f"🔁 چت متصل: {chat.linked_chat.title or chat.linked_chat.id}")
    flags = []
    for attr, label in (("is_verified", "تأییدشده"), ("is_scam", "اسکم"), ("is_fake", "فیک"), ("is_restricted", "محدود"), ("has_protected_content", "محتوای محافظت‌شده")):
        if getattr(chat, attr, False):
            flags.append(label)
    if flags:
        lines.append("🏷 وضعیت: " + "، ".join(flags))
    if getattr(chat, "dc_id", None):
        lines.append(f"🌐 DC: {chat.dc_id}")
    if chat.description or getattr(chat, "bio", None):
        lines += ["", f"📝 توضیحات: {(chat.description or chat.bio)[:400]}"]
    if (want == "channel" and kind != "channel") or (want == "group" and kind == "channel"):
        lines += ["", f"ℹ️ این چت از نوع {kind} است."]
    await message.reply_text("\n".join(lines), disable_web_page_preview=True)


async def group_handler(client, message):
    await _show(client, message, "group")


async def channel_handler(client, message):
    await _show(client, message, "channel")


def register(client):
    client.add_handler(MessageHandler(group_handler, filters.me & filters.command("groupinfo", prefixes=["/", "."])), group=0)
    client.add_handler(MessageHandler(channel_handler, filters.me & filters.command("channelinfo", prefixes=["/", "."])), group=0)
