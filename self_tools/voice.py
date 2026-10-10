import asyncio
import os
import time
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    from gtts import gTTS
    OK = True
except ImportError:
    OK = False

async def handler(client, message):
    if not OK:
        return await message.reply_text('❌ `pip install gTTS`')
    parts = (message.text or '').split()
    text = ''
    lang = 'fa'
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
        if len(parts) > 1:
            lang = parts[1]
    elif len(parts) > 1:
        text = ' '.join(parts[1:])
    if not text:
        return await message.reply_text('🎤 **Text to Voice**\n\n**فرمت:** `/voice سلام`\n**زبان:** `/voice en hello`')
    if len(text) > 500:
        text = text[:500]
    status = await message.reply_text('🎤 در حال ساخت...')
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        path = f'/tmp/voice_{int(time.time())}.mp3'
        await asyncio.to_thread(tts.save, path)
        await message.reply_voice(path, caption=f'🎤 `{text[:80]}`')
        await status.delete()
        os.remove(path)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('voice', prefixes=['/', '.'])), group=0)
