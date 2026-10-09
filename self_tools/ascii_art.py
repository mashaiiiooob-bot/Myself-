import asyncio
import io
from pyrogram import filters
from pyrogram.handlers import MessageHandler

try:
    import pyfiglet
except ImportError:
    pyfiglet = None

_RAMP = "@%#*+=-:. "


def _img_to_ascii(data, cols=60):
    from PIL import Image
    img = Image.open(io.BytesIO(data)).convert("L")
    w, h = img.size
    rows = max(1, int(cols * h / w * 0.5))
    img = img.resize((cols, rows))
    px = img.load()
    return "\n".join("".join(_RAMP[px[x, y] * (len(_RAMP) - 1) // 255] for x in range(cols)) for y in range(rows))


async def handler(client, message):
    rep = message.reply_to_message
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ""
    if not arg and rep and rep.photo:
        status = await message.reply_text("🖼 در حال تبدیل...")
        try:
            bio = await client.download_media(rep, in_memory=True)
            data = bio.getvalue() if hasattr(bio, "getvalue") else bytes(bio)
            art = await asyncio.to_thread(_img_to_ascii, data)
            return await status.edit_text(f"```\n{art[:3900]}\n```")
        except Exception as e:
            return await status.edit_text(f"❌ خطا: `{type(e).__name__}`")
    if not arg and rep:
        arg = (rep.text or rep.caption or "").strip()
    if not arg:
        return await message.reply_text("**فرمت:** `/ascii text` (حداکثر ۱۲ حرف انگلیسی)\nیا روی یک عکس ریپلای کن.")
    if pyfiglet is None:
        return await message.reply_text("❌ `pip install pyfiglet`")
    arg = arg[:12]
    try:
        art = pyfiglet.figlet_format(arg, width=60)
    except Exception as e:
        return await message.reply_text(f"❌ خطا: `{type(e).__name__}`")
    await message.reply_text(f"```\n{art.rstrip()[:3900]}\n```")


def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command("ascii", prefixes="/.")), group=0)
