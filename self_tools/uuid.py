import uuid
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    u = uuid.uuid4()
    await message.reply_text(f'🔢 **UUID v4**\n\n`{u}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('uuid', prefixes='/.')), group=0)
