import asyncio
import os
import time
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    from PIL import Image
    import pytesseract
    OK = True
except ImportError:
    OK = False

async def handler(client, message):
    if not OK:
        return await message.reply_text('❌ نصب نیست:\n`pip install Pillow pytesseract`\n`apt install tesseract-ocr tesseract-ocr-fas`')
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text('📌 روی یه عکس ریپلای کن')
    args = (message.text or '').split()
    lang = 'fas+eng'
    if len(args) > 1:
        if args[1] == 'en':
            lang = 'eng'
        elif args[1] == 'fa':
            lang = 'fas'
    status = await message.reply_text('🔤 در حال پردازش...')
    try:
        path = await message.reply_to_message.download()
        img = Image.open(path)
        text = await asyncio.to_thread(pytesseract.image_to_string, img, lang=lang)
        if not text.strip():
            return await status.edit_text('❌ متنی پیدا نشد')
        if len(text) > 4000:
            txt_path = f'/tmp/ocr_{int(time.time())}.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            await message.reply_document(txt_path, caption='🔤 متن استخراج\u200cشده')
            os.remove(txt_path)
        else:
            await status.edit_text(f'🔤 **متن استخراج\u200cشده:**\n\n{text[:4000]}')
        os.remove(path)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('ocr', prefixes=['/', '.'])), group=0)
