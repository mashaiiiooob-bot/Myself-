import os
import time
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    import qrcode
    QR_OK = True
except ImportError:
    QR_OK = False

async def handler(client, message):
    if not QR_OK:
        return await message.reply_text('❌ `pip install qrcode[pil]`')
    parts = (message.text or '').split(maxsplit=1)
    text = parts[1] if len(parts) > 1 else ''
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not text:
        return await message.reply_text('**فرمت:** `/qr متن یا لینک`')
    if len(text) > 2000:
        return await message.reply_text('❌ حداکثر ۲۰۰۰ کاراکتر')
    status = await message.reply_text('🔳 در حال ساخت...')
    try:
        img = qrcode.make(text)
        import tempfile
        path = tempfile.mkstemp(prefix='qr_', suffix='.png')[1]
        img.save(path)
        await message.reply_photo(path, caption=f'🔳 `{text[:80]}`')
        await status.delete()
        os.remove(path)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('qr', prefixes=['/', '.'])), group=0)
