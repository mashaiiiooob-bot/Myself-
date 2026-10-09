import asyncio
import requests
from datetime import datetime
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    status = await message.reply_text('🪙 در حال دریافت...')
    try:
        ids = 'bitcoin,ethereum,tether,tron,dogecoin,ripple,solana,cardano,binancecoin,litecoin'
        r = await asyncio.to_thread(requests.get, 'https://api.coingecko.com/api/v3/simple/price', params={'ids': ids, 'vs_currencies': 'usd', 'include_24hr_change': 'true'}, timeout=15)
        data = r.json()
        coins = {'bitcoin': '🥇 بیت\u200cکوین', 'ethereum': '💎 اتریوم', 'tether': '💵 تتر', 'tron': '⚡ ترون', 'ripple': '🌊 ریپل', 'dogecoin': '🐕 دوج', 'solana': '☀️ سولانا', 'cardano': '🔷 کاردانو', 'binancecoin': '🟡 BNB', 'litecoin': '⚪ لایت\u200cکوین'}
        lines = ['🪙 **قیمت لحظه\u200cای رمزارزها**\n']
        for cid, name in coins.items():
            c = data.get(cid, {})
            price = c.get('usd', 0)
            change = c.get('usd_24h_change', 0)
            emoji = '🟢' if change >= 0 else '🔴'
            lines.append(f'{name}: `${price:,.2f}` {emoji} `{change:+.2f}%`')
        lines.append(f'\n🕐 _{datetime.now().strftime('%H:%M:%S')}_')
        await status.edit_text('\n'.join(lines))
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('crypto', prefixes='/.')), group=0)
