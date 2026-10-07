"""Mini-app API for the DarkSelf bot.  Usage, inside the bot file after the loop is running:

    import miniapp_api
    asyncio.create_task(miniapp_api.start(globals()))

Env: MINIAPP_PORT (default 8080), MINIAPP_ORIGIN (CORS origin of the page, default *).
Every call is authenticated with Telegram's initData (HMAC with BOT_TOKEN / PREMIUM_BOT_TOKEN)."""
import asyncio, hashlib, hmac, json, os, time
from urllib.parse import parse_qsl
from aiohttp import web

# settings key -> (dict name in the bot, default).  Same pairs as the panel's tg_* callbacks.
T = {
 'clock': ('CLOCK_STATUS', False), 'bio_clock': ('BIO_CLOCK_STATUS', False), 'bio_date': ('BIO_DATE_STATUS', False),
 'avatar': ('AVATAR_STATUS', False), 'panel_color': ('PANEL_COLOR_STATUS', True), 'help_color': ('HELP_COLOR_STATUS', True),
 'bold': ('BOLD_MODE_STATUS', False), 'spoiler': ('SPOILER_MODE_STATUS', False), 'code': ('CODE_MODE_STATUS', False),
 'underline': ('UNDERLINE_MODE_STATUS', False), 'gradual': ('GRADUAL_MODE_STATUS', False), 'pemoji': ('PEMOJI_STATUS', False),
 'dot_commands': ('DOT_COMMANDS_STATUS', False), 'tag_alert': ('TAG_ALERT_STATUS', False),
 'filter_words_active': ('FILTER_WORDS_ACTIVE', False), 'anti_delete': ('ANTI_DELETE_STATUS', False),
 'anti_edit': ('ANTI_EDIT_STATUS', False), 'self_destruct': ('SELF_DESTRUCT_STATUS', False),
 'secretary': ('SECRETARY_MODE_STATUS', False), 'first_comment': ('FIRST_COMMENT_STATUS', False),
 'auto_seen': ('AUTO_SEEN_STATUS', False), 'auto_save': ('AUTO_SAVE_VIEW_ONCE', False),
 'forced_join_active': ('FORCED_JOIN_ACTIVE', False),
 'typing': ('TYPING_MODE_STATUS', False), 'playing': ('PLAYING_MODE_STATUS', False),
 'upload_photo': ('UPLOAD_PHOTO_STATUS', False), 'record_voice': ('RECORD_VOICE_STATUS', False),
 'watch_gif': ('WATCH_GIF_STATUS', False),
 'tabchi_pv': ('TABCHI_PV_STATUS', False), 'tabchi_gp': ('TABCHI_GP_STATUS', False), 'tabchi_smart': ('TABCHI_SMART_STATUS', False),
 'enemy_active': ('ENEMY_ACTIVE', False), 'friend_active': ('FRIEND_ACTIVE', False), 'crash_active': ('CRASH_ACTIVE', False),
 'pv_lock': ('PV_LOCK_STATUS', False), 'pv_photo': ('PV_PHOTO_LOCK', False), 'pv_video': ('PV_VIDEO_LOCK', False),
 'pv_gif': ('PV_GIF_LOCK', False), 'pv_voice': ('PV_VOICE_LOCK', False), 'pv_music': ('PV_MUSIC_LOCK', False),
 'pv_sticker': ('PV_STICKER_LOCK', False), 'pv_loc': ('PV_LOC_LOCK', False), 'pv_emo': ('PV_EMO_LOCK', False),
 'pv_txt': ('PV_TXT_LOCK', False),
}
CYC = {'font': ('USER_FONT_CHOICES', 'stylized'), 'bio_font': ('BIO_FONT_CHOICE', 'stylized'),
       'bio_date_type': ('BIO_DATE_TYPE', 'jalali'), 'tabchi_speed': ('TABCHI_SPEED', 'medium')}
TEXT_EXCL = ['bold', 'spoiler', 'code', 'underline', 'gradual']          # mutually exclusive
ACT_EXCL = ['typing', 'playing', 'upload_photo', 'record_voice', 'watch_gif']
NEEDS_BANNER = ('tabchi_pv', 'tabchi_gp', 'tabchi_smart')
TR = {'off': None, 'en': 'en', 'ru': 'ru', 'zh-CN': 'zh-CN'}


def _auth(g, init):
    """Validate Telegram initData; return user id or None."""
    try:
        d = dict(parse_qsl(init, keep_blank_values=True))
        got = d.pop('hash', '')
        if not got or time.time() - int(d.get('auth_date', 0)) > 86400:
            return None
        chk = '\n'.join(f'{k}={v}' for k, v in sorted(d.items()))
        for tok in (g.get('BOT_TOKEN'), g.get('PREMIUM_BOT_TOKEN')):
            if not tok:
                continue
            key = hmac.new(b'WebAppData', tok.encode(), hashlib.sha256).digest()
            if hmac.compare_digest(hmac.new(key, chk.encode(), hashlib.sha256).hexdigest(), got):
                return int(json.loads(d['user'])['id'])
    except Exception:
        pass
    return None


def _is_admin(g, uid):
    return uid == g['ROOT_ADMIN'] or uid in g['data_manager'].get_admins()


def _user(g, uid):
    return g['data_manager'].data.get('users', {}).get(str(uid), {})


def _settings(g, uid):
    out = {}
    for k, (name, dflt) in T.items():
        out[k] = bool(g[name].get(uid, dflt)) if name in g else dflt
    for k, (name, dflt) in CYC.items():
        out[k] = g[name].get(uid, dflt) if name in g else dflt
    out['translate'] = g['AUTO_TRANSLATE_TARGET'].get(uid) if 'AUTO_TRANSLATE_TARGET' in g else None
    return out


async def _toggle(g, uid, key, val):
    """Mirror of the panel's tg_* callbacks. Returns (changes, error)."""
    s = {}
    cli = (g['ACTIVE_BOTS'].get(uid) or [None])[0]
    spawn = asyncio.create_task
    if key in CYC:
        name, dflt = CYC[key]
        cur = g[name].get(uid, dflt)
        if key in ('font', 'bio_font'):
            order = g['FONT_KEYS_ORDER']; cur = cur if cur in order else 'stylized'
            new = order[(order.index(cur) + 1) % len(order)]
        elif key == 'bio_date_type':
            new = 'gregorian' if cur == 'jalali' else 'jalali'
        else:
            new = {'medium': 'fast', 'fast': 'slow'}.get(cur, 'medium')
        g[name][uid] = s[key] = new
        if cli and key == 'font' and g['CLOCK_STATUS'].get(uid):
            spawn(g['perform_clock_update_now'](cli, uid))
        if cli and key in ('bio_font', 'bio_date_type'):
            spawn(g['perform_bio_update_now'](cli, uid))
        if key == 'tabchi_speed':
            g['ensure_tabchi_loops_running'](uid)
        return s, None
    if key == 'translate':
        new = TR.get(val)
        g['AUTO_TRANSLATE_TARGET'][uid] = s['translate'] = None if g['AUTO_TRANSLATE_TARGET'].get(uid) == new else new
        return s, None
    if key not in T:
        return {}, 'کلید نامعتبر'
    name, dflt = T[key]
    new = not g[name].get(uid, dflt)
    # same guards as the panel
    if key == 'first_comment' and not g['FIRST_COMMENT_TEXT'].get(uid, '').strip():
        return {}, 'اول متن کامنت اول را با دستور «تنظیم متن کامنت اول ...» تنظیم کنید.'
    if key == 'forced_join_active' and not g['FORCED_JOIN_CHATS'].get(uid):
        return {}, 'ابتدا با دستور «تنظیم عضویت اجباری @یوزرنیم» یک کانال ثبت کنید.'
    if key in NEEDS_BANNER and new and not (g['TABCHI_BANNER'].get(uid) or g['TABCHI_BANNER_MEDIA'].get(uid)):
        return {}, 'ابتدا بنر را با دستور «تنظیم بنر [متن]» تنظیم کنید.'
    for k2, lst in (('enemy_active', 'ENEMY_LIST'), ('friend_active', 'FRIEND_LIST'), ('crash_active', 'CRASH_LIST')):
        if key == k2 and new and not g[lst].get(uid):
            return {}, 'اول باید یک نفر را به این لیست اضافه کنید (ریپلای + دستور تنظیم).'
    g[name][uid] = s[key] = new
    if key in TEXT_EXCL and new:
        for o in TEXT_EXCL:
            if o != key:
                g[T[o][0]][uid] = s[o] = False
    if key in ACT_EXCL and new:
        for o in ACT_EXCL:
            if o != key:
                g[T[o][0]][uid] = s[o] = False
    if key == 'clock':
        s['clock_manual'] = True
        if cli and new:
            spawn(g['perform_clock_update_now'](cli, uid))
    if key in ('bio_clock', 'bio_date') and cli:
        spawn(g['perform_bio_update_now'](cli, uid))
    if key == 'avatar' and cli:
        if new:
            g['AVATAR_STAMP'].pop(uid, None); spawn(g['_av_apply'](cli, uid))
        else:
            spawn(g['_av_clear'](cli, uid))
    if key == 'secretary' and new:
        g['USERS_REPLIED_IN_SECRETARY'][uid] = set()
        g['data_manager'].update_user_data(uid, {'replied_users': []})
    if key in NEEDS_BANNER:
        if new:
            for c in ('TABCHI_PV_COUNT', 'TABCHI_GP_COUNT'):
                g[c][uid] = 0
        g['ensure_tabchi_loops_running'](uid)
    return s, None


# settings key used in data_manager (differs from the dict-key for a few entries)
SAVE = {'auto_seen': 'auto_seen', 'dot_commands': 'dot_commands', 'tag_alert': 'tag_alert', 'pv_lock': 'pv_lock',
        'filter_words_active': 'filter_words_active', 'forced_join_active': 'forced_join_active'}


def make_app(g):
    dm = g['data_manager']

    def cors(r):
        r.headers['Access-Control-Allow-Origin'] = os.environ.get('MINIAPP_ORIGIN', '*')
        r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        r.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return r

    def handler(fn):
        async def h(req):
            if req.method == 'OPTIONS':
                return cors(web.Response())
            try:
                body = await req.json()
            except Exception:
                body = {}
            uid = _auth(g, body.get('initData', ''))
            if not uid:
                return cors(web.json_response({'ok': False}, status=401))
            try:
                return cors(web.json_response(await fn(uid, body)))
            except Exception as e:                                   # never leak internals
                return cors(web.json_response({'ok': False, 'err': 'خطای داخلی'}, status=500))
        return h

    async def state(uid, b):
        ud = _user(g, uid)
        has = bool(ud.get('session_string'))
        running = uid in g['ACTIVE_BOTS'] and dm.data.get('global_bot_status', True)
        phone = str(ud.get('phone') or '')
        me = getattr(g.get('manager_bot'), 'me', None)
        return {'ok': True, 'uid': uid, 'has': has, 'running': running,
                'self_active': bool(g.get('SELF_ACTIVE_STATUS', {}).get(uid, True)),
                'account': 'active' if uid in g['ACTIVE_BOTS'] else ('pending' if has else 'none'),
                'admin': _is_admin(g, uid), 'bot': getattr(me, 'username', '') or '',
                'phone': ('•••• ' + phone[-4:]) if len(phone) >= 4 else '',
                'links': {'channel': g.get('MENU_CHANNEL_URL', ''), 'support': g.get('MENU_SUPPORT_URL', '')},
                'settings': _settings(g, uid)}

    async def setv(uid, b):
        if uid not in g['ACTIVE_BOTS']:
            return {'ok': False, 'err': 'سلف شما روشن نیست.'}
        if g['_activation_wait_left'](uid) > 0:
            return {'ok': False, 'err': 'فعال‌سازی در انتظار است؛ کمی بعد دوباره امتحان کنید.'}
        s, err = await _toggle(g, uid, b.get('key'), b.get('val'))
        if err:
            return {'ok': False, 'err': err, 'settings': _settings(g, uid)}
        if s:
            dm.update_user_data(uid, {'settings': s})
            g['_commit_and_broadcast_shards']('miniapp-settings')
        return {'ok': True, 'settings': _settings(g, uid)}

    async def admin(uid, b):
        if not _is_admin(g, uid):
            return {'ok': False, 'err': 'دسترسی غیرمجاز'}
        op = b.get('op')
        if op == 'g_fjoin':
            dm.data['global_fjoin_active'] = not dm.data.get('global_fjoin_active', False); dm.save_data()
        elif op == 'g_bot':
            if uid != g['ROOT_ADMIN']:
                return {'ok': False, 'err': 'فقط مالک اصلی'}
            new = not dm.data.get('global_bot_status', True)
            dm.data['global_bot_status'] = new; dm.save_data()
            if not new:
                async def stop(c, ts):
                    for t in ts:
                        try: t.cancel()
                        except Exception: pass
                    try: await c.stop()
                    except Exception: pass
                await asyncio.gather(*[stop(c, ts) for _, (c, ts) in list(g['ACTIVE_BOTS'].items())], return_exceptions=True)
                g['ACTIVE_BOTS'].clear()
            else:
                for phone, sd in list(dm.get_all_sessions()):
                    asyncio.create_task(g['start_bot_instance'](sd['string'], phone, sd['user_id'], 'stylized'))
                    await asyncio.sleep(0.12)
        elif op == 'limit_set':
            if uid != g['ROOT_ADMIN']:
                return {'ok': False, 'err': 'فقط مالک اصلی'}
            dm.set_self_limit(b.get('n', 0))
        elif op == 'admins':
            return {'ok': True, 'admins': list(dm.get_admins())}
        elif op == 'users':
            us = [{'id': int(k), 'name': (v.get('first_name') or v.get('username') or ''), 'running': int(k) in g['ACTIVE_BOTS']}
                  for k, v in dm.data.get('users', {}).items() if v.get('session_string') or v.get('phone')]
            return {'ok': True, 'users': us[:200]}
        limit, used, free = dm.self_limit_status()
        try:
            stats = '\n'.join(l.replace('*', '').replace('`', '') for l in g['get_server_stats_text']().split('\n'))
        except Exception:
            stats = ''
        return {'ok': True, 'total': len(dm.get_all_users()), 'running': len(g['ACTIVE_BOTS']),
                'global_on': dm.data.get('global_bot_status', True), 'fjoin_on': dm.data.get('global_fjoin_active', False),
                'limit': limit, 'used': used, 'free': free, 'stats': stats}

    app = web.Application()
    for p, fn in (('state', state), ('set', setv), ('admin', admin)):
        app.router.add_route('*', '/miniapp/' + p, handler(fn))
    return app


async def start(g):
    app = make_app(g)
    page_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'miniapp', 'dashboard', 'index.html')

    async def page(req):
        try:
            with open(page_path, encoding='utf-8') as f:
                html = f.read()
        except OSError:
            return web.Response(text='dashboard not found', status=404)
        me = getattr(g.get('manager_bot'), 'me', None)
        html = html.replace('__BOT__', getattr(me, 'username', '') or '').replace('__API__', os.environ.get('MINIAPP_PUBLIC_URL', '').rstrip('/'))
        return web.Response(text=html, content_type='text/html', headers={'Cache-Control': 'no-store'})

    async def health(req):
        return web.json_response({'ok': True})

    app.router.add_get('/', page)
    app.router.add_get('/app', page)
    app.router.add_get('/healthz', health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('MINIAPP_PORT') or os.environ.get('PORT') or 8080)
    await web.TCPSite(runner, '0.0.0.0', port).start()
    return runner
