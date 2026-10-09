from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    text = parts[1] if len(parts) > 1 else ''
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not text:
        return await message.reply_text('**فرمت:** `/stats متن` یا ریپلای کن')
    chars = len(text)
    chars_no_space = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
    words = len(text.split())
    lines = len(text.splitlines())
    unique_words = len(set((w.lower() for w in text.split())))
    longest = max(text.split(), key=len) if text.split() else '-'
    avg_word = sum((len(w) for w in text.split())) / words if words else 0
    await message.reply_text(f'📈 **آمار متن**\n\n📝 **کاراکتر:** `{chars:,}`\n📝 **بدون فاصله:** `{chars_no_space:,}`\n📚 **کلمه:** `{words:,}`\n📄 **خط:** `{lines:,}`\n🔤 **کلمات یکتا:** `{unique_words:,}`\n\n📏 **میانگین طول کلمه:** `{avg_word:.1f}`\n🏆 **طولانی\u200cترین کلمه:** `{longest[:50]}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('stats', prefixes='/.')), group=0)
