import json
import os
import time
from pyrogram import filters
from pyrogram.handlers import MessageHandler
MAX_LEN = 20000

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    args = parts[1].strip() if len(parts) > 1 else ''
    mode = 'pretty'
    data = args
    for m in ('pretty', 'min', 'check'):
        if args.startswith(m + ' '):
            mode = m
            data = args[len(m):].strip()
            break
    if not data and message.reply_to_message:
        data = message.reply_to_message.text or message.reply_to_message.caption or ''
    if not data:
        return await message.reply_text('🧾 **JSON Formatter**\n\n`/json {\\"a\\":1}` — نمایش\n`/json pretty {...}` — خوانا\n`/json min {...}` — فشرده\n`/json check {...}` — بررسی')
    if len(data) > MAX_LEN:
        return await message.reply_text(f'❌ حداکثر {MAX_LEN} کاراکتر')
    try:
        obj = json.loads(data)
    except json.JSONDecodeError as e:
        return await message.reply_text(f'❌ **JSON نامعتبر**\n\n📍 خط: `{e.lineno}`\n📍 ستون: `{e.colno}`\n⚠️ {e.msg}')
    if mode == 'check':
        return await message.reply_text(f'✅ **JSON معتبره**\n\n📦 حجم: `{len(data):,}`\n📊 نوع: `{type(obj).__name__}`')
    if mode == 'min':
        out = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    else:
        out = json.dumps(obj, ensure_ascii=False, indent=2)
    if len(out) > 3500:
        path = f'/tmp/json_{int(time.time())}.json'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(out)
        await message.reply_document(path, caption=f'🧾 JSON ({mode})')
        os.remove(path)
    else:
        await message.reply_text(f'🧾 **JSON ({mode})**\n\n```json\n{out}\n```')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('json', prefixes=['/', '.'])), group=0)
