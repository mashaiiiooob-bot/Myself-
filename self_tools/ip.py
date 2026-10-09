import asyncio
import requests
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    ip = parts[1].strip() if len(parts) > 1 else ''
    if not ip:
        return await message.reply_text('🌐 **IP Lookup**\n\n**فرمت:** `/ip 8.8.8.8`')
    status = await message.reply_text('🌐 در حال بررسی...')
    try:
        r = await asyncio.to_thread(requests.get, f'http://ip-api.com/json/{ip}?lang=fa&fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query,proxy,hosting,mobile', timeout=10)
        data = r.json()
        if data.get('status') != 'success':
            return await status.edit_text(f'❌ خطا: {data.get('message', 'نامشخص')}')
        text = f'\n🌐 **اطلاعات آی\u200cپی**\n\n**🔢 آی\u200cپی:** `{data.get('query')}`\n\n**🌍 موقعیت:**\n• کشور: {data.get('country')} ({data.get('countryCode')})\n• منطقه: {data.get('regionName')}\n• شهر: {data.get('city')}\n• کد پستی: {data.get('zip') or '-'}\n• مختصات: `{data.get('lat')}, {data.get('lon')}`\n\n**📡 شبکه:**\n• ISP: {data.get('isp')}\n• سازمان: {data.get('org')}\n• AS: {data.get('as')}\n\n**🔒 امنیت:**\n• پراکسی: {('⚠️ بله' if data.get('proxy') else '✅ خیر')}\n• هاستینگ: {('✅ بله' if data.get('hosting') else '❌ خیر')}\n• موبایل: {('✅ بله' if data.get('mobile') else '❌ خیر')}\n\n**🕐 منطقه زمانی:** {data.get('timezone')}\n\n🔗 [مشاهده روی نقشه](https://www.openstreetmap.org/?mlat={data.get('lat')}&mlon={data.get('lon')}&zoom=12)\n'
        await status.edit_text(text, disable_web_page_preview=True)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('ip', prefixes='/.')), group=0)
