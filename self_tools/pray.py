import asyncio
import requests
import urllib.parse
from datetime import datetime
from pyrogram import filters
from pyrogram.handlers import MessageHandler
DEFAULT_CITIES = {'تهران': 'tehran', 'مشهد': 'mashhad', 'اصفهان': 'isfahan', 'شیراز': 'shiraz', 'تبریز': 'tabriz', 'کرج': 'karaj', 'اهواز': 'ahvaz', 'قم': 'qom', 'کرمان': 'kerman', 'رشت': 'rasht', 'یزد': 'yazd', 'ارومیه': 'urmia', 'زاهدان': 'zahedan', 'کرمانشاه': 'kermanshah', 'بندرعباس': 'bandarabbas', 'اردبیل': 'ardebil'}

def _fa(n):
    return str(n).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    city = parts[1].strip() if len(parts) > 1 else 'تهران'
    city_key = DEFAULT_CITIES.get(city, city.lower())
    status = await message.reply_text('🕌 در حال دریافت اوقات شرعی...')
    try:
        url = f'https://api.aladhan.com/v1/timingsByCity'
        params = {'city': city_key, 'country': 'Iran', 'method': 7}
        r = await asyncio.to_thread(requests.get, url, params=params, timeout=10)
        data = r.json()
        if data.get('code') != 200:
            return await status.edit_text(f'❌ شهر پیدا نشد: `{city}`')
        timings = data['data']['timings']
        date_info = data['data']['date']['gregorian']
        hijri = data['data']['date']['hijri']
        text = f'\n🕌 **اوقات شرعی — {city}**\n\n**📅 تاریخ:**\n• میلادی: `{date_info['date']}`\n• قمری: `{hijri['day']} {hijri['month']['ar']} {hijri['year']}`\n\n**🌙 اوقات:**\n• **اذان صبح:** `{_fa(timings['Fajr'])}`\n• **طلوع آفتاب:** `{_fa(timings['Sunrise'])}`\n• **اذان ظهر:** `{_fa(timings['Dhuhr'])}`\n• **غروب:** `{_fa(timings['Sunset'])}`\n• **اذان مغرب:** `{_fa(timings['Maghrib'])}`\n• **اذان عشا:** `{_fa(timings['Isha'])}`\n\n**🌙 نیمه\u200cشب:** `{_fa(timings['Midnight'])}`\n\n📌 _به وقت رسمی تهران_\n'
        await status.edit_text(text)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('pray', prefixes='/.')), group=0)
