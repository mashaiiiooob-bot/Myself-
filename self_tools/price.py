import asyncio
import requests
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    status = await message.reply_text('💰 در حال دریافت قیمت\u200cها...')
    try:
        r = await asyncio.to_thread(requests.get, 'https://call1.tgju.org/ajax.json', timeout=10)
        data = r.json().get('current', {})

        def gp(key):
            row = data.get(key, {})
            val = row.get('p', '0')
            try:
                return int(val.replace(',', ''))
            except Exception:
                return 0

        def gd(key):
            return data.get(key, {}).get('dt', '0')

        def fmt(n):
            return f'{n:,}'
        text = f'\n💰 **قیمت لحظه\u200cای بازار**\n\n**💵 ارزها:**\n• دلار: `{fmt(gp('price_dollar_rl'))}` {gd('price_dollar_rl')}ت\n• یورو: `{fmt(gp('price_eur'))}` {gd('price_eur')}ت\n• پوند: `{fmt(gp('price_gbp'))}` {gd('price_gbp')}ت\n• درهم: `{fmt(gp('price_aed'))}` {gd('price_aed')}ت\n• لیر: `{fmt(gp('price_try'))}` {gd('price_try')}ت\n\n**🏅 طلا:**\n• طلا ۱۸: `{fmt(gp('geram18'))}` {gd('geram18')}ت\n• طلا ۲۴: `{fmt(gp('geram24'))}` {gd('geram24')}ت\n• مثقال: `{fmt(gp('mesghal'))}` {gd('mesghal')}ت\n\n**🪙 سکه:**\n• امامی: `{fmt(gp('sekee'))}` {gd('sekee')}ت\n• نیم: `{fmt(gp('nim'))}` {gd('nim')}ت\n• ربع: `{fmt(gp('rob'))}` {gd('rob')}ت\n• گرمی: `{fmt(gp('gerami'))}` {gd('gerami')}ت\n\n🕐 _{data.get('price_dollar_rl', {}).get('t', '-')}_\n'
        await status.edit_text(text)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('price', prefixes=['/', '.'])), group=0)
