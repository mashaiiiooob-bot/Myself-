import asyncio
import requests
import urllib.parse
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    city = parts[1].strip() if len(parts) > 1 else ''
    if not city:
        return await message.reply_text('☀️ **Weather**\n\n**فرمت:** `/weather تهران`')
    status = await message.reply_text('☀️ در حال دریافت...')
    try:
        r = await asyncio.to_thread(requests.get, f'https://wttr.in/{urllib.parse.quote(city)}?format=j1', timeout=10)
        data = r.json()
        c = data['current_condition'][0]
        area = data['nearest_area'][0]
        today = data['weather'][0]
        text = f'\n☀️ **آب و هوای {area['areaName'][0]['value']}**\n\n**🌡 دما:**\n• فعلی: `{c['temp_C']}°C`\n• حسی: `{c['FeelsLikeC']}°C`\n• بیشترین: `{today['maxtempC']}°C`\n• کمترین: `{today['mintempC']}°C`\n\n**☁️ وضعیت:** {c['weatherDesc'][0]['value']}\n\n**💧 رطوبت:** `{c['humidity']}%`\n**💨 باد:** `{c['windspeedKmph']} km/h` ({c['winddir16Point']})\n**👁 دید:** `{c['visibility']} km`\n**🔽 فشار:** `{c['pressure']} mb`\n**☂️ بارش:** `{c['precipMM']} mm`\n\n**🌅 طلوع:** `{today['astronomy'][0]['sunrise']}`\n**🌇 غروب:** `{today['astronomy'][0]['sunset']}`\n**🌙 ماه:** {today['astronomy'][0]['moon_phase']}\n'
        await status.edit_text(text)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('weather', prefixes='/.')), group=0)
