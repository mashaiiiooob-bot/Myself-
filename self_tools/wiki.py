import asyncio
import re
import requests
from pyrogram import filters
from pyrogram.handlers import MessageHandler

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    query = parts[1].strip() if len(parts) > 1 else ''
    if not query:
        return await message.reply_text('📚 **Wikipedia**\n\n**فرمت:** `/wiki تهران`')
    status = await message.reply_text('📚 در حال جستجو...')
    try:
        r = await asyncio.to_thread(requests.get, 'https://fa.wikipedia.org/w/api.php', params={'action': 'query', 'list': 'search', 'srsearch': query, 'format': 'json', 'srlimit': 5}, timeout=10)
        results = r.json().get('query', {}).get('search', [])
        if not results:
            r = await asyncio.to_thread(requests.get, 'https://en.wikipedia.org/w/api.php', params={'action': 'query', 'list': 'search', 'srsearch': query, 'format': 'json', 'srlimit': 1}, timeout=10)
            results = r.json().get('query', {}).get('search', [])
            if not results:
                return await status.edit_text(f'❌ چیزی پیدا نشد برای: `{query}`')
        page_title = results[0]['title']
        r2 = await asyncio.to_thread(requests.get, 'https://fa.wikipedia.org/w/api.php', params={'action': 'query', 'prop': 'extracts|info', 'exintro': True, 'explaintext': True, 'titles': page_title, 'format': 'json', 'inprop': 'url'}, timeout=10)
        page = list(r2.json()['query']['pages'].values())[0]
        extract = page.get('extract', '')[:1800]
        url = page.get('fullurl', '')
        text = f'\n📚 **ویکی\u200cپدیا — {page_title}**\n\n{extract}\n\n🔗 [مشاهده کامل]({url})\n\n📖 _نتایج دیگر:_\n' + '\n'.join([f'• {r['title']}' for r in results[1:5]])
        await status.edit_text(text[:4000], disable_web_page_preview=True)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('wiki', prefixes='/.')), group=0)
