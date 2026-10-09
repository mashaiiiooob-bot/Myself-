import re
from pyrogram import filters
from pyrogram.handlers import MessageHandler
UNITS = {'length': {'m': 1, 'meter': 1, 'meters': 1, 'متر': 1, 'km': 1000, 'kilometer': 1000, 'kilometers': 1000, 'کیلومتر': 1000, 'cm': 0.01, 'centimeter': 0.01, 'سانتی\u200cمتر': 0.01, 'سانتیمتر': 0.01, 'mm': 0.001, 'millimeter': 0.001, 'میلی\u200cمتر': 0.001, 'mi': 1609.344, 'mile': 1609.344, 'miles': 1609.344, 'مایل': 1609.344, 'yd': 0.9144, 'yard': 0.9144, 'یارد': 0.9144, 'ft': 0.3048, 'foot': 0.3048, 'feet': 0.3048, 'پا': 0.3048, 'in': 0.0254, 'inch': 0.0254, 'اینچ': 0.0254, 'nmi': 1852, 'nautical_mile': 1852}, 'weight': {'kg': 1, 'kilogram': 1, 'kilograms': 1, 'کیلوگرم': 1, 'کیلو': 1, 'g': 0.001, 'gram': 0.001, 'grams': 0.001, 'گرم': 0.001, 'mg': 1e-06, 'milligram': 1e-06, 'میلی\u200cگرم': 1e-06, 'lb': 0.45359237, 'lbs': 0.45359237, 'pound': 0.45359237, 'پوند': 0.45359237, 'oz': 0.0283495, 'ounce': 0.0283495, 'اونس': 0.0283495, 'ton': 1000, 'tonne': 1000, 'تن': 1000, 'st': 6.35029, 'stone': 6.35029}, 'volume': {'l': 1, 'liter': 1, 'liters': 1, 'لیتر': 1, 'ml': 0.001, 'milliliter': 0.001, 'میلی\u200cلیتر': 0.001, 'gal': 3.78541, 'gallon': 3.78541, 'گالن': 3.78541, 'qt': 0.946353, 'quart': 0.946353, 'pt': 0.473176, 'pint': 0.473176, 'cup': 0.236588, 'فنجان': 0.236588, 'floz': 0.0295735, 'fluid_ounce': 0.0295735, 'm3': 1000, 'cubic_meter': 1000}, 'area': {'m2': 1, 'sqm': 1, 'مترمربع': 1, 'km2': 1000000, 'sqkm': 1000000, 'کیلومترمربع': 1000000, 'cm2': 0.0001, 'sqcm': 0.0001, 'ha': 10000, 'hectare': 10000, 'هکتار': 10000, 'acre': 4046.86, 'ایکر': 4046.86, 'ft2': 0.092903, 'sqft': 0.092903, 'فوت\u200cمربع': 0.092903}, 'speed': {'mps': 1, 'm/s': 1, 'kph': 0.277778, 'km/h': 0.277778, 'kmh': 0.277778, 'کیلومتربرساعت': 0.277778, 'mph': 0.44704, 'مایل\u200cبرساعت': 0.44704, 'knot': 0.514444, 'kn': 0.514444, 'گره': 0.514444, 'fps': 0.3048, 'ft/s': 0.3048}, 'digital': {'b': 1, 'byte': 1, 'bytes': 1, 'بایت': 1, 'kb': 1024, 'kilobyte': 1024, 'کیلوبایت': 1024, 'mb': 1024 ** 2, 'megabyte': 1024 ** 2, 'مگابایت': 1024 ** 2, 'gb': 1024 ** 3, 'gigabyte': 1024 ** 3, 'گیگابایت': 1024 ** 3, 'tb': 1024 ** 4, 'terabyte': 1024 ** 4, 'ترابایت': 1024 ** 4, 'pb': 1024 ** 5, 'petabyte': 1024 ** 5, 'bit': 0.125, 'بیت': 0.125, 'kbit': 128, 'mbit': 131072, 'gbit': 134217728}, 'time': {'s': 1, 'sec': 1, 'second': 1, 'seconds': 1, 'ثانیه': 1, 'm': 60, 'min': 60, 'minute': 60, 'minutes': 60, 'دقیقه': 60, 'h': 3600, 'hr': 3600, 'hour': 3600, 'hours': 3600, 'ساعت': 3600, 'd': 86400, 'day': 86400, 'days': 86400, 'روز': 86400, 'w': 604800, 'week': 604800, 'هفته': 604800, 'mo': 2592000, 'month': 2592000, 'ماه': 2592000, 'y': 31536000, 'year': 31536000, 'سال': 31536000}}

def _find_category(unit):
    """پیدا کردن دسته یه واحد"""
    u = unit.lower().strip()
    for cat, units in UNITS.items():
        if u in units:
            return cat
    return None

def _convert(value, from_unit, to_unit):
    """تبدیل"""
    f = from_unit.lower().strip()
    t = to_unit.lower().strip()
    temp_units = {'c', 'celsius', 'سلسیوس', 'سانتی\u200cگراد', 'f', 'fahrenheit', 'فارنهایت', 'k', 'kelvin', 'کلوین'}
    if f in temp_units or t in temp_units:
        return _convert_temp(value, f, t)
    cat_f = _find_category(f)
    cat_t = _find_category(t)
    if not cat_f:
        return (None, f'واحد مبدأ نامعتبر: `{from_unit}`')
    if not cat_t:
        return (None, f'واحد مقصد نامعتبر: `{to_unit}`')
    if cat_f != cat_t:
        return (None, f'واحدها از یک دسته نیستن ({cat_f} ≠ {cat_t})')
    factor_f = UNITS[cat_f][f]
    factor_t = UNITS[cat_t][t]
    result = value * factor_f / factor_t
    return (result, None)

def _convert_temp(value, f, t):
    """تبدیل دما"""
    if f in ('c', 'celsius', 'سلسیوس', 'سانتی\u200cگراد'):
        c = value
    elif f in ('f', 'fahrenheit', 'فارنهایت'):
        c = (value - 32) * 5 / 9
    elif f in ('k', 'kelvin', 'کلوین'):
        c = value - 273.15
    else:
        return (None, f'واحد دما نامعتبر: `{f}`')
    if t in ('c', 'celsius', 'سلسیوس', 'سانتی\u200cگراد'):
        return (c, None)
    elif t in ('f', 'fahrenheit', 'فارنهایت'):
        return (c * 9 / 5 + 32, None)
    elif t in ('k', 'kelvin', 'کلوین'):
        return (c + 273.15, None)
    else:
        return (None, f'واحد دما نامعتبر: `{t}`')

def _fmt_result(n):
    """فرمت عدد"""
    if n == int(n):
        return f'{int(n):,}'
    return f'{n:,.6f}'.rstrip('0').rstrip('.')

async def handler(client, message):
    parts = (message.text or '').split()
    if len(parts) < 5:
        return await message.reply_text('📏 **Unit Converter**\n\n**فرمت:** `/unit 10 km to m`\n\n**دسته\u200cها:**\n• طول: m, km, cm, mm, mi, ft, in, yd\n• وزن: kg, g, mg, lb, oz, ton\n• حجم: l, ml, gal, qt, pt, cup\n• مساحت: m2, km2, ha, acre, ft2\n• سرعت: m/s, km/h, mph, knot\n• داده: b, kb, mb, gb, tb\n• زمان: s, m, h, d, w, mo, y\n• دما: c, f, k\n\nمثال: `/unit 5 gb to mb`\nفارسی: `/unit 3 کیلومتر به متر`')
    try:
        value = float(parts[1])
    except ValueError:
        return await message.reply_text('❌ مقدار باید عدد باشه')
    from_u = parts[2]
    connector = parts[3].lower()
    to_u = parts[4]
    if connector not in ('to', 'in', 'به'):
        return await message.reply_text('❌ کلمه اتصال باید `to` یا `in` یا `به` باشه')
    result, err = _convert(value, from_u, to_u)
    if err:
        return await message.reply_text(f'❌ {err}')
    await message.reply_text(f'📏 **تبدیل واحد**\n\n🔢 **مقدار:** `{_fmt_result(value)} {from_u}`\n\n✅ **نتیجه:**\n`{_fmt_result(result)} {to_u}`')

async def list_handler(client, message):
    lines = ['📏 **واحدهای پشتیبانی\u200cشده**\n']
    cat_names = {'length': '📐 طول', 'weight': '⚖️ وزن', 'volume': '🧴 حجم', 'area': '📦 مساحت', 'speed': '🏎 سرعت', 'digital': '💾 داده', 'time': '⏱ زمان'}
    for cat, name in cat_names.items():
        units = list(UNITS[cat].keys())[:8]
        lines.append(f'\n**{name}:**')
        lines.append(f'`{', '.join(units)}`')
    lines.append('\n🌡 **دما:** `c, f, k`')
    lines.append('\n💡 `/unit 10 km to m`')
    await message.reply_text('\n'.join(lines))

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('unit', prefixes='/.')), group=0)
    client.add_handler(MessageHandler(list_handler, filters.me & filters.command('units', prefixes='/.')), group=0)
