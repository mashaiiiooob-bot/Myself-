import ast
import operator
from pyrogram import filters
from pyrogram.handlers import MessageHandler
SAFE_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
MAX_EXPR = 200
MAX_POW = 100
MAX_NUM = 10 ** 100
MAX_DIGITS = 200

def _norm(t):
    for i, d in enumerate('۰۱۲۳۴۵۶۷۸۹'):
        t = t.replace(d, '0123456789'[i])
    for i, d in enumerate('٠١٢٣٤٥٦٧٨٩'):
        t = t.replace(d, '0123456789'[i])
    return t.replace('×', '*').replace('÷', '/').replace('−', '-').replace('،', '').replace(',', '')

def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            if abs(node.value) > MAX_NUM:
                raise ValueError('عدد خیلی بزرگه')
            return node.value
        raise ValueError('فقط عدد مجازه')
    if isinstance(node, ast.BinOp):
        l, r = (_eval(node.left), _eval(node.right))
        op = type(node.op)
        if op not in SAFE_OPS:
            raise ValueError('عملگر غیرمجاز')
        if op == ast.Pow:
            if abs(r) > MAX_POW:
                raise ValueError('توان بزرگه')
            if abs(l) > 10 ** 10:
                raise ValueError('پایه بزرگه')
        if op in (ast.Div, ast.FloorDiv, ast.Mod) and r == 0:
            raise ValueError('تقسیم بر صفر')
        res = SAFE_OPS[op](l, r)
        if isinstance(res, (int, float)):
            if abs(res) > MAX_NUM:
                raise ValueError('نتیجه بزرگه')
            if isinstance(res, int) and len(str(abs(res))) > MAX_DIGITS:
                raise ValueError('ارقام زیاد')
        return res
    if isinstance(node, ast.UnaryOp):
        v = _eval(node.operand)
        op = type(node.op)
        if op not in SAFE_OPS:
            raise ValueError('عملگر غیرمجاز')
        return SAFE_OPS[op](v)
    raise ValueError('عبارت غیرمجاز')

def calculate(expr):
    expr = _norm(expr).strip()
    if len(expr) > MAX_EXPR:
        return (None, 'طولانی')
    if not expr:
        return (None, 'خالی')
    if not all((c in set('0123456789+-*/()% .') for c in expr)):
        return (None, 'کاراکتر غیرمجاز')
    try:
        tree = ast.parse(expr, mode='eval')
        return (_eval(tree.body), None)
    except SyntaxError as e:
        return (None, f'خطای نگارشی: {e.msg}')
    except ValueError as e:
        return (None, str(e))
    except ZeroDivisionError:
        return (None, 'تقسیم بر صفر')
    except Exception:
        return (None, 'خطا')

def _fmt(n):
    if isinstance(n, int):
        return f'{n:,}'
    if n.is_integer():
        return f'{int(n):,}'
    return f'{n:,.6f}'.rstrip('0').rstrip('.')

def _fa(t):
    r = str(t)
    for i, d in enumerate('0123456789'):
        r = r.replace(d, '۰۱۲۳۴۵۶۷۸۹'[i])
    return r

async def handler(client, message):
    parts = (message.text or '').strip().split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply_text('🧮 **Calculator**\n\n**فرمت:** `/calc 2+2`\n**عملگرها:** `+` `-` `*` `/` `//` `%` `**`')
    expr = parts[1]
    r, err = calculate(expr)
    if err:
        return await message.reply_text(f'❌ **خطا**\n`{expr}`\n⚠️ {err}')
    f = _fmt(r)
    await message.reply_text(f'🧮 **نتیجه**\n\n📝 `{expr}`\n\n✅ **{f}**\n\n🇮🇷 `{_fa(f)}`')

def register(client):
    client.add_handler(MessageHandler(handler, filters.me & filters.command('calc', prefixes='/.')), group=0)
