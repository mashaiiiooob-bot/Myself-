import os
import time
from pyrogram import filters
from pyrogram.handlers import MessageHandler
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_OK = True
except ImportError:
    PIL_OK = False

def _parse_exif(img):
    """استخراج EXIF"""
    exif_data = {}
    try:
        exif = img._getexif()
        if exif:
            for tid, val in exif.items():
                tag = TAGS.get(tid, tid)
                if tag == 'GPSInfo':
                    gps = {}
                    for gid, gval in val.items():
                        gps[GPSTAGS.get(gid, gid)] = gval
                    exif_data['GPSInfo'] = gps
                else:
                    exif_data[tag] = val
    except Exception:
        pass
    return exif_data

def _gps_to_deg(gps_data):
    """تبدیل GPS به مختصات"""
    try:

        def to_deg(values):
            d, m, s = values
            return float(d) + float(m) / 60 + float(s) / 3600
        lat = to_deg(gps_data.get('GPSLatitude', [0, 0, 0]))
        lon = to_deg(gps_data.get('GPSLongitude', [0, 0, 0]))
        if gps_data.get('GPSLatitudeRef') == 'S':
            lat = -lat
        if gps_data.get('GPSLongitudeRef') == 'W':
            lon = -lon
        return (lat, lon)
    except Exception:
        return (None, None)

async def handler(client, message):
    if not PIL_OK:
        return await message.reply_text('❌ `pip install Pillow`')
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text('📌 روی یه عکس ریپلای کن')
    args = (message.text or '').split()
    arg = args[1].lower() if len(args) > 1 else ''
    status = await message.reply_text('📄 در حال تحلیل...')
    path = None
    try:
        path = await message.reply_to_message.download()
        img = Image.open(path)
        if arg == 'strip':
            size_before = os.path.getsize(path)
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.jpg', '.jpeg'):
                clean = img.convert('RGB') if img.mode != 'RGB' else img.copy()
                out = path + '_clean.jpg'
                clean.save(out, 'JPEG', quality=95)
            else:
                clean = img.copy()
                clean.info = {}
                out = path + '_clean.png'
                clean.save(out, 'PNG', optimize=True)
            size_after = os.path.getsize(out)
            diff = size_before - size_after
            pct = diff / size_before * 100 if size_before else 0
            await message.reply_document(out, caption=f'🧹 **متادیتا پاک شد**\n\n📦 قبل: `{size_before:,}` B\n📦 بعد: `{size_after:,}` B\n📉 کاهش: `{diff:,}` B (`{pct:.1f}%`)')
            await status.delete()
            return
        exif = _parse_exif(img)
        if arg == 'find' and len(args) > 2:
            kw = args[2].lower()
            found = []
            for k, v in exif.items():
                if kw in str(k).lower() or kw in str(v).lower():
                    found.append(f'• **{k}:** `{str(v)[:80]}`')
            if found:
                await status.edit_text(f'🔍 **نتایج `{kw}`:**\n\n' + '\n'.join(found[:20]))
            else:
                await status.edit_text(f'❌ چیزی پیدا نشد برای `{kw}`')
            return
        lines = ['╔══════════════════════════╗', '║   📄 IMAGE METADATA     ║', '╚══════════════════════════╝', '', '📦 **اطلاعات پایه:**', f'• فرمت: `{img.format or '-'}`', f'• ابعاد: `{img.width} × {img.height}`', f'• حالت رنگ: `{img.mode}`', f'• حجم: `{os.path.getsize(path):,}` bytes']
        if hasattr(img, 'icc_profile') and img.icc_profile:
            lines.append(f'• پروفایل رنگ: `دارد ({len(img.icc_profile)} B)`')
        if exif:
            lines.append('\n📊 **EXIF:**')
            important = ['Make', 'Model', 'Software', 'DateTime', 'DateTimeOriginal', 'DateTimeDigitized', 'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength', 'Flash', 'Orientation', 'WhiteBalance', 'MeteringMode', 'ExposureProgram']
            for key in important:
                if key in exif:
                    lines.append(f'• {key}: `{str(exif[key])[:60]}`')
            if 'GPSInfo' in exif:
                lat, lon = _gps_to_deg(exif['GPSInfo'])
                if lat and lon:
                    lines.append(f'\n📍 **GPS:**')
                    lines.append(f'• مختصات: `{lat:.6f}, {lon:.6f}`')
                    lines.append(f'• [مشاهده نقشه](https://www.openstreetmap.org/?mlat={lat}&mlon={lon})')
            if arg == 'raw':
                lines.append('\n📋 **همه EXIF:**')
                for k, v in exif.items():
                    if k != 'GPSInfo':
                        lines.append(f'• {k}: `{str(v)[:80]}`')
            if hasattr(img, 'info'):
                extra = {k: v for k, v in img.info.items() if k not in ('exif', 'icc_profile')}
                if extra and arg == 'raw':
                    lines.append('\n📁 **اطلاعات فایل:**')
                    for k, v in extra.items():
                        lines.append(f'• {k}: `{str(v)[:60]}`')
        else:
            lines.append('\nℹ️ EXIF ندارد')
        text = '\n'.join(lines)
        lines_arr = text.split('\n')
        if len(lines_arr) > 40:
            text = '\n'.join(lines_arr[:40]) + f'\n\n_... و {len(lines_arr) - 40} خط دیگر_'
        await status.edit_text(text[:4000], disable_web_page_preview=True)
    except Exception as e:
        await status.edit_text(f'❌ خطا: `{e}`')
    finally:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
        try:
            for f in os.listdir(os.path.dirname(path)):
                if os.path.basename(path) + '_clean' in f:
                    os.remove(os.path.join(os.path.dirname(path), f))
        except Exception:
            pass

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('imgmeta', prefixes=['/', '.'])), group=0)
