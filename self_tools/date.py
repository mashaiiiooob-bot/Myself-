import re
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    import jdatetime
    JDATE_OK = True
except ImportError:
    JDATE_OK = False
WEEKDAYS_FA = ['دوشنبه', 'سه\u200cشنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
MONTHS_FA = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def _fa_num(n):
    return str(n).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))

def _gregorian_to_jalali(gy, gm, gd):
    """تبدیل میلادی به شمسی بدون کتابخانه"""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    gy2 = gy + 1 if gm > 2 else gy
    days = 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400 - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return (jy, jm, jd)

def _jalali_to_gregorian(jy, jm, jd):
    """تبدیل شمسی به میلادی بدون کتابخانه"""
    jy += 1595
    days = -355668 + 365 * jy + jy // 33 * 8 + (jy % 33 + 3) // 4 + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += (jm - 7) * 30 + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and gy % 100 != 0 or gy % 400 == 0
    sal_a = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    for gm in range(1, 13):
        if gd <= sal_a[gm]:
            break
        gd -= sal_a[gm]
    return (gy, gm, gd)

async def handler(client, message):
    parts = (message.text or '').split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ''
    if not arg:
        now = datetime.now()
        gy, gm, gd = (now.year, now.month, now.day)
        if JDATE_OK:
            j = jdatetime.datetime.fromgregorian(datetime=now)
            jy, jm, jd = (j.year, j.month, j.day)
        else:
            jy, jm, jd = _gregorian_to_jalali(gy, gm, gd)
        wd = WEEKDAYS_FA[now.weekday()]
        time_str = now.strftime('%H:%M:%S')
        text = f'\n🗓 **تاریخ امروز**\n\n**🇮🇷 شمسی:**\n• `{_fa_num(jy)}/{_fa_num(jm):۰>2}/{_fa_num(jd):۰>2}`\n• {_fa_num(jd)} {MONTHS_FA[jm - 1]} {_fa_num(jy)}\n• روز: **{wd}**\n\n**🌍 میلادی:**\n• `{gy}/{gm:02d}/{gd:02d}`\n• {gd} {MONTHS_EN[gm - 1]} {gy}\n\n**⏰ ساعت:** `{_fa_num(time_str)}`\n'
        return await message.reply_text(text)
    m = re.match('^(\\d{4})[/\\-.](\\d{1,2})[/\\-.](\\d{1,2})$', arg)
    if not m:
        return await message.reply_text('**فرمت:**\n`/date` — امروز\n`/date 1404/6/5` — شمسی به میلادی\n`/date 2025/8/27` — میلادی به شمسی')
    y, mo, d = map(int, m.groups())
    if y < 1500:
        try:
            if JDATE_OK:
                g = jdatetime.date(y, mo, d).togregorian()
                gy, gm, gd = (g.year, g.month, g.day)
            else:
                gy, gm, gd = _jalali_to_gregorian(y, mo, d)
        except Exception:
            return await message.reply_text('❌ تاریخ شمسی اشتباه')
        try:
            dt = datetime(gy, gm, gd)
            wd = WEEKDAYS_FA[dt.weekday()]
        except Exception:
            wd = '-'
        text = f'\n🗓 **تبدیل شمسی → میلادی**\n\n**🇮🇷 شمسی:**\n• `{_fa_num(y)}/{_fa_num(mo):۰>2}/{_fa_num(d):۰>2}`\n• {_fa_num(d)} {MONTHS_FA[mo - 1]} {_fa_num(y)}\n\n**🌍 میلادی:**\n• `{gy}/{gm:02d}/{gd:02d}`\n• {gd} {MONTHS_EN[gm - 1]} {gy}\n• روز: **{wd}**\n'
        await message.reply_text(text)
    else:
        try:
            dt = datetime(y, mo, d)
        except Exception:
            return await message.reply_text('❌ تاریخ میلادی اشتباه')
        if JDATE_OK:
            j = jdatetime.datetime.fromgregorian(datetime=dt)
            jy, jm, jd = (j.year, j.month, j.day)
        else:
            jy, jm, jd = _gregorian_to_jalali(y, mo, d)
        wd = WEEKDAYS_FA[dt.weekday()]
        text = f'\n🗓 **تبدیل میلادی → شمسی**\n\n**🌍 میلادی:**\n• `{y}/{mo:02d}/{d:02d}`\n• {d} {MONTHS_EN[mo - 1]} {y}\n\n**🇮🇷 شمسی:**\n• `{_fa_num(jy)}/{_fa_num(jm):۰>2}/{_fa_num(jd):۰>2}`\n• {_fa_num(jd)} {MONTHS_FA[jm - 1]} {_fa_num(jy)}\n• روز: **{wd}**\n'
        await message.reply_text(text)

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('date', prefixes='/.')), group=0)
