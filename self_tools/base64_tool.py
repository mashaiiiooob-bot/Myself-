import base64
import binascii
from pyrogram import filters
from pyrogram.handlers import MessageHandler
MAX_LEN = 5000

async def encode_handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    text = parts[1] if len(parts) > 1 else ''
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not text:
        return await message.reply_text('**فرمت:** `/b64e متن`')
    if len(text) > MAX_LEN:
        return await message.reply_text(f'❌ حداکثر {MAX_LEN} کاراکتر')
    encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')
    await message.reply_text(f'🔐 **Base64 Encode**\n\n📝 **اصلی:**\n`{text[:200]}`\n\n🔑 **Base64:**\n`{encoded[:1000]}`')

async def decode_handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    text = parts[1].strip() if len(parts) > 1 else ''
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not text:
        return await message.reply_text('**فرمت:** `/b64d SGVsbG8=`')
    if len(text) > MAX_LEN:
        return await message.reply_text(f'❌ حداکثر {MAX_LEN} کاراکتر')
    text = text.strip().replace('\n', '').replace(' ', '')
    try:
        decoded = base64.b64decode(text, validate=True).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError):
        try:
            decoded = base64.b64decode(text + '==', validate=False).decode('utf-8')
        except Exception:
            return await message.reply_text('❌ **Base64 نامعتبره**')
    await message.reply_text(f'🔓 **Base64 Decode**\n\n📝 **Base64:**\n`{text[:200]}`\n\n✅ **متن:**\n`{decoded[:1500]}`')

def register(client):
    client.add_handler(MessageHandler(encode_handler, filters.me & filters.command('b64e', prefixes='/.')), group=0)
    client.add_handler(MessageHandler(decode_handler, filters.me & filters.command('b64d', prefixes='/.')), group=0)
