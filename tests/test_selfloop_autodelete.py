"""Regression tests: per-slot auto-delete of own message / next bot message,
only in groups where the account may delete messages."""
import asyncio
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyrogram.enums import ChatMemberStatus, ChatType
from self_tools import selfloop as sl


class DM:
    def __init__(self):
        self.d = {}

    def get_user_data(self, u):
        return self.d.setdefault(u, {})

    def update_user_data(self, u, up):
        self.d.setdefault(u, {}).update(up)


class FakeClient:
    def __init__(self, status=ChatMemberStatus.ADMINISTRATOR, can_delete=True, uid=7):
        self.me = types.SimpleNamespace(id=uid)
        self.status, self.can_delete = status, can_delete
        self.deleted = []
        self.member_calls = 0
        self.fail_delete = None

    async def get_chat_member(self, chat_id, who):
        self.member_calls += 1
        priv = types.SimpleNamespace(can_delete_messages=self.can_delete)
        return types.SimpleNamespace(status=self.status, privileges=priv)

    async def delete_messages(self, chat_id, ids):
        if self.fail_delete:
            raise self.fail_delete
        self.deleted.append((chat_id, ids))


def reset():
    sl._WATCH.clear()
    sl._PERM_CACHE.clear()


def sent(msg_id, ctype=ChatType.SUPERGROUP):
    return types.SimpleNamespace(id=msg_id, chat=types.SimpleNamespace(type=ctype))


def botmsg(msg_id, chat_id=-100, reply_to=None, ctype=ChatType.SUPERGROUP):
    return types.SimpleNamespace(id=msg_id, reply_to_message_id=reply_to,
                                 chat=types.SimpleNamespace(id=chat_id, type=ctype))


async def main():
    CHAT = -100

    # 1) own: deleted immediately by admin with delete right
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {"del_own": True}, sent(10))
    assert c.deleted == [(CHAT, 10)], c.deleted

    # 2) owner is fine even without privileges object
    reset(); c = FakeClient(status=ChatMemberStatus.OWNER, can_delete=False)
    await sl._after_send(c, 7, CHAT, {"del_own": True}, sent(11))
    assert c.deleted == [(CHAT, 11)]

    # 3) admin WITHOUT delete right -> nothing deleted, nothing watched
    reset(); c = FakeClient(can_delete=False)
    await sl._after_send(c, 7, CHAT, {"del_own": True, "del_bot": True}, sent(12))
    assert c.deleted == [] and not sl._WATCH

    # 4) plain member -> nothing
    reset(); c = FakeClient(status=ChatMemberStatus.MEMBER)
    await sl._after_send(c, 7, CHAT, {"del_own": True}, sent(13))
    assert c.deleted == []

    # 5) private chat / channel -> nothing, and no permission API call needed
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {"del_own": True}, sent(14, ChatType.PRIVATE))
    assert c.deleted == [] and c.member_calls == 0

    # 6) flags off -> nothing
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {}, sent(15))
    assert c.deleted == [] and c.member_calls == 0

    # 7) bot only: our message stays, next bot message (no reply) is deleted once
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {"del_bot": True}, sent(20))
    assert c.deleted == [] and sl._WATCH[(7, CHAT)]
    await sl.bot_reply_handler(c, botmsg(21))
    assert c.deleted == [(CHAT, 21)]
    await sl.bot_reply_handler(c, botmsg(22))          # second bot msg: not ours anymore
    assert c.deleted == [(CHAT, 21)]

    # 8) both: own deleted + bot reply (reply_to ours) deleted
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {"del_own": True, "del_bot": True}, sent(30))
    await sl.bot_reply_handler(c, botmsg(31, reply_to=30))
    assert c.deleted == [(CHAT, 30), (CHAT, 31)], c.deleted

    # 9) bot message replying to SOMEONE ELSE's message is left alone
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {"del_bot": True}, sent(40))
    await sl.bot_reply_handler(c, botmsg(41, reply_to=3))
    assert c.deleted == []

    # 10) bot message older than ours / other chat is ignored
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {"del_bot": True}, sent(50))
    await sl.bot_reply_handler(c, botmsg(49))
    await sl.bot_reply_handler(c, botmsg(51, chat_id=-999))
    assert c.deleted == []

    # 11) expired watcher is ignored
    reset(); c = FakeClient()
    await sl._after_send(c, 7, CHAT, {"del_bot": True}, sent(60))
    sl._WATCH[(7, CHAT)] = [(60, 0.0)]
    await sl.bot_reply_handler(c, botmsg(61))
    assert c.deleted == []

    # 12) permission result is cached (one API call for many sends)
    reset(); c = FakeClient()
    for i in range(5):
        await sl._after_send(c, 7, CHAT, {"del_own": True}, sent(70 + i))
    assert c.member_calls == 1 and len(c.deleted) == 5

    # 13) delete failing with admin error flips cache to "no permission"
    reset(); c = FakeClient()
    class ChatAdminRequired(Exception): pass
    c.fail_delete = ChatAdminRequired()
    await sl._after_send(c, 7, CHAT, {"del_own": True}, sent(80))
    assert sl._PERM_CACHE[(7, CHAT)][1] is False

    # 14) delay option schedules deletion instead of deleting right now
    reset(); c = FakeClient()
    old = sl.asyncio.sleep
    async def fast_sleep(_): return None
    sl.asyncio.sleep = fast_sleep
    try:
        await sl._after_send(c, 7, CHAT, {"del_own": True, "del_delay": 3}, sent(90))
        assert c.deleted == []
        await old(0); await old(0)
        assert c.deleted == [(CHAT, 90)]
    finally:
        sl.asyncio.sleep = old

    # 15) arg parser
    assert sl._parse_del_args("2 own") == (2, "own", None)
    assert sl._parse_del_args("2: both 5") == (2, "both", 5)
    assert sl._parse_del_args("bot") == (1, "bot", None)
    assert sl._parse_del_args("3") == (3, None, None)
    for bad in ("2 nope", "9 own", "2 own 999", "2 own x"):
        try:
            sl._parse_del_args(bad); raise SystemExit("should fail: " + bad)
        except ValueError:
            pass

    # 16) /self_del persists per-slot flags; re-running /self_on keeps them
    reset(); dm = DM(); sl._G = {"data_manager": dm}
    c = FakeClient(); replies = []
    async def reply_text(t): replies.append(t)
    def msg(text):
        return types.SimpleNamespace(text=text, reply_text=reply_text,
                                     chat=types.SimpleNamespace(id=CHAT, type=ChatType.SUPERGROUP))
    sl._TASKS.clear()
    await sl.on_handler(c, msg("/self_on 2: 5m-7m یخچال میویی"))
    await sl.on_handler(c, msg("/self_on 1: 10m سلام"))
    await sl.del_handler(c, msg("/self_del 2 both"))
    cfg2 = dm.get_user_data(7)["self_loop"][str(CHAT)]["2"]
    cfg1 = dm.get_user_data(7)["self_loop"][str(CHAT)]["1"]
    assert cfg2["del_own"] and cfg2["del_bot"] and not cfg1.get("del_own")      # per-slot
    assert "✅" in replies[-1]
    await sl.on_handler(c, msg("/self_on 2: 6m-8m"))                             # re-config keeps flags
    assert dm.get_user_data(7)["self_loop"][str(CHAT)]["2"]["del_bot"]
    await sl.del_handler(c, msg("/self_del 2 off"))
    cfg2 = dm.get_user_data(7)["self_loop"][str(CHAT)]["2"]
    assert not cfg2.get("del_own") and not cfg2.get("del_bot")
    await sl.del_handler(c, msg("/self_del 4 own"))                              # slot not active
    assert "روشن نیست" in replies[-1]
    for t in list(sl._TASKS.values()): t.cancel()
    await asyncio.sleep(0)

    # 17) warning shown when no permission
    c2 = FakeClient(can_delete=False); sl._PERM_CACHE.clear()
    await sl.on_handler(c2, msg("/self_on 3: 5m-7m x"))
    await sl.del_handler(c2, msg("/self_del 3 own"))
    assert "⚠️" in replies[-1]
    for t in list(sl._TASKS.values()): t.cancel()
    await asyncio.sleep(0)

    # 18) registration
    class Reg:
        g = None
        def __init__(self): self.h = []
        def add_handler(self, h, group=0): self.h.append((h, group))
    r = Reg(); sl.register(r)
    assert (sl.bot_reply_handler, -20) in [(h.callback, g) for h, g in r.h]
    assert any(h.callback is sl.del_handler for h, _ in r.h)
    print("selfloop auto-delete: OK (18 checks)")

asyncio.run(main())
