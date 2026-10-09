"""
Self tools package: ~40 commands (prefix `/` or `.`), e.g. /calc 2+2, /qr text, /font hello.

register_all(client, g=None) loads every module independently: one broken/missing module
never prevents the others (or the bot) from working.
"""
import importlib
import logging

log = logging.getLogger(__name__)

MODULES = [
    "calc", "uuid", "count_age", "qr", "tr", "date", "bmi", "hash", "json_fmt", "base64_tool",
    "stats", "remind", "passgen", "pray", "tz", "short", "unit", "imgmeta",
    "ip", "weather", "crypto", "price", "wiki", "ai", "image", "voice", "ocr", "removebg",
    "userinfo", "chatinfo", "checkuser", "font", "ascii_art", "sumfix",
]


class _Registrar:
    """Wraps a Pyrogram client so every tool handler runs in its own early group and
    is silent while the self is switched off (SELF_ACTIVE_STATUS)."""

    def __init__(self, client, g, group):
        self._c, self._g, self._group = client, g or {}, group

    def __getattr__(self, name):
        return getattr(self._c, name)

    def add_handler(self, handler, group=0):
        cb = handler.callback
        status = self._g.get("SELF_ACTIVE_STATUS")
        client = self._c

        async def guarded(c, m):
            try:
                if status is not None and not status.get(client.me.id, True):
                    return
            except Exception:
                pass
            return await cb(c, m)

        handler.callback = guarded
        return self._c.add_handler(handler, group=self._group)


def register_all(client, g=None, group=-6):
    reg = _Registrar(client, g, group)
    ok, failed = 0, []
    for name in MODULES:
        try:
            mod = importlib.import_module(f"{__name__}.{name}")
            mod.register(reg)
            ok += 1
        except Exception as e:  # keep going
            failed.append(f"{name}: {type(e).__name__}: {e}")
    if failed:
        log.warning("self_tools: %d modules skipped: %s", len(failed), "; ".join(failed))
    log.info("self_tools: %d tools registered", ok)
    return ok
