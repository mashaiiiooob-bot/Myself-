"""Regression test: /self_on supports multiple independent slots per chat (N: syntax)."""
import asyncio
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import self_tools


class DM:
    def __init__(self):
        self.d = {}

    def get_user_data(self, u):
        return self.d.setdefault(u, {})

    def update_user_data(self, u, up):
        self.d.setdefault(u, {}).update(up)


class Client:
    def __init__(self, uid=7):
        self.handlers = []
        self.me = types.SimpleNamespace(id=uid)
        self.sent = []

    def add_handler(self, h, group=0):
        self.handlers.append((h, group))

    async def send_message(self, cid, text):
        self.sent.append((cid, text))


def _commands(client):
    out = {}

    def walk(flt):
        found = set()
        for attr in ("base", "other"):
            f = getattr(flt, attr, None)
            if f is not None:
                found |= walk(f)
        cs = getattr(flt, "commands", None)
        if cs:
            found |= set(cs)
        return found

    for h, _ in client.handlers:
        for name in walk(h.filters):
            out[name] = h.callback
    return out


class Msg:
    def __init__(self, text, chat=1):
        self.text = text
        self.out = []
        self.chat = types.SimpleNamespace(id=chat)

    async def reply_text(self, t, **k):
        self.out.append(t)
        return self


async def _run():
    dm = DM()
    client = Client()
    self_tools.register_all(client, {"SELF_ACTIVE_STATUS": {}, "data_manager": dm})
    cmds = _commands(client)
    await asyncio.sleep(0.05)

    m1 = Msg("/self_on")
    await cmds["self_on"](client, m1)
    assert "اسلات 1" in m1.out[0] and "میو" in m1.out[0], m1.out

    m2 = Msg("/self_on 2: 2m یخچال میویی")
    await cmds["self_on"](client, m2)
    assert "اسلات 2" in m2.out[0] and "یخچال میویی" in m2.out[0], m2.out

    ms = Msg("/self_status")
    await cmds["self_status"](client, ms)
    assert "اسلات 1" in ms.out[0] and "اسلات 2" in ms.out[0], ms.out

    dm.d[7]["self_loop"]["1"]["1"]["interval"] = 1
    dm.d[7]["self_loop"]["1"]["2"]["interval"] = 1
    await asyncio.sleep(1.3)
    assert sorted(client.sent) == [(1, "میو"), (1, "یخچال میویی")], client.sent

    moff = Msg("/self_off 2")
    await cmds["self_off"](client, moff)
    assert "اسلات 2 خاموش" in moff.out[0], moff.out
    client.sent.clear()

    moffall = Msg("/self_off")
    await cmds["self_off"](client, moffall)
    assert "اسلات" in moffall.out[0], moffall.out

    for t in list(self_tools.selfloop._TASKS.values()):
        t.cancel()
    print("selfloop multi-slot regression: OK")


if __name__ == "__main__":
    asyncio.run(_run())
