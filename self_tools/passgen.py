import random
import string
from pyrogram import filters
from pyrogram.handlers import MessageHandler
MIN_LEN = 8
MAX_LEN = 64

def _gen_password(length, use_symbols=True):
    chars = string.ascii_letters + string.digits
    if use_symbols:
        chars += '!@#$%^&*()-_=+[]{};:,.<>?/'
    pwd = [random.choice(string.ascii_lowercase), random.choice(string.ascii_uppercase), random.choice(string.digits)]
    if use_symbols:
        pwd.append(random.choice('!@#$%^&*()-_=+'))
    while len(pwd) < length:
        pwd.append(random.choice(chars))
    random.shuffle(pwd)
    return ''.join(pwd)

def _strength(pwd):
    score = 0
    if len(pwd) >= 12:
        score += 1
    if len(pwd) >= 20:
        score += 1
    if any((c.islower() for c in pwd)):
        score += 1
    if any((c.isupper() for c in pwd)):
        score += 1
    if any((c.isdigit() for c in pwd)):
        score += 1
    if any((c in '!@#$%^&*()-_=+[]{};:,.<>?/' for c in pwd)):
        score += 1
    if score >= 6:
        return '🟢 قوی'
    if score >= 4:
        return '🟡 متوسط'
    return '🔴 ضعیف'

async def handler(client, message):
    parts = (message.text or '').split()
    length = 16
    use_symbols = True
    if len(parts) > 1:
        try:
            length = int(parts[1])
        except ValueError:
            return await message.reply_text('❌ طول باید عدد باشه')
    if len(parts) > 2 and parts[2].lower() in ('nosym', 'nosymbols'):
        use_symbols = False
    if length < MIN_LEN or length > MAX_LEN:
        return await message.reply_text(f'❌ طول باید بین {MIN_LEN} و {MAX_LEN} باشه')
    pwd = _gen_password(length, use_symbols)
    await message.reply_text(f'🔐 **Password Generator**\n\n🔑 `{pwd}`\n\n📏 طول: `{length}`\n🔤 نمادها: {('✅' if use_symbols else '❌')}\n💪 قدرت: {_strength(pwd)}')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('passgen', prefixes=['/', '.'])), group=0)
