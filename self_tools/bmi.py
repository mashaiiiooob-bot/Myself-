from pyrogram import filters
from pyrogram.handlers import MessageHandler

def _bmi_category(bmi):
    if bmi < 18.5:
        return ('🔵 کمبود وزن', 'وزن شما کمتر از حد معمول است')
    elif bmi < 25:
        return ('🟢 وزن نرمال', 'وزن شما در محدوده سالم است')
    elif bmi < 30:
        return ('🟡 اضافه وزن', 'وزن شما کمی بیشتر از حد معمول است')
    elif bmi < 35:
        return ('🟠 چاقی درجه ۱', 'بهتره با پزشک مشورت کنی')
    elif bmi < 40:
        return ('🔴 چاقی درجه ۲', 'خطرناک - نیاز به مشورت پزشک')
    else:
        return ('⚫ چاقی درجه ۳', 'خیلی خطرناک - فوراً پزشک')

def _fa(n):
    return str(n).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))

async def handler(client, message):
    parts = (message.text or '').split()
    if len(parts) < 3:
        return await message.reply_text('⚖️ **BMI Calculator**\n\n**فرمت:** `/bmi 178 72`\n• اول: قد به سانتی\u200cمتر\n• دوم: وزن به کیلوگرم')
    try:
        height = float(parts[1])
        weight = float(parts[2])
    except ValueError:
        return await message.reply_text('❌ اعداد معتبر بده')
    if height < 50 or height > 300:
        return await message.reply_text('❌ قد باید بین ۵۰ تا ۳۰۰ سانتی\u200cمتر باشه')
    if weight < 10 or weight > 500:
        return await message.reply_text('❌ وزن باید بین ۱۰ تا ۵۰۰ کیلوگرم باشه')
    h_m = height / 100
    bmi = weight / h_m ** 2
    cat, advice = _bmi_category(bmi)
    ideal_min = 18.5 * h_m ** 2
    ideal_max = 24.9 * h_m ** 2
    await message.reply_text(f'⚖️ **محاسبه BMI**\n\n📏 قد: `{_fa(height)} cm`\n🏋️ وزن: `{_fa(weight)} kg`\n\n📊 **BMI:** `{bmi:.2f}`\n\n{cat}\n_{advice}_\n\n💡 **وزن سالم برای قد تو:**\n`{ideal_min:.1f}` تا `{ideal_max:.1f}` kg')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('bmi', prefixes=['/', '.'])), group=0)
