import asyncio
import urllib.parse
import requests
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    prompt = parts[1].strip() if len(parts) > 1 else ''
    if not prompt and message.reply_to_message:
        prompt = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not prompt:
        return await message.reply_text('🤖 **AI Assistant**\n\n**فرمت:** `/ai سلام`\n**یا:** روی یه پیام ریپلای کن')
    mode = ''
    if prompt.startswith('ترجمه '):
        mode = 'translate'
        prompt = prompt[6:]
    elif prompt.startswith('خلاصه '):
        mode = 'summarize'
        prompt = prompt[6:]
    elif prompt.startswith('کد '):
        mode = 'code'
        prompt = prompt[4:]
    status = await message.reply_text('🤖 در حال پردازش...')
    try:
        if mode == 'translate':
            full = f'این متن رو به فارسی ترجمه کن:\n\n{prompt}'
        elif mode == 'summarize':
            full = f'این متن رو خلاصه کن (حداکثر ۵ خط):\n\n{prompt}'
        elif mode == 'code':
            full = f'این کد رو توضیح بده:\n\n{prompt}'
        else:
            full = f'سوال کاربر (به فارسی جواب بده):\n\n{prompt}'
        r = await asyncio.to_thread(requests.get, f'https://text.pollinations.ai/{urllib.parse.quote(full)}', timeout=90)
        await status.edit_text(f'🤖 **پاسخ:**\n\n{r.text[:4000]}')
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('ai', prefixes='/.')), group=0)
