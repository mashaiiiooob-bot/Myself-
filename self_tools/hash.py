import hashlib
from pyrogram import filters
from pyrogram.handlers import MessageHandler
MAX_LEN = 2000

def _hash(text, algo):
    if algo == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    if algo == 'sha1':
        return hashlib.sha1(text.encode()).hexdigest()
    if algo == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    if algo == 'sha512':
        return hashlib.sha512(text.encode()).hexdigest()
    return None

async def _handle(client, message, algo):
    parts = (message.text or '').split(maxsplit=1)
    text = parts[1] if len(parts) > 1 else ''
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not text:
        return await message.reply_text(f'**فرمت:** `/{algo} متن` یا ریپلای کن')
    if len(text) > MAX_LEN:
        return await message.reply_text(f'❌ حداکثر {MAX_LEN} کاراکتر')
    h = _hash(text, algo)
    await message.reply_text(f'🔐 **{algo.upper()}**\n\n📝 **ورودی:**\n`{text[:200]}`\n\n🔑 **هش:**\n`{h}`')

async def md5_h(client, m):
    return await _handle(client, m, 'md5')

async def sha1_h(client, m):
    return await _handle(client, m, 'sha1')

async def sha256_h(client, m):
    return await _handle(client, m, 'sha256')

async def sha512_h(client, m):
    return await _handle(client, m, 'sha512')

def register(client):
    for cmd, h in [('md5', md5_h), ('sha1', sha1_h), ('sha256', sha256_h), ('sha512', sha512_h)]:
        client.add_handler(MessageHandler(h, filters.me & filters.command(cmd, prefixes='/.')), group=0)
