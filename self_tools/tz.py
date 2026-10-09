import re
from datetime import datetime
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    from zoneinfo import ZoneInfo
    TZ_OK = True
except ImportError:
    try:
        from pytz import timezone as ZoneInfo
        TZ_OK = True
    except ImportError:
        TZ_OK = False
CITIES = {'تهران': 'Asia/Tehran', 'tehran': 'Asia/Tehran', 'لندن': 'Europe/London', 'london': 'Europe/London', 'نیویورک': 'America/New_York', 'newyork': 'America/New_York', 'new_york': 'America/New_York', 'nyc': 'America/New_York', 'توکیو': 'Asia/Tokyo', 'tokyo': 'Asia/Tokyo', 'دبی': 'Asia/Dubai', 'dubai': 'Asia/Dubai', 'استانبول': 'Europe/Istanbul', 'istanbul': 'Europe/Istanbul', 'مسکو': 'Europe/Moscow', 'moscow': 'Europe/Moscow', 'برلین': 'Europe/Berlin', 'berlin': 'Europe/Berlin', 'پاریس': 'Europe/Paris', 'paris': 'Europe/Paris', 'سیدنی': 'Australia/Sydney', 'sydney': 'Australia/Sydney', 'لوس\u200cآنجلس': 'America/Los_Angeles', 'losangeles': 'America/Los_Angeles', 'toronto': 'America/Toronto', 'تورنتو': 'America/Toronto', 'shanghai': 'Asia/Shanghai', 'شانگهای': 'Asia/Shanghai', 'beijing': 'Asia/Shanghai', 'پکن': 'Asia/Shanghai', 'delhi': 'Asia/Kolkata', 'دهلی': 'Asia/Kolkata', 'mumbai': 'Asia/Kolkata', 'بمبئی': 'Asia/Kolkata', 'riyadh': 'Asia/Riyadh', 'ریاض': 'Asia/Riyadh', 'mecca': 'Asia/Riyadh', 'مکه': 'Asia/Riyadh', 'کابل': 'Asia/Kabul', 'kabul': 'Asia/Kabul', 'بغداد': 'Asia/Baghdad', 'baghdad': 'Asia/Baghdad', 'کویت': 'Asia/Kuwait', 'kuwait': 'Asia/Kuwait', 'دوحه': 'Asia/Qatar', 'doha': 'Asia/Qatar', 'seoul': 'Asia/Seoul', 'سئول': 'Asia/Seoul', 'singapore': 'Asia/Singapore', 'سنگاپور': 'Asia/Singapore', 'bangkok': 'Asia/Bangkok', 'بانکوک': 'Asia/Bangkok', 'کوالالامپور': 'Asia/Kuala_Lumpur', 'kualalumpur': 'Asia/Kuala_Lumpur', 'کپنهاگ': 'Europe/Copenhagen', 'copenhagen': 'Europe/Copenhagen', 'آمستردام': 'Europe/Amsterdam', 'amsterdam': 'Europe/Amsterdam', 'رم': 'Europe/Rome', 'rome': 'Europe/Rome', 'مادرید': 'Europe/Madrid', 'madrid': 'Europe/Madrid', 'lisbon': 'Europe/Lisbon', 'لیسبون': 'Europe/Lisbon', 'athens': 'Europe/Athens', 'آتن': 'Europe/Athens', 'چین': 'Asia/Shanghai', 'china': 'Asia/Shanghai', 'هند': 'Asia/Kolkata', 'india': 'Asia/Kolkata', 'japan': 'Asia/Tokyo', 'ژاپن': 'Asia/Tokyo', 'usa': 'America/New_York', 'آمریکا': 'America/New_York', 'england': 'Europe/London', 'انگلیس': 'Europe/London', 'germany': 'Europe/Berlin', 'آلمان': 'Europe/Berlin', 'france': 'Europe/Paris', 'فرانسه': 'Europe/Paris', 'canada': 'America/Toronto', 'کانادا': 'America/Toronto', 'uae': 'Asia/Dubai', 'امارات': 'Asia/Dubai'}
QUICK_CITIES = ['تهران', 'لندن', 'نیویورک', 'توکیو', 'دبی', 'استانبول', 'مسکو', 'برلین']

def _get_tz(name):
    return CITIES.get(name.lower()) or CITIES.get(name) or (name if '/' in name else None)

def _fmt_time(dt):
    return dt.strftime('%H:%M:%S')

def _fmt_date(dt):
    return dt.strftime('%Y/%m/%d')

async def handler(client, message):
    if not TZ_OK:
        return await message.reply_text('❌ `pip install tzdata` یا `pip install pytz`')
    parts = (message.text or '').split(maxsplit=1)
    arg = parts[1].strip() if len(parts) > 1 else ''
    if not arg:
        lines = ['🕰 **ساعت شهرهای پرکاربرد**\n']
        for city_name in QUICK_CITIES:
            tz_name = CITIES.get(city_name)
            if not tz_name:
                continue
            try:
                tz = ZoneInfo(tz_name)
                now = datetime.now(tz)
                lines.append(f'• **{city_name}:** `{_fmt_time(now)}`')
            except Exception:
                continue
        lines.append(f'\n💡 `/tz <شهر>` برای ساعت خاص')
        return await message.reply_text('\n'.join(lines))
    m = re.match('^(\\d{1,2}):(\\d{2})\\s+(.+)$', arg)
    if m:
        h, mi, city = (int(m.group(1)), int(m.group(2)), m.group(3).strip())
        target_tz_name = _get_tz(city)
        if not target_tz_name:
            return await message.reply_text(f'❌ شهر پیدا نشد: `{city}`')
        try:
            from zoneinfo import ZoneInfo as ZI
            source_tz = ZI('Asia/Tehran')
            target_tz = ZI(target_tz_name)
        except Exception:
            try:
                from pytz import timezone as TZ
                source_tz = TZ('Asia/Tehran')
                target_tz = TZ(target_tz_name)
            except Exception:
                return await message.reply_text('❌ خطا در تبدیل منطقه زمانی')
        now = datetime.now(source_tz)
        source_dt = now.replace(hour=h, minute=mi, second=0, microsecond=0)
        target_dt = source_dt.astimezone(target_tz)
        await message.reply_text(f'🕰 **تبدیل ساعت**\n\n🇮🇷 **تهران:** `{_fmt_date(source_dt)} {_fmt_time(source_dt)}`\n\n🌍 **{city.title()}:** `{_fmt_date(target_dt)} {_fmt_time(target_dt)}`')
        return
    tz_name = _get_tz(arg)
    if not tz_name:
        return await message.reply_text(f'❌ شهر پیدا نشد: `{arg}`\n_برو `/tzlist` برای فهرست_')
    try:
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        try:
            tehran_tz = ZoneInfo('Asia/Tehran')
            tehran_now = datetime.now(tehran_tz)
        except Exception:
            tehran_now = None
        text = f'\n🕰 **ساعت {arg.title()}**\n\n📍 منطقه: `{tz_name}`\n📅 تاریخ: `{_fmt_date(now)}`\n⏰ ساعت: `{_fmt_time(now)}`\n\n🌐 _UTC Offset: `{now.strftime('%z')}`_\n'
        if tehran_now:
            text += f'\n🇮🇷 **تهران:** `{_fmt_time(tehran_now)}`'
        await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f'❌ خطا: `{e}`')

async def list_handler(client, message):
    lines = ['🌍 **شهرهای پشتیبانی\u200cشده**\n']
    seen = set()
    for name, tz in sorted(CITIES.items(), key=lambda x: x[1]):
        if tz in seen:
            continue
        seen.add(tz)
        lines.append(f'• `{name}`')
    lines.append(f'\n📌 _قابل استفاده با `/tz <شهر>`_')
    await message.reply_text('\n'.join(lines))

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('tz', prefixes='/.')), group=0)
    client.add_handler(MessageHandler(list_handler, filters.me & filters.command('tzlist', prefixes='/.')), group=0)
