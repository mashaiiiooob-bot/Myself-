import asyncio, sys, types, logging, ast, re
import os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pyrogram import Client, filters, enums
from pyrogram.types import Message, User, Chat
logger=logging.getLogger("t")
import self_tools
def cmds(flt):
    out=set()
    for a in ('base','other'):
        f=getattr(flt,a,None)
        if f is not None: out|=cmds(f)
    cs=getattr(flt,'commands',None)
    if cs: out|=set(cs)
    return out
async def main():
    c=Client("t",api_id=1,api_hash="a",in_memory=True)
    c.me=User(id=7,is_self=True,first_name="Me",username="me_user")
    class DM:
        def __init__(s): s.d={}
        def get_user_data(s,u): return s.d.setdefault(u,{})
        def update_user_data(s,u,up): s.d.setdefault(u,{}).update(up)
    n=self_tools.register_all(c,{'SELF_ACTIVE_STATUS':{},'data_manager':DM()})
    await asyncio.sleep(0.1)
    hs=[h for g in c.dispatcher.groups.values() for h in g]
    names=sorted({x for h in hs for x in cmds(h.filters)})
    chat=Chat(id=7,type=enums.ChatType.PRIVATE,first_name="Me")
    def mk(text,out=True): return Message(id=1,client=c,text=text,outgoing=out,from_user=c.me,chat=chat)
    bad=[]
    for name in names:
        for pre in ("/","."):
            m=mk(f"{pre}{name} test")
            hit=[h for h in hs if await h.check(c,m)]
            if len(hit)!=1: bad.append((pre+name,len(hit)))
    m=mk("/calc 2+2",out=False); inc=[h for h in hs if await h.check(c,m)]
    print("registered",n,"| commands",len(names),"| prefix mismatches:",bad,"| incoming matched (must be 0):",len(inc))
    # run real callbacks through the real filter
    replies=[]
    samples=["/calc 2+2","/uuid",".count سلام","/bmi 175 70","/sha256 hi","/b64e hi","/passgen 12","/unit 10 km mi","/units","/tzlist","/sum 1 2 3","/fix ghfd","/font hi","/ascii Hi","/checkuser abcde","/qr hello","/date","/age 1990/5/20","/json {\"a\":1}","/prompt","/stats hello","/tz Tehran"]
    ok=0
    for t in samples:
        m=mk(t); out=[]
        async def rt(text,*a,**k): out.append(text); return m
        m.reply_text=rt; m.edit_text=rt
        async def rp(*a,**k): out.append("PHOTO"); return m
        m.reply_photo=rp; m.reply_document=rp
        hit=[h for h in hs if await h.check(c,m)]
        if hit:
            try: await asyncio.wait_for(hit[0].callback(c,m),20)
            except Exception as e: out.append("EXC "+type(e).__name__+": "+str(e)[:60])
        good=bool(out) and not str(out[0]).startswith("EXC")
        ok+=good
        print("OK  " if good else "FAIL",t,"->",(out[0] if out else "no reply")[:60].replace("\n"," | "))
    print(f"end-to-end through real filters: {ok}/{len(samples)}")
    assert not bad and ok==len(samples), 'self_tools filter/handler regression'
asyncio.run(main())
