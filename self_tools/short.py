import asyncio
import urllib.parse
import requests
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    url = parts[1].strip() if len(parts) > 1 else ''
    if not url and message.reply_to_message:
        url = message.reply_to_message.text or message.reply_to_message.caption or ''
        url = url.strip()
    if not url:
        return await message.reply_text('🔗 **Short Link**\n\n**فرمت:** `/short https://example.com/very/long/link`')
    if not (url.startswith('http://') or url.startswith('https://')):
        return await message.reply_text('❌ لینک باید با `http://` یا `https://` شروع بشه')
    status = await message.reply_text('🔗 در حال کوتاه کردن...')
    try:
        r = await asyncio.to_thread(requests.get, 'https://is.gd/create.php', params={'format': 'simple', 'url': url}, timeout=10)
        if r.status_code != 200 or 'error' in r.text.lower()[:30]:
            r = await asyncio.to_thread(requests.get, 'https://v.gd/create.php', params={'format': 'simple', 'url': url}, timeout=10)
        short = r.text.strip()
        if not short.startswith('http'):
            return await status.edit_text(f'❌ خطا: `{short[:100]}`')
        await status.edit_text(f'🔗 **لینک کوتاه شد**\n\n📎 **اصلی:**\n`{url[:200]}`\n\n✅ **کوتاه:**\n`{short}`')
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('short', prefixes=['/', '.'])), group=0)
