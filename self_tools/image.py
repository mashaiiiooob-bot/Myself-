import asyncio
import io
import random
import urllib.parse
import requests
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    prompt = parts[1].strip() if len(parts) > 1 else ''
    if not prompt:
        return await message.reply_text('🎨 **AI Image**\n\n**فرمت:** `/image گربه فضانورد`\n**استایل:** `/image گربه --style anime`\n**استایل\u200cها:** anime, real, cartoon, dark')
    style = ''
    if ' --style ' in prompt:
        p = prompt.split(' --style ')
        prompt = p[0]
        style = p[1].strip()
    style_suffix = ''
    if style == 'anime':
        style_suffix = ', anime style, studio ghibli'
    elif style == 'real':
        style_suffix = ', photorealistic, 8k, hyperdetailed'
    elif style == 'cartoon':
        style_suffix = ', cartoon style, cute'
    elif style == 'dark':
        style_suffix = ', dark, moody, dramatic lighting'
    full_prompt = prompt + style_suffix
    status = await message.reply_text(f'🎨 در حال ساخت...\n_{prompt}_')
    try:
        url = f'https://image.pollinations.ai/prompt/{urllib.parse.quote(full_prompt)}?width=1024&height=1024&nologo=true&enhance=true&seed={random.randint(1, 999999)}'
        r = await asyncio.to_thread(requests.get, url, timeout=180)
        if r.status_code == 200:
            bio = io.BytesIO(r.content)
            bio.name = 'image.jpg'
            await message.reply_photo(bio, caption=f'🎨 **{prompt}**\n_{style or 'default'}_')
            await status.delete()
        else:
            await status.edit_text(f'❌ HTTP {r.status_code}')
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('image', prefixes=['/', '.'])), group=0)
