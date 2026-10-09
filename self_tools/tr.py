import asyncio
import re
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    from deep_translator import GoogleTranslator
    OK = True
except ImportError:
    OK = False
MAX_LEN = 450

def _parse(s):
    if not s:
        return (None, None, '')
    m = re.match('^(\\w{2})[|,](\\w{2})\\s+(.+)$', s, re.DOTALL)
    if m:
        return (m.group(1), m.group(2), m.group(3))
    m = re.match('^to\\s+(\\w{2})\\s+(.+)$', s, re.DOTALL | re.IGNORECASE)
    if m:
        return ('auto', m.group(1), m.group(2))
    m = re.match('^(\\w{2})\\s+(.+)$', s, re.DOTALL)
    if m:
        return ('auto', m.group(1), m.group(2))
    return ('auto', 'en', s)

async def handler(client, message):
    if not OK:
        return await message.reply_text('❌ `pip install deep-translator`')
    args = (message.text or '').split(maxsplit=1)
    args = args[1].strip() if len(args) > 1 else ''
    if not args:
        return await message.reply_text('🌐 **Translator**\n\n`/tr متن` — ترجمه به انگلیسی\n`/tr en متن` — ترجمه به انگلیسی\n`/tr fa متن` — ترجمه به فارسی\n`/tr en|fa hello` — انگلیسی به فارسی\n`/tr auto|fa hello` — تشخیص خودکار\n`/tr to en متن`')
    src, dst, text = _parse(args)
    if len(text) > MAX_LEN:
        return await message.reply_text(f'❌ حداکثر {MAX_LEN} کاراکتر')
    status = await message.reply_text('🌐 در حال ترجمه...')
    try:
        s = await asyncio.to_thread(GoogleTranslator(source=src or 'auto', target=dst).translate, text)
        if not s or s.strip() == text.strip():
            await status.edit_text(f'⚠️ **ترجمه تغییری نداد**\n\nمتن: `{text[:200]}`\nمبدأ: `{src or 'auto'}` — مقصد: `{dst}`')
            return
        await status.edit_text(f'🌐 **{src or 'auto'} → {dst}**\n\n📝 **اصلی:**\n`{text[:400]}`\n\n✅ **ترجمه:**\n`{s[:1500]}`')
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('tr', prefixes='/.')), group=0)
