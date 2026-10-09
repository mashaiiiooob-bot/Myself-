import asyncio
import os
import requests
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    from rembg import remove
    from PIL import Image
    REMBG_OK = True
except ImportError:
    REMBG_OK = False
REMOVEBG_API_KEY = os.environ.get('REMOVEBG_API_KEY', '')

async def handler(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text('📌 روی یه عکس ریپلای کن')
    status = await message.reply_text('✂️ در حال حذف پس\u200cزمینه...')
    path = None
    try:
        path = await message.reply_to_message.download()
        out = path + '_nobg.png'
        if REMBG_OK:
            img_in = Image.open(path)
            img_out = remove(img_in)
            img_out.save(out)
            await message.reply_document(out, caption='✂️ پس\u200cزمینه حذف شد (rembg)')
            await status.delete()
            return
        if REMOVEBG_API_KEY:
            with open(path, 'rb') as f:
                r = await asyncio.to_thread(requests.post, 'https://api.remove.bg/v1.0/removebg', files={'image_file': f}, data={'size': 'auto'}, headers={'X-Api-Key': REMOVEBG_API_KEY}, timeout=60)
            if r.status_code == 200:
                with open(out, 'wb') as f:
                    f.write(r.content)
                await message.reply_document(out, caption='✂️ پس\u200cزمینه حذف شد (remove.bg)')
                await status.delete()
                return
            else:
                return await status.edit_text(f'❌ remove.bg: HTTP {r.status_code}')
        await status.edit_text('❌ هیچ روشی فعال نیست:\n\n**روش ۱ (لوکال):**\n`pip install rembg`\n\n**روش ۲ (API):**\nاز https://www.remove.bg/api کلید رایگان بگیر\nو توی کد بذار')
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
        try:
            if path and os.path.exists(path + '_nobg.png'):
                os.remove(path + '_nobg.png')
        except Exception:
            pass

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('removebg', prefixes='/.')), group=0)
