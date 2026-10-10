import re
from pyrogram import filters
from pyrogram.handlers import MessageHandler

_FA = "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩"
_NUM = re.compile(r"-?\d+(?:[.,٫]\d+)?")


def _src(message):
    parts = (message.text or "").split(maxsplit=1)
    arg = parts[1] if len(parts) > 1 else ""
    if not arg.strip() and message.reply_to_message:
        arg = message.reply_to_message.text or message.reply_to_message.caption or ""
    return arg


def numbers(text):
    t = text.translate(str.maketrans(_FA, "0123456789" * 2)).replace("٬", "").replace("،", " ")
    out = []
    for m in _NUM.findall(t):
        try:
            out.append(float(m.replace(",", ".").replace("٫", ".")))
        except ValueError:
            pass
    return out


def _fmt(x):
    return f"{int(x):,}" if float(x).is_integer() else f"{x:,.6f}".rstrip("0").rstrip(".")


async def sum_handler(client, message):
    nums = numbers(_src(message))[:500]
    if not nums:
        return await message.reply_text("**فرمت:** `/sum 10 20 30` یا روی پیامی با چند عدد ریپلای کن.")
    await message.reply_text(f"➕ **جمع:** `{_fmt(sum(nums))}`\n🔢 تعداد: {len(nums)}\n📊 میانگین: `{_fmt(sum(nums) / len(nums))}`\n⬇️ کمترین: `{_fmt(min(nums))}`   ⬆️ بیشترین: `{_fmt(max(nums))}`")


_EN = "qwertyuiop[]asdfghjkl;'zxcvbnm,"
_FAK = "ضصثقفغعهخحجچشسیبلاتنمکگظطزرذدپو"
_E2F = dict(zip(_EN, _FAK))
_F2E = dict(zip(_FAK, _EN))


def fix_layout(text):
    letters = [c for c in text if c.isalpha()]
    latin = sum(1 for c in letters if c.isascii())
    mp = _E2F if letters and latin >= len(letters) / 2 else _F2E
    return "".join(mp.get(c.lower(), c) for c in text), (mp is _E2F)


async def fix_handler(client, message):
    text = _src(message).strip()
    if not text:
        return await message.reply_text("**فرمت:** `/fix متن` یا ریپلای روی متنی که با زبان کیبورد اشتباه نوشته شده.")
    out, to_fa = fix_layout(text[:2000])
    await message.reply_text(f"⌨️ **{'انگلیسی ← فارسی' if to_fa else 'فارسی ← انگلیسی'}**\n\n{out}")


def register(client):
    client.add_handler(MessageHandler(sum_handler, filters.me & filters.command("sum", prefixes=["/", "."])), group=0)
    client.add_handler(MessageHandler(fix_handler, filters.me & filters.command("fix", prefixes=["/", "."])), group=0)
