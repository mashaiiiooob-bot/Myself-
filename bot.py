import asyncio
import os
import signal
import sys
import logging
import re
import aiohttp
import urllib.parse
import time
import json
import random
import uuid
import gc
import math
import collections
import html
import base64
import io
import hashlib
import hmac
import secrets
import zlib
import concurrent.futures
import threading
try :
    threading .stack_size (512 *1024 )
except Exception :
    pass 
import shutil
import binascii
import struct
import traceback
import subprocess
import tempfile
from logging.handlers import RotatingFileHandler
from types import SimpleNamespace
from urllib.parse import quote, urlsplit, parse_qs, unquote
from datetime import datetime
from zoneinfo import ZoneInfo
import pyrogram.utils

try:
    import platform as _platform
    if _platform.system() != "Windows":
        import uvloop
        uvloop.install()
    else:
        uvloop = None
        pass
except Exception:
    uvloop = None

try :
    _darkself_loop =asyncio .get_event_loop ()
except RuntimeError :
    _darkself_loop =asyncio .new_event_loop ()
    asyncio .set_event_loop (_darkself_loop )

def _darkself_loop_exception_handler (loop ,context ):
    try :
        message =str (context .get ("message","")).lower ()
        exc =context .get ("exception")
        exc_text =str (exc or "").lower ()
        if ("closed database"in message or "closed database"in exc_text or 
        isinstance (exc ,__import__ ("sqlite3").ProgrammingError )):
            return 
    except Exception :
        pass 
    loop .default_exception_handler (context )

_darkself_loop .set_exception_handler (_darkself_loop_exception_handler )

from pyrogram.methods.messages.inline_session import get_session as _pem_get_session
from pyrogram.utils import pack_inline_message_id as _pyro_pack_inline
from pyrogram.utils import unpack_inline_message_id as _pyro_unpack_inline
from pyrogram import Client, filters, idle, StopPropagation
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, RawUpdateHandler, InlineQueryHandler
from pyrogram.enums import (
    ChatType, ChatAction, ChatMembersFilter, ChatMemberStatus, ParseMode, MessagesFilter
)
from pyrogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent
)
from pyrogram.raw import functions, types
from pyrogram.errors import (
    SessionPasswordNeeded, ChatSendInlineForbidden,
    AuthKeyUnregistered, UserDeactivated, UserDeactivatedBan, PeerIdInvalid,
    FloodWait, MessageNotModified, MessageIdInvalid, SessionRevoked, AuthKeyInvalid,
    ChannelPrivate, ChannelInvalid, NotAcceptable
)
try :
    from pyrogram.errors import ChatWriteForbidden 
except Exception :
    class ChatWriteForbidden (Exception ):
        pass 

_PILLOW_IMPORT_ERROR = None
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
except (ImportError, OSError) as exc:
    Image = ImageDraw = ImageFont = ImageFilter = ImageChops = None
    _PILLOW_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"

try:
    from yt_dlp import YoutubeDL
except Exception:
    YoutubeDL = None

try:
    import jdatetime
except ImportError:
    jdatetime = None

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    arabic_reshaper = None
    get_display = None

try:
    import psutil
except ImportError:
    psutil = None

try:
    import resource as _resource_limits
except ImportError:
    _resource_limits = None

logging .basicConfig (
level =logging .INFO ,
format ="[%(asctime)s] %(levelname)s - %(message)s",
datefmt ="%Y-%m-%d %H:%M:%S"
)
logger =logging .getLogger ()

class DarkselfNoiseFilter (logging .Filter ):
    NOISY_PATTERNS =(
    "connection lost",
    "socket.send() raised exception",
    "server closed the connection",
    "connection reset by peer",
    "broken pipe",
    "transport closed",
    "connection aborted",
    "cannot operate on a closed database",
    "peer_id_invalid",
    "chat_write_forbidden",
    "task exception was never retrieved",
    "winerror 10053",
    "winerror 10054",
    "an established connection was aborted",
    )

    def filter (self ,record ):
        try :
            parts =[str (record .getMessage ()or "")]
            if record .exc_info and len (record .exc_info )>1 and record .exc_info [1 ]:
                parts .append (str (record .exc_info [1 ]))
            text =" ".join (parts ).lower ()
            return not any (p in text for p in self .NOISY_PATTERNS )
        except Exception :
            return True 

_noise_filter =DarkselfNoiseFilter ()
logger .addFilter (_noise_filter )

for _log_name in ("pyrogram","pyrogram.session","pyrogram.connection","pyrogram.dispatcher","asyncio"):
    _lg =logging .getLogger (_log_name )
    _lg .setLevel (logging .ERROR )
    _lg .addFilter (_noise_filter )

cpu_executor =concurrent .futures .ThreadPoolExecutor (max_workers =2 )

_AIOHTTP_OK = False
try:
    import sys as _sys_diag
    _aio_ver = getattr(aiohttp, "__version__", "unknown")
    _aio_file = getattr(aiohttp, "__file__", "unknown")
    _has_tc = hasattr(aiohttp, 'TCPConnector')
    _has_cs = hasattr(aiohttp, 'ClientSession')
    _has_ct = hasattr(aiohttp, 'ClientTimeout')
    logger.info(f"aiohttp loaded: version={_aio_ver} path={_aio_file} has_TCPConnector={_has_tc} has_ClientSession={_has_cs}")
    logger.info(f"Python executable: {_sys_diag.executable} | sys.path[0]={_sys_diag.path[0] if _sys_diag.path else 'empty'}")
    if not _has_tc:
        try:
            from aiohttp.connector import TCPConnector as _TC
            aiohttp.TCPConnector = _TC
            _has_tc = True
            logger.warning("Patched aiohttp.TCPConnector from aiohttp.connector")
        except Exception as _e:
            logger.error(f"Cannot patch TCPConnector: {_e} | aiohttp is BROKEN - will use fallback HTTP")
    
    import os as _os_diag
    for _shadow in ["aiohttp.py", "PIL.py"]:
        if _os_diag.path.exists(_shadow):
            logger.error(f"CRITICAL: {_shadow} in working dir shadows library! MUST rename/delete it. Path={_os_diag.path.abspath(_shadow)}")
    
    try:
        import PIL as _pil_check
        logger.info(f"Pillow OK: version={getattr(_pil_check, '__version__', 'unknown')} path={getattr(_pil_check, '__file__', 'unknown')}")
    except Exception as _pe:
        logger.warning(f"Pillow missing/broken: {_pe}")
    try:
        import tgcrypto as _tgc
        logger.info(f"TgCrypto OK: path={getattr(_tgc, '__file__', 'unknown')}")
    except Exception as _te:
        logger.warning(f"TgCrypto missing (bot will be slower): {_te} | Install: python -m pip install tgcrypto")
    _AIOHTTP_OK = _has_tc and _has_cs and _has_ct and _aio_ver != "unknown" and _aio_file not in (None, "unknown")
    if not _AIOHTTP_OK:
        logger.error("aiohttp BROKEN/MISSING: Bot API will use fallback (urllib). FIX: run 'python -m pip install --upgrade --force-reinstall --no-cache-dir aiohttp' with SAME python: " + _sys_diag.executable)
    else:
        logger.info("aiohttp health check PASSED")
except Exception as _diag_e:
    logger.warning(f"aiohttp diag failed: {_diag_e}")
    _AIOHTTP_OK = False

import multiprocessing as _mp 

_SHARD_ID_ENV =os .environ .get ("DARKSELF_SHARD_ID")
SHARD_ID =int (_SHARD_ID_ENV )if (_SHARD_ID_ENV or "").isdigit ()else None 
_SHARD_COUNT_ENV =os .environ .get ("DARKSELF_SHARD_COUNT")
SHARD_COUNT =int (_SHARD_COUNT_ENV )if (_SHARD_COUNT_ENV or "").isdigit ()else 0 

ADMIN_LOG_DIR =os .path .join (os .path .dirname (os .path .abspath (__file__ )),".darkself_logs")
ADMIN_LOG_SOURCE =f"shard-{SHARD_ID }"if SHARD_ID is not None else "manager"

def _redact_admin_log (text ):
    text =str (text )
    for key in ("BOT_TOKEN","API_HASH","DB_ENCRYPTION_KEY","ENCRYPTION_KEY"):
        value =globals ().get (key )
        if isinstance (value ,str )and len (value )>=8 :
            text =text .replace (value ,"[REDACTED]")
    text =re .sub (r"\b\d{5,16}:[A-Za-z0-9_-]{20,}\b","[TOKEN]",text )
    text =re .sub (r"(?i)(\b(?:api_hash|bot_token|access_token|auth_key|session_string|phone_code_hash|password|passwd|secret|authorization)\b[\"']?\s*[:=]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",r"\1[REDACTED]",text )
    text =re .sub (r"(?i)\b(?:Bearer|Basic)\s+[A-Za-z0-9_+/=.-]+","[AUTH]",text )
    text =re .sub (r"\b[0-9a-fA-F]{32,}\b","[KEY]",text )
    text =re .sub (r"[A-Za-z0-9_+/=-]{80,}","[SECRET]",text )
    text =re .sub (r"(?<!\w)\+?\d{9,15}(?!\w)","[NUMBER]",text )
    text =re .sub (r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]","",text )
    return text 

class DarkselfAdminLogFormatter (logging .Formatter ):
    def format (self ,record ):
        text =record .getMessage ()
        if record .exc_info :
            text +="\n"+self .formatException (record .exc_info )
        return json .dumps ({
        "ts":record .created ,"level":record .levelname ,
        "source":ADMIN_LOG_SOURCE ,"text":_redact_admin_log (text )[:3000 ]
        },ensure_ascii =False )

class DarkselfPrivateLogFile (RotatingFileHandler ):
    def handleError (self ,record ):
        
        pass 

class DarkselfAdminLogHandler (logging .Handler ):
    def __init__ (self ):
        super ().__init__ (level =logging .INFO )
        self .recent =collections .deque (maxlen =300 )
        self .disk =None 
        formatter =DarkselfAdminLogFormatter ()
        self .setFormatter (formatter )
        try :
            os .makedirs (ADMIN_LOG_DIR ,mode =0o700 ,exist_ok =True )
            path =os .path .join (ADMIN_LOG_DIR ,ADMIN_LOG_SOURCE +".jsonl")
            self .disk =DarkselfPrivateLogFile (path ,maxBytes =524288 ,backupCount =2 ,encoding ="utf-8")
            self .disk .setFormatter (formatter )
            try :os .chmod (path ,0o600 )
            except OSError :pass 
        except Exception :
            
            self .disk =None 

    def emit (self ,record ):
        try :
            self .recent .append (self .format (record ))
            if self .disk is not None :
                self .disk .emit (record )
        except Exception :
            pass 

_ADMIN_LOG_HANDLER =DarkselfAdminLogHandler ()
logger .addHandler (_ADMIN_LOG_HANDLER )

if _PILLOW_IMPORT_ERROR is not None:
    logger.warning (
        "Sticker rendering disabled: Pillow import failed (%s). "
        "In the bot's Python environment run: `python -m pip install "
        "--upgrade --force-reinstall --no-cache-dir Pillow`. "
        "Also check for a local PIL.py or PIL folder shadowing Pillow, then restart.",
        _PILLOW_IMPORT_ERROR
    )

def _read_recent_admin_logs ():
    _ADMIN_LOG_HANDLER .acquire ()
    try :
        lines =list (_ADMIN_LOG_HANDLER .recent )
    finally :
        _ADMIN_LOG_HANDLER .release ()
    try :
        with os .scandir (ADMIN_LOG_DIR )as entries :
            files =[
            (entry .stat (follow_symlinks =False ).st_mtime ,entry .path )
            for entry in entries 
            if re .fullmatch (r"(?:manager|shard-\d+)\.jsonl(?:\.[12])?",entry .name )
            and entry .is_file (follow_symlinks =False )
            ]
        for _ ,path in sorted (files ,reverse =True )[:48 ]:
            try :
                with open (path ,"rb")as stream :
                    stream .seek (0 ,os .SEEK_END )
                    start =max (0 ,stream .tell ()-65536 )
                    stream .seek (start )
                    if start :stream .readline ()
                    lines .extend (stream .read (65536 ).decode ("utf-8",errors ="replace").splitlines ())
            except OSError :
                continue 
    except OSError :
        pass 
    records ={}
    for line in lines :
        try :
            item =json .loads (line )
            ts =float (item ["ts"])
            if not math .isfinite (ts ):continue 
            source =str (item .get ("source","manager"))[:40 ]
            level =str (item .get ("level","INFO"))[:20 ]
            text =_redact_admin_log (item .get ("text",""))[:3000 ]
            records [(ts ,source ,level ,text )]={"ts":ts ,"source":source ,"level":level ,"text":text }
        except (ValueError ,TypeError ,KeyError ):
            continue 
    return sorted (records .values (),key =lambda item :item ["ts"],reverse =True )[:300 ]

SHARD_MASTER_MODE =(SHARD_ID is None )and bool (int (os .environ .get ("DARKSELF_SHARDING_ACTIVE","0")))

_SHARD_RELOAD_EVENT =None 
_SHARD_STATUS_DICT =None 
_SHARD_MGR_PROXY =None 
_SHARD_WORKERS ={}
_SHARD_CURRENT_N =0 

_SHARD_LOCK =threading .Lock ()

def _shard_init_ipc ():
    global _SHARD_RELOAD_EVENT ,_SHARD_STATUS_DICT ,_SHARD_MGR_PROXY 
    if SHARD_ID is not None :

        _SHARD_RELOAD_EVENT =None 
        _SHARD_STATUS_DICT ={}
        return 
    if _SHARD_MGR_PROXY is None :
        try :
            _SHARD_MGR_PROXY =_mp .Manager ()
            _SHARD_RELOAD_EVENT =_SHARD_MGR_PROXY .Event ()
            _SHARD_STATUS_DICT =_SHARD_MGR_PROXY .dict ()
        except Exception as _e :
            logger .warning (f"Shard IPC init failed: {_e }")
            _SHARD_RELOAD_EVENT =None 
            _SHARD_STATUS_DICT ={}

_SHARD_RELOAD_SENTINEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".darkself_shard_reload")

def _shard_reload_signature():
    try:
        with open(_SHARD_RELOAD_SENTINEL, "rb") as stream:
            stat = os.fstat(stream.fileno())
            payload = stream.read(256)
        return stat.st_mtime_ns, stat.st_size, payload
    except OSError:
        return None

def _shard_signal_reload():
    temporary = f"{_SHARD_RELOAD_SENTINEL}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    try:
        with open(temporary, "w", encoding="ascii") as stream:
            stream.write(f"{time.time_ns()}:{os.getpid()}:{uuid.uuid4().hex}")
            stream.flush()
        os.replace(temporary, _SHARD_RELOAD_SENTINEL)
    except Exception as exc:
        logger.debug("shard reload signal failed: %s", exc)
        try:
            os.remove(temporary)
        except OSError:
            pass
    try:
        if _SHARD_RELOAD_EVENT is not None:
            _SHARD_RELOAD_EVENT.set()
    except Exception:
        pass

def _broadcast_database_change():
    if SHARD_ID is not None or _SHARD_CURRENT_N > 0:
        _shard_signal_reload()

def _commit_and_broadcast_shards(reason: str = "state-sync"):
    try:
        data_manager.force_save_sync()
    except Exception as exc:
        try:
            logger.warning("force save before shard broadcast failed: %s", exc)
        except Exception:
            pass
    try:
        _shard_signal_reload()
    except Exception:
        pass

def _shard_should_reload(last_signature):
    signature = _shard_reload_signature()
    if signature is None:
        return False, last_signature
    return signature != last_signature, signature

def _shard_assigns_to_me (uid ):
    if SHARD_ID is None or SHARD_COUNT <=1 :
        return True 
    return (int (uid )%SHARD_COUNT )==SHARD_ID 

class _ShardSupervisor :

    def __init__ (self ):
        self .workers ={}

    def _spawn_worker (self ,shard_id ,total ):
        env =os .environ .copy ()
        env ["DARKSELF_SHARD_ID"]=str (shard_id )
        env ["DARKSELF_SHARD_COUNT"]=str (total )
        env ["DARKSELF_SHARDING_ACTIVE"]="1"
        try :

            ctx =_mp .get_context ("spawn")
            p =ctx .Process (
            target =_shard_worker_entry ,
            args =(shard_id ,total ),
            name =f"darkself-shard-{shard_id }",
            daemon =False ,
            )
            p .start ()
            self .workers [shard_id ]=p 
            logger .info (f"[shard] spawned worker shard_id={shard_id } pid={p .pid } (total={total })")
            return p 
        except Exception as e :
            logger .error (f"[shard] failed to spawn worker {shard_id }: {e }")
            return None 

    def resize (self ,n ):
        global _SHARD_CURRENT_N 
        if n <=0 :
            self .kill_all ()
            _SHARD_CURRENT_N =0 
            return 
        if n ==_SHARD_CURRENT_N and len (self .workers )==n :
            return 
        with _SHARD_LOCK :

            self .kill_all ()
            for k in range (n ):
                self ._spawn_worker (k ,n )
            _SHARD_CURRENT_N =n 
            logger .info (f"[shard] resize complete: {n } workers active")

    def kill_all (self ):
        global _SHARD_CURRENT_N 
        for k ,p in list (self .workers .items ()):
            try :
                if p .is_alive ():
                    p .terminate ()
                    p .join (timeout =3.0 )
                if p .is_alive ():
                    p .kill ()
            except Exception as e :
                logger .warning (f"[shard] kill worker {k } error: {e }")
        self .workers .clear ()
        _SHARD_CURRENT_N =0 

    def health_check (self ):
        for k ,p in list (self .workers .items ()):
            try :
                if not p .is_alive ():
                    logger .warning (f"[shard] worker {k } died (exitcode={p .exitcode }); respawning")
                    del self .workers [k ]
                    self ._spawn_worker (k ,_SHARD_CURRENT_N )
            except Exception :
                pass 

    def status (self ):
        out ={}
        for k ,p in self .workers .items ():
            out [k ]={"alive":p .is_alive (),"pid":p .pid ,"exitcode":p .exitcode }
        return out 

_shard_supervisor =_ShardSupervisor ()

def _shard_worker_entry (shard_id ,total ):

    try :
        asyncio .get_event_loop ().run_until_complete (main ())
    except KeyboardInterrupt :
        pass 
    finally :
        os ._exit (0 )

def _patch_pyrogram_filter_performance ():
    import inspect as _inspect 
    from pyrogram import filters as _pf 

    def _is_coro (fn ):
        return _inspect .iscoroutinefunction (fn )

    async def _and_call (self ,client ,update ):
        is_base_coro =self .__dict__ .get ("_base_is_coro")
        if is_base_coro is None :
            is_base_coro =_is_coro (self .base .__call__ )
            self ._base_is_coro =is_base_coro 
        if is_base_coro :
            x =await self .base (client ,update )
        else :
            x =await client .loop .run_in_executor (client .executor ,self .base ,client ,update )

        if not x :
            return False 

        is_other_coro =self .__dict__ .get ("_other_is_coro")
        if is_other_coro is None :
            is_other_coro =_is_coro (self .other .__call__ )
            self ._other_is_coro =is_other_coro 
        if is_other_coro :
            y =await self .other (client ,update )
        else :
            y =await client .loop .run_in_executor (client .executor ,self .other ,client ,update )

        return x and y 

    async def _or_call (self ,client ,update ):
        is_base_coro =self .__dict__ .get ("_base_is_coro")
        if is_base_coro is None :
            is_base_coro =_is_coro (self .base .__call__ )
            self ._base_is_coro =is_base_coro 
        if is_base_coro :
            x =await self .base (client ,update )
        else :
            x =await client .loop .run_in_executor (client .executor ,self .base ,client ,update )

        if x :
            return True 

        is_other_coro =self .__dict__ .get ("_other_is_coro")
        if is_other_coro is None :
            is_other_coro =_is_coro (self .other .__call__ )
            self ._other_is_coro =is_other_coro 
        if is_other_coro :
            y =await self .other (client ,update )
        else :
            y =await client .loop .run_in_executor (client .executor ,self .other ,client ,update )

        return x or y 

    async def _invert_call (self ,client ,update ):
        is_base_coro =self .__dict__ .get ("_base_is_coro")
        if is_base_coro is None :
            is_base_coro =_is_coro (self .base .__call__ )
            self ._base_is_coro =is_base_coro 
        if is_base_coro :
            x =await self .base (client ,update )
        else :
            x =await client .loop .run_in_executor (client .executor ,self .base ,client ,update )

        return not x 

    try :
        _pf .AndFilter .__call__ =_and_call 
        _pf .OrFilter .__call__ =_or_call 
        _pf .InvertFilter .__call__ =_invert_call 
        logger .info ("Pyrogram filter performance patch applied (AndFilter/OrFilter/InvertFilter cached).")
    except Exception as _e :
        logger .warning (f"Pyrogram filter performance patch failed, continuing without it: {_e }")

_patch_pyrogram_filter_performance ()

def patch_peer_id_validation ():
    original_get_peer_type =pyrogram .utils .get_peer_type 
    def patched_get_peer_type (peer_id :int )->str :
        try :
            return original_get_peer_type (peer_id )
        except ValueError :
            if str (peer_id ).startswith ("-100"):
                return "channel"
            raise 
    pyrogram .utils .get_peer_type =patched_get_peer_type 

def patch_pyrogram_runtime_noise ():
    try :
        ChatClass =pyrogram .types .Chat 
        original_parse =ChatClass ._parse 
        if not getattr (original_parse ,"_darkself_safe",False ):
            def safe_chat_parse (client ,message ,users ,chats ,is_chat =True ):
                try :
                    return original_parse (client ,message ,users ,chats ,is_chat )
                except KeyError as e :
                    try :
                        missing_id =int (e .args [0 ])
                    except Exception :
                        missing_id =0 
                    try :
                        return ChatClass (
                        id =missing_id ,
                        type =ChatType .PRIVATE ,
                        first_name =str (missing_id )if missing_id else "Unknown",
                        client =client 
                        )
                    except Exception :
                        return None 
            safe_chat_parse ._darkself_safe =True 
            ChatClass ._parse =staticmethod (safe_chat_parse )
    except Exception :
        pass 

    try :
        from pyrogram.types.messages_and_media.message_story import MessageStory as _MS
        async def _skip_ms_story (*a ,**kw ):
            return None 
        _skip_ms_story ._darkself_safe =True 
        try :
            _MS ._parse =staticmethod (_skip_ms_story )
        except Exception :
            _MS ._parse =_skip_ms_story 
    except Exception :
        pass 

    try :
        async def _skip_story (*a ,**kw ):
            return None 
        _skip_story ._darkself_safe =True 
        for _cls_name in ("Story","StoryDeleted","StoryForwarded"):
            _cls =getattr (pyrogram .types ,_cls_name ,None )
            if _cls is None :
                continue 
            try :
                setattr (_cls ,"_parse",staticmethod (_skip_story ))
            except Exception :
                try :setattr (_cls ,"_parse",_skip_story )
                except Exception :pass 
        try :
            from pyrogram.types.messages_and_media.story_deleted import StoryDeleted as _SD
            _SD ._parse =staticmethod (_skip_story )
        except Exception :
            pass 
        try :
            from pyrogram.types.messages_and_media.story import Story as _ST
            _ST ._parse =staticmethod (_skip_story )
        except Exception :
            pass 
    except Exception :
        pass 

    try :
        CallbackQueryClass =pyrogram .types .CallbackQuery 
        original_answer =CallbackQueryClass .answer 
        if not getattr (original_answer ,"_darkself_safe",False ):
            async def safe_callback_answer (self ,*args ,**kwargs ):
                try :
                    return await original_answer (self ,*args ,**kwargs )
                except Exception as e :
                    low =str (e ).lower ()
                    if "query_id_invalid"in low or "query id is invalid"in low or "setbotcallbackanswer"in low :
                        return None 
                    raise 
            safe_callback_answer ._darkself_safe =True 
            CallbackQueryClass .answer =safe_callback_answer 
    except Exception :
        pass 

    try :
        MessageClass =pyrogram .types .Message 
        original_delete =MessageClass .delete 
        if not getattr (original_delete ,"_darkself_guard",False ):
            async def guarded_message_delete (self ,*args ,**kwargs ):
                try :
                    client =getattr (self ,"_client",None )or getattr (self ,"client",None )
                    chat =getattr (self ,"chat",None )
                    from_user =getattr (self ,"from_user",None )
                    is_out =bool (getattr (self ,"outgoing",False ))
                    if client and getattr (client ,"me",None )and chat and from_user and not is_out :
                        uid =int (client .me .id )
                        sender_id =int (from_user .id )
                        is_private =getattr (chat ,"type",None )==ChatType .PRIVATE 
                        if is_private and sender_id !=uid and sender_id !=ROOT_ADMIN :
                            any_pv_lock =any (d .get (uid ,False )for d in (
                            PV_LOCK_STATUS ,PV_PHOTO_LOCK ,PV_VIDEO_LOCK ,PV_GIF_LOCK ,PV_VOICE_LOCK ,
                            PV_MUSIC_LOCK ,PV_STICKER_LOCK ,PV_DOC_LOCK ,PV_LOC_LOCK ,PV_EMO_LOCK ,PV_TXT_LOCK 
                            ))
                            filter_on =FILTER_WORDS_ACTIVE .get (uid ,False )
                            fjoin_on =FORCED_JOIN_ACTIVE .get (uid ,False )and bool (FORCED_JOIN_CHATS .get (uid ,[]))
                            muted_on =(sender_id ,int (chat .id ))in MUTED_USERS .get (uid ,set ())

                            if not (any_pv_lock or filter_on or fjoin_on or muted_on ):
                                return None 
                            if ANTI_DELETE_STATUS .get (uid ,False ):
                                try :
                                    remember_message_for_timeline (uid ,self )
                                    item =MESSAGE_TIMELINE_CACHE .get (uid ,{}).get ((chat .id ,self .id ))
                                    if item :
                                        await notify_timeline_event (client ,uid ,"☒ ضد دیلیت | پیام توسط سلف حذف شد",item )
                                except Exception :
                                    pass 
                except Exception :
                    pass 
                return await original_delete (self ,*args ,**kwargs )
            guarded_message_delete ._darkself_guard =True 
            MessageClass .delete =guarded_message_delete 
    except Exception :
        pass 

patch_peer_id_validation ()
patch_pyrogram_runtime_noise ()

_SKIP_RAW_UPDATE_NAMES =frozenset ((
"UpdateUserStatus","UpdateChatUserTyping","UpdateChannelUserTyping","UpdateUserTyping",
"UpdateStory","UpdateStoryID","UpdateSentStoryReaction","UpdateReadStories","UpdateStoriesStealthMode",
"UpdateStoryReaction","UpdateNewStory","UpdateUserStories",
"UpdateReadHistoryInbox","UpdateReadHistoryOutbox","UpdateReadChannelInbox","UpdateReadChannelOutbox",
"UpdateReadChannelDiscussionInbox","UpdateReadChannelDiscussionOutbox",
"UpdateChannelReadMessagesContents","UpdateReadMessagesContents",
"UpdateDraftMessage","UpdatePendingJoinRequests",
"UpdateDialogPinned","UpdatePinnedDialogs","UpdateFolderPeers",
"UpdateChannelAvailableMessages","UpdateChannelMessageViews","UpdateChannelMessageForwards",
"UpdateWebPage","UpdatePtsChanged","UpdateConfig","UpdateDcOptions",
"UpdatePeerSettings","UpdatePeerBlocked","UpdateTheme",
"UpdateLangPack","UpdateLangPackTooLong",
"UpdateRecentStickers","UpdateRecentReactions",
"UpdatePinnedMessages","UpdatePinnedChannelMessages",
"UpdateBotMenuButton",
"UpdateRecentEmojiStatuses","UpdateUserEmojiStatus","UpdateMoveStickerSetToTop",
"UpdatePeerWallpaper","UpdatePeerHistoryTTL",
"UpdateDialogFilter","UpdateDialogFilterOrder","UpdateDialogFilters","UpdateDialogUnreadMark",
"UpdateSavedGifs","UpdateSavedRingtones","UpdateFavedStickers","UpdateAttachMenuBots",
"UpdateBotCommands","UpdateGroupCall","UpdateGroupCallParticipants","UpdateGroupCallConnection",
"UpdatePhoneCall","UpdatePhoneCallSignalingData",
"UpdateMessagePoll","UpdateMessagePollVote",
"UpdateChannelViewForumAsMessages","UpdateChannelPinnedTopic","UpdateChannelPinnedTopics",
"UpdateAutoSaveSettings",
))

def _raw_update_is_noise (u ):
    if u is None :
        return True 
    name =type (u ).__name__ 
    if name in _SKIP_RAW_UPDATE_NAMES or "Story"in name :
        return True 
    msg =getattr (u ,"message",None )
    if msg is not None :
        media =getattr (msg ,"media",None )
        if media is not None and "Story"in type (media ).__name__ :
            return True 
        action =getattr (msg ,"action",None )
        if action is not None and "Story"in type (action ).__name__ :
            return True 
    return False 

def _filter_raw_updates (updates ):
    if updates is None :
        return None 
    name =type (updates ).__name__ 
    if name in ("Updates","UpdatesCombined"):
        seq =getattr (updates ,"updates",None )
        if not seq :
            return updates 
        kept =[u for u in seq if not _raw_update_is_noise (u )]
        if not kept :
            return None 
        if len (kept )!=len (seq ):
            try :
                updates .updates =kept 
            except Exception :
                pass 
        return updates 
    if name =="UpdateShort":
        inner =getattr (updates ,"update",None )
        if _raw_update_is_noise (inner ):
            return None 
        return updates 
    if _raw_update_is_noise (updates ):
        return None 
    return updates 

def _darkself_optional_client_kwargs ():
    out ={}
    try :
        import inspect as _inspect
        params =_inspect .signature (Client .__init__ ).parameters
        if "max_message_cache_size" in params :
            out ["max_message_cache_size"]=64
    except Exception :
        pass
    return out

class ResilientClient (Client ):
    def __init__ (self ,*args ,**kwargs ):
        kwargs .setdefault ("sleep_threshold",30 )
        kwargs .setdefault ("max_concurrent_transmissions",1 )
        kwargs .setdefault ("workers",1 )
        kwargs .update (_darkself_optional_client_kwargs ())
        try :
            import inspect as _inspect2
            if "skip_updates" in _inspect2 .signature (Client .__init__ ).parameters :
                kwargs .setdefault ("skip_updates",True )
            else :
                kwargs .pop ("skip_updates",None )
        except Exception :
            kwargs .pop ("skip_updates",None )
        super ().__init__ (*args ,**kwargs )
        self ._darkself_invalid_session_cleanup =False 

    def _extract_darkself_uid (self ):
        try :
            name =getattr (self ,"name","")or ""
            if name .startswith ("bot_"):
                return int (name .split ("_",1 )[1 ])
        except Exception :
            pass 
        try :
            return int (getattr (getattr (self ,"me",None ),"id",0 )or 0 )
        except Exception :
            return 0 

    def _schedule_invalid_session_cleanup (self ,reason ="SESSION_INVALID"):
        if self ._darkself_invalid_session_cleanup :
            return 
        self ._darkself_invalid_session_cleanup =True 
        uid =self ._extract_darkself_uid ()

        async def cleanup ():
            try :
                logger .warning (f"Invalid/revoked session detected for {uid or self .name }: {reason }. Cleaning up to prevent RAM loop.")
                if uid :
                    try :
                        MESSAGE_TIMELINE_CACHE .pop (uid ,None )
                    except Exception :
                        pass 
                    try :
                        pair =ACTIVE_BOTS .pop (uid ,None )
                        if pair :
                            _ ,tasks =pair 
                            for t in tasks :
                                try :t .cancel ()
                                except Exception :pass 
                    except Exception :
                        pass 
                    try :
                        phone_to_remove =None 
                        for phone ,s_data in list (data_manager .data .get ("sessions",{}).items ()):
                            if s_data .get ("user_id")==uid :
                                phone_to_remove =phone 
                                break 
                        if phone_to_remove :
                            data_manager .mark_invalid_session (uid ,phone_to_remove ,reason )
                            data_manager .delete_session (phone_to_remove )
                            logger .warning (f"Marked invalid and deleted revoked session: uid={uid }, phone={phone_to_remove }")
                    except Exception as e :
                        logger .warning (f"Could not remove revoked session {uid }: {e }")
                try :
                    await self .stop ()
                except Exception :
                    pass 
                try :
                    gc .collect ()
                except Exception :
                    pass 
            except Exception as e :
                logger .warning (f"Invalid session cleanup failed: {e }")

        try :
            asyncio .create_task (cleanup ())
        except Exception :
            pass 

    async def invoke (self ,*args ,**kwargs ):
        try :
            return await super ().invoke (*args ,**kwargs )
        except (SessionRevoked ,AuthKeyUnregistered ,UserDeactivated ,UserDeactivatedBan ,SessionRevoked ,AuthKeyInvalid )as e :
            self ._schedule_invalid_session_cleanup (type (e ).__name__ )
            raise 

    async def fetch_peers (self ,peers ):
        try :
            conn =getattr (getattr (self ,"storage",None ),"conn",None )
            if conn is not None and peers :
                try :
                    n =conn .execute ("SELECT COUNT(*) FROM peers").fetchone ()[0 ]
                except Exception :
                    n =0 
                if n >2500 :
                    slim =[]
                    for p in peers :
                        if type (p ).__name__ in ("Channel","Chat","ChannelForbidden","ChatForbidden"):
                            slim .append (p )
                    peers =slim 
            return await super ().fetch_peers (peers )
        except Exception :
            try :
                return await super ().fetch_peers (peers )
            except Exception :
                return False 

    async def handle_updates (self ,*args ,**kwargs ):
        try :
            if args :
                filtered =_filter_raw_updates (args [0 ])
                if filtered is None :
                    return 
                try :
                    q =self .dispatcher .updates_queue 
                    if q .qsize ()>100 :
                        return 
                except Exception :
                    pass 
                args =(filtered ,)+args [1 :]
            await super ().handle_updates (*args ,**kwargs )
        except (SessionRevoked ,AuthKeyUnregistered ,UserDeactivated ,UserDeactivatedBan ,SessionRevoked ,AuthKeyInvalid )as e :
            self ._schedule_invalid_session_cleanup (type (e ).__name__ )
        except (PeerIdInvalid ,ChannelPrivate ,ChannelInvalid ,ChatWriteForbidden ,MessageIdInvalid ,NotAcceptable ):
            pass 
        except (ValueError ,KeyError )as e :
            msg =str (e )
            if 'Peer id invalid'not in msg and 'ID not found'not in msg :
                logger .debug (f"ResilientClient minor exception: {msg }")
        except Exception as e :
            msg =str (e )
            low =msg .lower ()
            if "SESSION_REVOKED"in msg or "AUTH_KEY"in msg or "USER_DEACTIVATED"in msg :
                self ._schedule_invalid_session_cleanup (msg [:80 ])
            elif "peer_id_invalid"in low or "chat_write_forbidden"in low or "channel_private"in low :
                pass 

    async def get_messages (self ,*args ,**kwargs ):
        try :
            return await super ().get_messages (*args ,**kwargs )
        except (ChannelPrivate ,ChannelInvalid ,PeerIdInvalid ):
            pass 
        except (SessionRevoked ,AuthKeyUnregistered ,UserDeactivated ,UserDeactivatedBan ,AuthKeyInvalid )as e :
            self ._schedule_invalid_session_cleanup (type (e ).__name__ )
            pass 
        except Exception :
            pass 

        msg_ids =args [1 ]if len (args )>1 else kwargs .get ("message_ids")
        if isinstance (msg_ids ,(list ,tuple ,set )):
            return []
        return None 

API_ID = int(os.environ.get("API_ID", "0") or 0)
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PREMIUM_BOT_TOKEN = os.environ.get("PREMIUM_BOT_TOKEN", "")
ROOT_ADMIN = int(os.environ.get("ROOT_ADMIN", "0") or 0)

_missing_env = [k for k, v in (("API_ID", API_ID), ("API_HASH", API_HASH), ("BOT_TOKEN", BOT_TOKEN)) if not v]
if _missing_env:
    logger.error("[سیستم] متغیرهای محیطی تنظیم نشده‌اند: %s (آنها را در Railway > Variables اضافه کنید)", ", ".join(_missing_env))
    raise SystemExit(1)

DATA_FILE ="bot_data.json"
TEHRAN_TIMEZONE =ZoneInfo ("Asia/Tehran")
LOGIN_STATES ={}
LOGIN_RATE_LIMIT ={}
LOGIN_RATE_MAX =3 
LOGIN_RATE_WINDOW =600 
SESSION_START_THROTTLE ={}
SESSION_START_LOCKS ={}
ACTIVATION_DELAY_SECONDS =120
BOT_USERNAME =None 

HTTP_SESSION =None 
RECENT_CHATS ={}
USE_FALLBACK_HTTP = False  

HTTP_SESSION_LOCK = asyncio.Lock()

async def get_http_session ():
    global HTTP_SESSION 
    
    if not globals().get("_AIOHTTP_OK", False):
        return None
    if HTTP_SESSION is not None and not HTTP_SESSION .closed :
        return HTTP_SESSION 
    async with HTTP_SESSION_LOCK :
        if HTTP_SESSION is not None and not HTTP_SESSION .closed :
            return HTTP_SESSION 
        
        connector = None 
        try :
            
            if hasattr(aiohttp, "TCPConnector"):
                connector = aiohttp.TCPConnector(limit=30, limit_per_host=10, ttl_dns_cache=600, keepalive_timeout=60, force_close=False, enable_cleanup_closed=True)
            else:
                
                try:
                    from aiohttp.connector import TCPConnector as _TCPConnector
                    connector = _TCPConnector(limit=30, limit_per_host=10, ttl_dns_cache=600, keepalive_timeout=60, force_close=False, enable_cleanup_closed=True)
                    logger.warning("aiohttp.TCPConnector missing, used aiohttp.connector.TCPConnector fallback")
                except Exception as ie:
                    logger.warning(f"TCPConnector unavailable, using plain ClientSession: {ie}")
                    connector = None
        except Exception as ce:
            logger.warning(f"TCPConnector creation failed, fallback to plain session: {ce}")
            connector = None
        try:
            if connector is not None:
                HTTP_SESSION = aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10))
            else:
                HTTP_SESSION = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            
            try:
                ver = getattr(aiohttp, "__version__", "unknown")
                path = getattr(aiohttp, "__file__", "unknown")
                logger.info(f"HTTP session ready | aiohttp {ver} @ {path} | connector={'yes' if connector else 'no'}")
                
                import os as _os
                if _os.path.exists("aiohttp.py") or _os.path.exists("./aiohttp.py"):
                    logger.error("SHADOWING DETECTED: aiohttp.py in working directory shadows library! Rename it.")
            except Exception:
                pass
        except Exception as se:
            logger.error(f"Failed to create ClientSession: {se} -> will use fallback HTTP")
            globals()["USE_FALLBACK_HTTP"] = True
            globals()["_AIOHTTP_OK"] = False
            return None
    return HTTP_SESSION 

async def _fallback_bot_api_request(method: str, payload: dict, timeout: float = 5.0):
    import json as _json
    import urllib.request as _req
    import urllib.error as _err
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = _json.dumps(payload).encode("utf-8")
    def _do():
        try:
            r = _req.Request(url, data=data, headers={"Content-Type": "application/json"})
            with _req.urlopen(r, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                try:
                    return _json.loads(body)
                except Exception:
                    return {"ok": False, "description": body[:500]}
        except _err.HTTPError as he:
            try:
                body = he.read().decode("utf-8", errors="replace")
                try:
                    return _json.loads(body)
                except:
                    return {"ok": False, "description": f"HTTP {he.code}: {body[:500]}"}
            except Exception as ce:
                return {"ok": False, "description": str(ce)}
        except Exception as ce:
            return {"ok": False, "description": str(ce)}
    try:
        result = await asyncio.get_event_loop().run_in_executor(None, _do)
        if not result.get("ok"):
            desc = str(result.get("description",""))
            low = desc.lower()
            if "message is not modified" not in low and "message_id_invalid" not in low:
                logger.error(f"Bot API fallback error [{method}]: {result}")
        return result
    except Exception as e:
        return {"ok": False, "description": str(e)}

async def bot_api_request (method :str ,payload :dict ,timeout :float =5.0 ):
    global HTTP_SESSION
    
    if not globals().get("_AIOHTTP_OK", False) or globals().get("USE_FALLBACK_HTTP", False):
        return await _fallback_bot_api_request(method, payload, timeout)
    
    last_err = ""
    _fast = method == "answerInlineQuery"
    for attempt in range(1 if _fast else 2):
        try :
            session =await get_http_session ()
            if session is None:
                
                return await _fallback_bot_api_request(method, payload, timeout)
            url =f"https://api.telegram.org/bot{BOT_TOKEN }/{method }"
            
            t = aiohttp.ClientTimeout(total=timeout)
            async with session .post (url ,json =payload ,timeout =t )as resp :
                try :
                    result =await resp .json ()
                except Exception :
                    try:
                        txt = await resp.text()
                    except Exception:
                        txt = "no body"
                    result ={"ok":False ,"description":txt}
                if not result .get ("ok"):
                    desc =str (result .get ("description",""))
                    low_desc =desc .lower ()
                    if "message is not modified"not in low_desc and "message_id_invalid"not in low_desc :
                        logger .error (f"Bot API error [{method }] attempt {attempt+1}: {result }")
                    if "retry after" in low_desc or "too many requests" in low_desc:
                        if method .startswith ("edit"):
                            return result
                        await asyncio.sleep(1.5)
                        continue
                return result 
        except asyncio.TimeoutError as e:
            last_err = f"Timeout after {timeout}s"
            logger.warning(f"Bot API timeout [{method }] attempt {attempt+1}: {last_err}")
            await asyncio.sleep(0.6)
        except Exception as e :
            err =str (e )
            last_err = err
            if "TCPConnector" in err or "has no attribute" in err or "ClientSession" in err:
                logger.error(f"Bot API aiohttp error detected, switching to fallback: {err}")
                globals()["USE_FALLBACK_HTTP"] = True
                return await _fallback_bot_api_request(method, payload, timeout)
            if err .strip ():
                logger .error (f"Bot API request failed [{method }] attempt {attempt+1}: {err }")
            await asyncio.sleep(0.4)
    if _fast :
        return {"ok":False ,"description":last_err or "inline answer timed out"}
    
    try:
        fb = await _fallback_bot_api_request(method, payload, timeout)
        if fb.get("ok"):
            return fb
    except Exception:
        pass
    return {"ok":False ,"description":last_err or "failed after retries"}

ENEMY_REPLIES_DEFAULT = [
    "کیرم تو رحم اجاره ای و خونی مالی مادرت",
    "دو میلیون شبی pool ویلا بدم تا مادرتو تو گوشه کناراش بگام و اب کوسشو بریزم کف خونه تا فردا صبح کارگرای افغانی برای نظافت اومدن با بوی اب کس مادرت بجقن و ابکیراشون نثار قبر مرده هات بشه",
    "احمق مادر کونی من کس مادرت گذاشتم تو بازم داری کسشر میگی",
    "هی بیناموس کیرم بره تو کس ننت واس بابات نشآخ مادر کیری کیرم بره تو کس اجدادت کسکش بیناموس کس ول نسل شوتی ابجی کسده کیرم تو کس مادرت بیناموس کیری کیرم تو کس نسل ابجی کونی کس نسل سگ ممبر کونی ابجی سگ ممبر سگ کونی کیرم تو کس ننت کیر تو کس مادرت کیر خاندان تو کس نسل مادر کونی ابجی کونی کیری ناموس ابجیتو گاییدم سگ حرومی خارکسه مادر کیری با کیر بزنم تو رحم مادرت ناموستو بگام لاشی کونی ابجی کس خیابونی مادرخونی ننت کیرمو میماله تو میای کص میگی شاخ نشو ییا ببین شاخو کردم تو کون ابجی جندت کس ابجیتو پاره کردم تو شاخ میشی اوبی",
    "کیرم تو کس سیاه مادرت خارکصده",
    "حروم زاده باک کص ننت با ابkیرم پر میکنم",
    "منبع اب ایرانو با اب کص مادرت تامین میکنم",
    "خارکسته میخای مادرتو بگام بعد بیای ادعای شرف کنی کیرم تو شرف مادرت",
    "کیرم تویه اون خرخره مادرت بیا اینحا ببینم تویه نوچه کی دانلود شدی کیفیتت پایینه صدات نمیاد فقط رویه حالیت بی صدا داری امواج های بی ارزش و بیناموسانه از خودت ارسال میکنی که ناگهان دیدی من روانی شدم دست از پا خطا کردم با تبر کائنات کوبیدم رو سر مادرت نمیتونی مارو تازه بالقه گمان کنی",
    "کیرم تو کس مادرت انقدر گاییدم که رحم ننت شده پارکینگ کیرهای محله",
    "ننتو بردم زیر پل گاییدم بعد اب کیرمو ریختم رو قبر پدرت تا جنازه ش هم طعم ناموستو بچشه",
    "مادر جندت رو انقدر گاییدم که کسش شده بزرگراه بین شهری کیرم تو نسلت",
    "خواهرتو تو حموم عمومی گاییدم همه دیدن بعد اب کیرمو با شامپو قاطی کردم سرش ریختم",
    "کیرم تو رحم مادرت انقدر کوبیدم که جنین مرده ش هم از ترس بیرون پرید",
    "بابات اومد در زد گفتم ننت داره کیر میخوره گفت بذار تموم شه بعد بیام",
    "کس مادرتو با مشت باز کردم بعد کیرمو تا ته فرو کردم تا ناله ش کوچه رو لرزوند",
    "مادرتو بستم به درخت گاییدم بعد سگای محل اومدن اب کیرمو لیسیدن از روش",
    "ننت جنده محله است هر شب ده تا کیر میخوره بعد میاد خونه ادعا میکنه پاکه",
    "کیرم تو کس اجداد مادرت نسل به نسل گاییده شدن تا رسیدن به تو حرومزاده",
    "خواهرتو تو تاکسی گاییدم راننده هم پیاده شد فیلم گرفت بعد پخش کرد تو کانال محله",
    "مادرتو انقدر گاییدم که کسش بوی کیر کهنه میده حتی با آب ژاول هم پاک نمیشه",
    "ننتو بردم ویلای شمال سه روز گاییدم بعد گذاشتم بره خونه با شکم پر از اب کیر",
    "کیرم تو کون مادرت انقدر کوبیدم که روده‌هاش بیرون زد و با کیرم بازی کرد",
    "بابات مرده هنوزم از قبرش فریاد میزنه که ننتو دیگه نگایید ولی من بیشتر گاییدم",
    "مادرت جنده بین المللیه پاسپورتش پر از مهر کیر کشورهای مختلفه",
    "کس ننتو با بطری نوشابه گاییدم بعد بطری رو شکستم تو رحمش",
    "خواهرتو تو پارک گاییدم بعد گذاشتم سگای ولگرد بیان اب کیرمو از کسش پاک کنن",
    "کیرم تو ناموس خاندانت انقدر گاییدم که دیگه هیچکی تو فامیلت نمیتونه سرش رو بالا بگیره",
    "ننتو تو صف نانوایی گاییدم همه دیدن ولی هیچکی چیزی نگفت چون همه قبلاً گاییده بودنش",
    "مادرتو بستم رو میز بیلیارد گاییدم بعد توپ‌ها رو یکی یکی فرو کردم تو کسش",
    "کیرم تو رحم مادرت جنین سازی کردم حالا ده تا بچه حرومزاده داری که همه شبیه منن",
    "خواهرت جنده‌س هر شب تو خیابون وایمیسه کیر مجانی میخوره بعد میاد خونه گریه میکنه",
    "ننتو انقدر گاییدم که کسش شل شده مثل جوراب کهنه هر کی رد میشه پاش میره توش",
    "مادرتو تو مسجد گاییدم بعد اب کیرمو ریختم رو مهر نمازش تا وقتی سجده میکنه طعم کیرمو بفهمه",
    "کیرم تو کس سیاه و گند مادرت انقدر کوبیدم که بوی گندش تا سه خیابون اونورتر رفته",
    "بابات اومد گفت ننتو دیگه نگا بگو بسه گفتم صبر کن این سری تموم شه بعد نوبت خواهرت",
    "ننتو بردم پشت کوه گاییدم بعد ول کردم بره با پاهای لرزون و کس پر از اب کیر",
    "مادرت جنده بازنشسته‌س ولی هنوز هر شب کیر میخوره چون عادت کرده",
    "کیرم تو نسل مادرت از جد اعلا تا نوه‌های آینده‌ت همه رو گاییدم",
    "خواهرتو تو سینما گاییدم فیلم تموم شد ولی من هنوز داشتم می‌کوبیدم تو کسش",
    "ننتو با جاروبرقی گاییدم بعد مکش رو گذاشتم رو کسش تا اب کیرمو کامل بکشه",
    "مادرتو انقدر گاییدم که رحم ش شده انبار کیر محله هر کی نیاز داره میره اونجا خالی میکنه",
    "کیرم تو کون ننت انقدر فرو کردم که از دهنش بیرون اومد و مجبور شد ببوشه",
    "بابات مرده ولی روحش هنوز میاد بالای سرت و میگه ببین ننتو چجوری دارن می‌گاین",
    "مادرتو تو استخر عمومی گاییدم همه دیدن بعد اب استخر رو با اب کیرم عوض کردم",
    "ننت جنده‌س کارش اینه که کیر خام بفروشه متری حساب میکنه",
    "کیرم تو کس مادرت با سرعت نور کوبیدم تا ناله ش سرعت صوت رد کرد",
    "خواهرتو بستم به تیر چراغ برق گاییدم بعد گذاشتم همه محل بیان تماشا کنن",
    "مادرتو انقدر گاییدم که دیگه کسش بسته نمیشه باید با چسب زخم ببندتش",
    "ننتو تو صف عابربانک گاییدم همه دیدن ولی کسی اعتراض نکرد چون نوبتشون بود",
    "کیرم تو رحم مادرت بمب اتمی منفجر کردم حالا نسلت رادیواکتیوه",
    "بابات اومد التماس کرد ننتو نگا گفتم اول تو رو بگام بعد تصمیم میگیرم",
    "مادرت جنده فصلیه تابستون‌ها بیشتر کار میکنه چون هوا گرمه و کیرها بیشتر وایمیسن",
    "کس ننتو با مته برقی سوراخ کردم بعد کیرمو جای مته گذاشتم",
    "خواهرتو تو اتوبوس گاییدم راننده مسیر رو عوض کرد تا بیشتر طول بکشه",
    "کیرم تو ناموس ابجیت انقدر گاییدم که دیگه حتی سگای محل هم بهش نزدیک نمیشن",
    "ننتو بردم جنگل گاییدم بعد گذاشتم خرس بیاد اب کیرمو از کسش پاک کنه",
    "مادرتو انقدر گاییدم که شکمش باد کرده فکر میکنه حامله‌س ولی فقط پر از اب کیره",
    "کیرم تو کس اجداد ننت همه قبرستون اجدادت رو گاییدم یکی یکی",
    "خواهرت جنده‌س هر ماه یه کیر جدید میگیره ولی هیچکدومش نمیمونه چون کسش شله",
    "ننتو تو حموم خونه گاییدم بعد آب گرم رو بستم و گذاشتم با اب کیرم دوش بگیره",
    "مادرتو بستم رو چرخ خیاطی گاییدم بعد پدال رو فشار دادم تا کیرم بره جلو عقب",
    "کیرم تو کون مادرت انقدر کوبیدم که از دهنش فحش ناموسی اومد بیرون",
    "بابات مرده هنوزم تو خواب میاد میگه ننتو بسه دیگه گاییدی ولی من بیشتر می‌گام",
    "مادرت جنده حرفه‌ایه کارنامه ش پر از کیرهای مختلفه از سرباز تا ژنرال",
    "کس ننتو با آچار فرانسه باز کردم بعد کیرمو جای مهره گذاشتم سفت کردم",
    "خواهرتو تو پشت بام گاییدم همسایه‌ها دیدن بعد همه اومدن صف بستن",
    "ننتو انقدر گاییدم که دیگه راه رفتن بلد نیست فقط می‌تونه چهار دست و پا بره",
    "کیرم تو رحم مادرت مزرعه کیر کاشتم حالا هر روز محصول جدید میده",
    "مادرتو تو صف نانوایی سنگک گاییدم بعد نان داغ رو گذاشتم رو کسش تا بپزه",
    "ننت جنده‌س قیمتش متری حساب میشه هر سانتی متر کیر یه قیمت جدا داره",
    "کیرم تو کس سیاه مادرت انقدر کوبیدم که رنگ کیرم سیاه شد از بوی گندش",
    "خواهرتو بستم به ستون خونه گاییدم بعد ستون ترک برداشت از فشار کیرم",
    "مادرتو انقدر گاییدم که رحمش شده تونل زمان هر کی میره توش برمیگرده به دوران حجر",
    "ننتو تو پارکینگ عمومی گاییدم همه ماشین‌ها بوق زدن از شدت ناله‌ش",
    "کیرم تو ناموس خاندانت بمب خوشه‌ای منفجر کردم همه فامیلت تکه‌تکه شدن",
    "بابات اومد گفت حداقل خواهرتو نگا گفتم نوبت ش هم میرسه نوبتی هستش",
    "مادرت جنده بازنشسته ولی هنوز پاره وقت کار میکنه چون حقوق بازنشستگی کافیش نیست",
    "کس ننتو با دریل صنعتی سوراخ کردم بعد کیرمو جای مته گذاشتم روشن کردم",
    "خواهرتو تو آسانسور گاییدم آسانسور خراب شد سه ساعت گیر کردیم من داشتم می‌کوبیدم",
    "ننتو انقدر گاییدم که کسش شده مثل غار علیصدر همه میرن بازدید کنن",
    "کیرم تو کون ننت انقدر فرو کردم که از گلوش بیرون اومد و مجبور شد قورت بده",
    "مادرتو تو حیاط خونه گاییدم همسایه‌ها از پشت دیوار تماشا کردن و دست زدن",
    "ننت جنده‌س کارش اینه که کیرهای مونده از شب قبل رو صبح‌ها تمیز کنه",
    "کیرم تو رحم مادرت نیروگاه هسته‌ای ساختم حالا هر بار که میگام برق کل شهر قطع میشه",
    "خواهرتو بستم به درخت کاج گاییدم بعد شیره درخت با اب کیرم قاطی شد",
    "مادرتو انقدر گاییدم که دیگه حتی کرم‌های خاکی هم از کسش فرار میکنن",
    "ننتو تو صف پمپ بنزین گاییدم همه دیدن ولی کسی چیزی نگفت چون همه منتظر نوبت بودن",
    "کیرم تو کس اجداد مادرت قبرستون اجدادت رو تبدیل کردم به پارکینگ کیر",
    "بابات مرده ولی هنوزم از قبرش ناله میکنه که ننتو بسه دیگه گاییدی",
    "مادرت جنده فصلیه زمستون‌ها کمتر کار میکنه چون هوا سرده و کیرها جمع میشن",
    "کس ننتو با اره برقی بریدم بعد کیرمو جای اره گذاشتم و ادامه دادم",
    "خواهرتو تو پشت تراکتور گاییدم کشاورز داشت شخم میزد من هم داشتم می‌کوبیدم",
    "ننتو انقدر گاییدم که شکمش شده مثل بادکنک هر لحظه ممکنه بترکه از اب کیر",
    "کیرم تو ناموس ابجیت انقدر گاییدم که دیگه حتی مادر بزرگت هم خجالت میکشه",
    "مادرتو تو سالن ورزشی گاییدم همه داشتن ورزش میکردن من داشتم ننتو نابود میکردم",
    "ننت جنده‌س هر شب یه کیر جدید تست میکنه مثل آزمایشگاه کنترل کیفیت",
    "کیرم تو کون مادرت انقدر کوبیدم که روده‌هاش اومد بیرون و دور کیرم پیچید",
    "خواهرتو بستم به میله پرچم گاییدم بعد پرچم رو بالا بردم همه دیدن",
    "مادرتو انقدر گاییدم که رحمش شده فرودگاه کیر هر کی میخواد میتونه فرود بیاد",
    "ننتو تو صف خودپرداز گاییدم کارت کشید و موجودی حسابش پر از اب کیر شد",
    "کیرم تو کس سیاه و گند ننت انقدر کوبیدم که بوی گندش ماهواره ها رو مختل کرد",
    "بابات اومد التماس کرد که حداقل مادربزرگتو نگا گفتم اونم تو لیسته نوبتی",
    "مادرت جنده حرفه‌ایه رزومه‌ش پر از پروژه های موفق کیر خوردن از سال ۱۳۵۷ تا حالا",
    "کس ننتو با جک هیدرولیک باز کردم بعد کیرمو گذاشتم و جک رو بالا بردم",
    "خواهرتو تو پشت وانت گاییدم راننده داشت بار میبرد من هم داشتم بار ناموستو خالی میکردم",
    "ننتو انقدر گاییدم که دیگه نمیتونه بنشینه فقط باید وایسه یا دراز بکشه",
    "کیرم تو رحم مادرت کارخونه تولید حرومزاده راه انداختم شیفت شبانه هم داره",
    "مادرتو تو کتابخونه عمومی گاییدم همه داشتن کتاب میخوندن من داشتم ننتو میگاییدم",
    "ننت جنده‌س قیمتش با نرخ دلار حساب میشه هر بار که دلار میره بالا کیر بیشتری میخوره",
    "کیرم تو ناموس خاندانت زلزله ۸ ریشتری ایجاد کردم همه فامیلت زیر آوار رفتن",
    "خواهرتو بستم به نرده پارک گاییدم بعد بچه‌ها داشتن بازی میکردن من داشتم می‌کوبیدم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل توحید ترافیک کیر توش سنگینه",
    "ننتو تو صف نان بربری گاییدم نانوا اومد گفت نوبت تموم شد ولی من هنوز داشتم می‌کوبیدم",
    "کیرم تو کون ننت انقدر فرو کردم که از بینی ش بیرون اومد و عطسه کرد",
    "بابات مرده هنوزم تو عالم برزخ داره التماس میکنه که ننتو بسه دیگه",
    "مادرت جنده بین المللیه ویزای شینگن ش پر از مهر کیر کشورهای اروپایی است",
    "کس ننتو با دستگاه فرز تراشیدم بعد کیرمو گذاشتم روش و صیقل دادم",
    "خواهرتو تو پشت کامیون گاییدم راننده داشت بار میبرد من هم داشتم بار کسش رو پر میکردم",
    "ننتو انقدر گاییدم که دیگه حتی با کرم ضد حساسیت هم کسش آروم نمیشه",
    "کیرم تو رحم مادرت سد سازی کردم حالا هر بار که میگام سیل اب کیر راه میفته",
    "مادرتو تو سالن انتظار فرودگاه گاییدم پروازها تاخیر خوردن از شدت ناله‌ش",
    "ننت جنده‌س کارش اینه که کیرهای خسته رو ماساژ بده تا دوباره سفت بشن",
    "کیرم تو کس اجداد ننت همه قبرهای قدیمی رو شکافتم و گاییدم یکی یکی",
    "خواهرتو بستم به تیر برق گاییدم بعد برق گرفت و ناله ش با صدای برق قاطی شد",
    "مادرتو انقدر گاییدم که رحمش شده مثل استادیوم آزادی ظرفیت صد هزار کیر داره",
    "ننتو تو صف میوه فروشی گاییدم میوه فروش اومد گفت خیار تموم شد ولی من هنوز داشتم",
    "کیرم تو ناموس ابجیت سونامی راه انداختم همه فامیلت غرق شدن تو اب کیر",
    "بابات اومد گفت حداقل عمه‌تو نگا گفتم اونم نوبتش میرسه صبر کن",
    "مادرت جنده بازنشسته ولی هنوز مشاوره میده به جنده‌های جوون که چجوری کیر بخورن",
    "کس ننتو با دستگاه جوش برق وصل کردم بعد کیرمو گذاشتم و جوش دادم به رحمش",
    "خواهرتو تو پشت اتوبوس بین شهری گاییدم مسافرا داشتن خواب بودن من داشتم می‌کوبیدم",
    "ننتو انقدر گاییدم که دیگه نمیتونه حرف بزنه فقط ناله میکنه و اب کیر تف میکنه",
    "کیرم تو کون مادرت انقدر کوبیدم که از گوشش بیرون اومد و ناشنوا شد",
    "مادرتو تو پارک جنگلی گاییدم بعد حیوونا اومدن تماشا کردن و یاد گرفتن",
    "ننت جنده‌س هر شب یه کیر جدید میگیره و صبح‌ها گزارش کیفیت میده به رئیس",
    "کیرم تو رحم مادرت پالایشگاه نفت راه انداختم حالا اب کیرم بوی بنزین میده",
    "خواهرتو بستم به نیمکت پارک گاییدم بعد پیرمردا داشتن شطرنج بازی میکردن",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل نیایش همیشه ترافیک کیر داره",
    "ننتو تو صف داروخانه گاییدم دکتر اومد گفت نسخه تموم شد ولی من هنوز داشتم",
    "کیرم تو کس سیاه مادرت انقدر کوبیدم که رنگ پوستم سیاه شد از شدت گندی",
    "بابات مرده هنوزم داره تو خواب‌هات میاد و میگه ببین ننتو چجوری دارن نابود میکنن",
    "مادرت جنده حرفه‌ایه مدرک بین المللی کیر خوردن داره از سازمان جهانی بهداشت",
    "کس ننتو با دستگاه تراش سی ان سی تراشیدم بعد کیرمو دقیقاً اندازه کردم فرو کردم",
    "خواهرتو تو پشت قطار گاییدم قطار داشت میرفت من هم داشتم سرعت می‌کوبیدم",
    "ننتو انقدر گاییدم که دیگه حتی با عمل جراحی هم کسش درست نمیشه",
    "کیرم تو ناموس خاندانت آتشفشان فعال کردم گدازه‌های اب کیر همه جا رو پوشوند",
    "مادرتو تو سالن سینما گاییدم فیلم ترسناک بود ولی ناله ش از فیلم بلندتر بود",
    "ننت جنده‌س کارش اینه که کیرهای خراب رو تعمیر کنه مثل مکانیک کیر",
    "کیرم تو کون ننت انقدر فرو کردم که از نافش بیرون اومد و گره زد",
    "خواهرتو بستم به درخت چنار گاییدم بعد برگ‌ها از شدت لرزش ریختن",
    "مادرتو انقدر گاییدم که رحمش شده مثل فرودگاه امام خمینی پروازهای کیر شبانه روزه",
    "ننتو تو صف بانک گاییدم کارمندا داشتن کار میکردن من داشتم حساب ناموستو خالی میکردم",
    "کیرم تو رحم مادرت معدن الماس کشف کردم حالا هر بار که میگام تکه الماس میاد بیرون",
    "بابات اومد التماس کرد که دیگه بس کن گفتم وقتی نسلت تموم شد حرف حسابتو گوش میدم",
    "مادرت جنده فصلیه بهارها بیشتر کار میکنه چون گل‌ها شکفتن و کیرها هم همینطور",
    "کس ننتو با دستگاه لیزر بریدم بعد کیرمو دقیق جای لیزر گذاشتم و سوزوندم",
    "خواهرتو تو پشت کشتی گاییدم دریا طوفانی بود من هم داشتم طوفان راه مینداختم",
    "ننتو انقدر گاییدم که دیگه نمیتونه آب بخوره چون همه جاش پر از اب کیره",
    "کیرم تو کس اجداد مادرت موزه مردم شناسی راه انداختم همه میان بازدید از قبر گاییده شده",
    "مادرتو تو سالن امتحان گاییدم دانشجوها داشتن امتحان میدادن من داشتم ننتو امتحان میکردم",
    "ننت جنده‌س قیمتش با نرخ طلا حساب میشه هر گرم کیر یه گرم طلا میارزه",
    "کیرم تو ناموس ابجیت سیاهچاله ایجاد کردم همه فامیلت مکیده شدن تو اب کیر",
    "خواهرتو بستم به میله اتوبوس گاییدم مسافرا داشتن ایستاده بودن من داشتم می‌کوبیدم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل رسالت همیشه شلوغه از کیر",
    "ننتو تو صف پست گاییدم مامور پست اومد گفت بسته تموم شد ولی من هنوز داشتم بسته میکردم",
    "کیرم تو کون مادرت انقدر کوبیدم که از چشم‌هاش اشک اب کیر اومد بیرون",
    "بابات مرده هنوزم داره تو برزخ داد میزنه که ننتو بسه دیگه نابود کردی",
    "مادرت جنده بین المللیه پاسپورت ش پر از ویزای کیر کشورهای مختلفه از ژاپن تا برزیل",
    "کس ننتو با دستگاه پرس هیدرولیک له کردم بعد کیرمو گذاشتم و فشار دادم",
    "خواهرتو تو پشت هواپیما گاییدم خلبان داشت پرواز میکرد من هم داشتم اوج می‌گرفتم",
    "ننتو انقدر گاییدم که دیگه حتی با داروهای آرامبخش هم ناله ش قطع نمیشه",
    "کیرم تو رحم مادرت نیروگاه برق آبی راه انداختم حالا اب کیرم برق کل کشور رو تامین میکنه",
    "مادرتو تو سالن کنسرت گاییدم خواننده داشت میخوند من داشتم ننتو به اوج میرسوندم",
    "ننت جنده‌س کارش اینه که کیرهای جدید رو تست کنه و به بقیه جنده‌ها امتیاز بده",
    "کیرم تو کس سیاه و گند مادرت انقدر کوبیدم که سازمان محیط زیست اومد شکایت کرد از آلودگی",
    "خواهرتو بستم به درخت سرو گاییدم بعد کاج‌ها از شدت لرزش افتادن",
    "مادرتو انقدر گاییدم که رحمش شده مثل استادیوم نقش جهان ظرفیت هفتاد هزار کیر داره",
    "ننتو تو صف مترو گاییدم مسافرا داشتن رفت و امد میکردن من داشتم ناموستو زیر و رو میکردم",
    "کیرم تو ناموس خاندانت شهاب سنگ انداختم همه فامیلت سوختتن تو اتش اب کیر",
    "بابات اومد گفت حداقل خالتو نگا گفتم لیست بلنده صبر کن نوبت همه میرسه",
    "مادرت جنده بازنشسته ولی هنوز کلاس آموزش کیر خوردن برای جنده‌های جوون میذاره",
    "کس ننتو با دستگاه برش پلاسما بریدم بعد کیرمو گذاشتم و ذوب کردم تو رحمش",
    "خواهرتو تو پشت هلیکوپتر گاییدم خلبان داشت پرواز میکرد من هم داشتم اوج می‌گرفتم تو کسش",
    "ننتو انقدر گاییدم که دیگه نمیتونه بخنده چون همه عضلاتش از ناله کردن فلج شده",
    "کیرم تو کون ننت انقدر فرو کردم که از دهنش شعر ناموسی اومد بیرون",
    "مادرتو تو پارک ملی گاییدم بعد حیوونات وحشی اومدن صف بستن برای نوبت",
    "ننت جنده‌س هر شب یه کیر جدید میگیره و صبح‌ها آمار میده به اتحادیه جنده‌ها",
    "کیرم تو رحم مادرت پالایشگاه گاز راه انداختم حالا هر بار که میگام گاز کل شهر قطع میشه",
    "خواهرتو بستم به نیمکت ایستگاه اتوبوس گاییدم مسافرا داشتن منتظر بودن من داشتم می‌کوبیدم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل آزادی همیشه پر از کیرهای منتظره",
    "ننتو تو صف نانوایی سنگک گاییدم نانوا اومد گفت آتش تموم شد ولی من هنوز داشتم اتش میزدم",
    "کیرم تو کس اجداد ننت همه اسکلت‌های قدیمی رو گاییدم و اب کیرمو ریختم روشون",
    "بابات مرده هنوزم داره تو عالم ارواح التماس میکنه که نسلش رو بسه دیگه نابود نکن",
    "مادرت جنده حرفه‌ایه مدرک دکترای کیر خوردن داره از دانشگاه جنده‌های جهان",
    "کس ننتو با دستگاه فرز انگشتی تراشیدم بعد کیرمو دقیقاً فیت کردم تو رحمش",
    "خواهرتو تو پشت قایق موتوری گاییدم دریا داشت موج میزد من هم داشتم موج راه مینداختم",
    "ننتو انقدر گاییدم که دیگه حتی با تزریق آمپول هم کسش آروم نمیشه از درد",
    "کیرم تو ناموس ابجیت آتش سوزی جنگلی راه انداختم همه فامیلت تو اتش اب کیر سوختن",
    "مادرتو تو سالن تئاتر گاییدم بازیگرا داشتن نقش بازی میکردن من داشتم نقش اصلی رو با ننت بازی میکردم",
    "ننت جنده‌س کارش اینه که کیرهای مریض رو مداوا کنه مثل پزشک متخصص کیر",
    "کیرم تو کون مادرت انقدر کوبیدم که از بینی ش خون اب کیر اومد بیرون",
    "خواهرتو بستم به درخت بید گاییدم بعد شاخه‌ها از شدت لرزش شکستن",
    "مادرتو انقدر گاییدم که رحمش شده مثل فرودگاه مهرآباد پروازهای کیر شبانه روز بدون توقف",
    "ننتو تو صف اداره پست گاییدم مامور اومد گفت مرسوله تموم شد ولی من هنوز داشتم مرسوله میکردم",
    "کیرم تو رحم مادرت سد خاکی ساختم حالا هر بار که میگام سیل بنیان کن راه میفته",
    "بابات اومد التماس کرد که حداقل نسل بعدیتو نگا گفتم نسل بعدیت هم از همین اب کیر به وجود میان",
    "مادرت جنده فصلیه پاییزها برگ‌ها میریزن و کیرها هم میریزن تو کسش",
    "کس ننتو با دستگاه واترجت آب فشار قوی شستم بعد کیرمو گذاشتم و با فشار فرو کردم",
    "خواهرتو تو پشت موتور سیکلت گاییدم راننده داشت سرعت میرفت من هم داشتم سرعت می‌کوبیدم",
    "ننتو انقدر گاییدم که دیگه نمیتونه گریه کنه چون همه اشک‌هاش تبدیل به اب کیر شده",
    "کیرم تو کس سیاه مادرت انقدر کوبیدم که ناسا اومد تحقیق کرد روی آلودگی فضایی بوی گندش",
    "مادرتو تو سالن ورزشگاه گاییدم تماشاچی‌ها داشتن تشویق میکردن من داشتم ننتو تشویق میکردم با کیر",
    "ننت جنده‌س قیمتش با نرخ سکه حساب میشه هر سکه بهار آزادی یه کیر کامل",
    "کیرم تو ناموس خاندانت زلزله ۹ ریشتری ایجاد کردم همه فامیلت زیر آوار اب کیر موندن",
    "خواهرتو بستم به میله مترو گاییدم مسافرا داشتن ایستاده بودن من داشتم ناموستو زیر پا له میکردم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل حکیم همیشه شلوغ از کیرهای عجول",
    "ننتو تو صف نانوایی تافتون گاییدم نانوا اومد گفت آرد تموم شد ولی من هنوز داشتم آرد میکردم ناموستو",
    "کیرم تو کون ننت انقدر فرو کردم که از گوشش صدای فحش ناموسی اومد بیرون",
    "بابات مرده هنوزم داره تو برزخ داد میزنه که دیگه بس کن نسلمو تموم کردی",
    "مادرت جنده بین المللیه ویزای آمریکا ش پر از مهر کیر ایالت‌های مختلفه",
    "کس ننتو با دستگاه برش لیزری دقیق بریدم بعد کیرمو میلیمتری جاگذاری کردم",
    "خواهرتو تو پشت کشتی باری گاییدم بارها داشتن جابجا میشدن من هم داشتم بار کسش رو جابجا میکردم",
    "ننتو انقدر گاییدم که دیگه حتی با خواب مصنوعی هم ناله ش قطع نمیشه",
    "کیرم تو رحم مادرت نیروگاه خورشیدی راه انداختم حالا هر بار که میگام برق از اب کیر تولید میشه",
    "مادرتو تو سالن کنفرانس گاییدم سخنران داشت حرف میزد من داشتم با ننت کنفرانس خصوصی میذاشتم",
    "ننت جنده‌س کارش اینه که کیرهای قدیمی رو بازسازی کنه مثل مرمت کار آثار باستانی",
    "کیرم تو کس اجداد مادرت موزه عبرت راه انداختم همه میان ببینن چجوری گاییده شدن",
    "خواهرتو بستم به درخت نارون گاییدم بعد میوه‌ها از شدت لرزش افتادن رو زمین",
    "مادرتو انقدر گاییدم که رحمش شده مثل استادیوم آزادی در روز دربی ظرفیت کامل از کیر",
    "ننتو تو صف داروخانه شبانه گاییدم داروساز اومد گفت دارو تموم شد ولی من هنوز داشتم دارو میدادم",
    "کیرم تو ناموس ابجیت آتشفشان آتشفشانی راه انداختم گدازه‌های داغ اب کیر همه جا رو پوشوند",
    "بابات اومد گفت حداقل نسل آینده‌تو نجات بده گفتم نسل آینده‌ت هم از کیر من به وجود میان حرومزاده‌ان",
    "مادرت جنده بازنشسته ولی هنوز به عنوان مشاور عالی اتحادیه جنده‌های ایران فعالیت میکنه",
    "کس ننتو با دستگاه پرس گرم فشرده کردم بعد کیرمو گذاشتم و با حرارت جوش دادم",
    "خواهرتو تو پشت هواپیمای مسافربری گاییدم مهماندارا داشتن سرویس میدادن من داشتم سرویس ناموستو میدادم",
    "ننتو انقدر گاییدم که دیگه نمیتونه نفس بکشه چون همه ریه هاش پر از بوی کیره",
    "کیرم تو کون مادرت انقدر کوبیدم که از دهنش خون و اب کیر با هم اومد بیرون",
    "مادرتو تو پارک شهر گاییدم بعد خانواده‌ها داشتن پیک نیک میکردن من داشتم پیک نیک ناموسی میذاشتم",
    "ننت جنده‌س هر شب یه کیر جدید تست میکنه و به سیستم امتیازدهی جنده‌ها نمره میده",
    "کیرم تو رحم مادرت پالایشگاه نفت خام راه انداختم حالا اب کیرم بوی نفت خام میده و قابل صادراته",
    "خواهرتو بستم به نیمکت پارک بازی گاییدم بچه‌ها داشتن سرسره میرفتن من داشتم سرسره ناموسی میرفتم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل آرش همیشه پر از کیرهای در حال عبوره",
    "ننتو تو صف نانوایی لواش گاییدم نانوا اومد گفت خمیر تموم شد ولی من هنوز داشتم خمیر میکردم ناموستو",
    "کیرم تو کس سیاه و گند ننت انقدر کوبیدم که سازمان ملل اومد قطعنامه داد علیه آلودگی ناموسی",
    "بابات مرده هنوزم داره تو عالم ارواح گریه میکنه که ننتو اینجوری نابود کردن",
    "مادرت جنده حرفه‌ایه مدرک فوق دکترای علوم کیر خوردن داره از آکادمی جنده‌های جهان",
    "کس ننتو با دستگاه تراش دقیق سی ان سی تراشیدم بعد کیرمو با تلورانس صفر فرو کردم",
    "خواهرتو تو پشت قطار سریع السیر گاییدم قطار داشت رکورد میزد من هم داشتم رکورد می‌کوبیدم",
    "ننتو انقدر گاییدم که دیگه حتی با مرگ هم ناله ش تموم نمیشه روحش هم داره ناله میکنه",
    "کیرم تو ناموس خاندانت شهاب سنگ آسمانی انداختم همه فامیلت تو گودال اب کیر دفن شدن",
    "مادرتو تو سالن اپرا گاییدم خواننده‌ها داشتن آواز میخوندن من داشتم با ننت دوئت ناموسی میخوندم",
    "ننت جنده‌س کارش اینه که کیرهای خسته و شکسته رو دوباره احیا کنه مثل بخش اورژانس کیر",
    "کیرم تو کون ننت انقدر فرو کردم که از چشم‌هاش اب کیر مثل اشک جاری شد",
    "خواهرتو بستم به درخت کاج نوئل گاییدم بعد کریسمس ناموسی براتون رقم زدم",
    "مادرتو انقدر گاییدم که رحمش شده مثل فرودگاه جده پروازهای کیر حجی و عمره‌ای شبانه روزه",
    "ننتو تو صف اداره برق گاییدم کارمندا داشتن قبض میدادن من داشتم قبض ناموستو صادر میکردم",
    "کیرم تو رحم مادرت سد بتنی عظیمی ساختم حالا هر بار که میگام سیلاب اب کیر کل استان رو میگیره",
    "بابات اومد آخرین التماسش رو کرد که دیگه بس کن گفتم وقتی آخرین نسلت هم گاییده شد حرفتو گوش میدم",
    "مادرت جنده فصلیه زمستون‌ها کیرها جمع میشن تو کسش مثل پناهگاه زمستونی",
    "کس ننتو با دستگاه واترجت فشار هزار بار شستم بعد کیرمو با تمام قدرت تا ته فرو کردم",
    "خواهرتو تو پشت جت خصوصی گاییدم خلبان داشت پرواز میکرد من هم داشتم پرواز ناموسی میرفتم",
    "ننتو انقدر گاییدم که دیگه نمیتونه بمیره چون مرگ هم از کسش فرار کرده",
    "کیرم تو کس اجداد مادرت گورستان بین المللی راه انداختم همه جهان میان زیارت قبرهای گاییده شده",
    "مادرتو تو سالن دادگاه گاییدم قاضی داشت رای میداد من داشتم رای نهایی رو با کیرم صادر میکردم",
    "ننت جنده‌س قیمتش با نرخ بیت کوین حساب میشه هر ساتوشی یه میلیمتر کیر",
    "کیرم تو ناموس ابجیت سیاهچاله کلان جرم ایجاد کردم همه فامیلت تا ابد مکیده شدن تو تاریکی اب کیر",
    "خواهرتو بستم به میله اتوبوس بی آر تی گاییدم مسافرا داشتن نگاه میکردن من داشتم نمایش ناموسی میدادم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل نیایش در ساعت شلوغی همیشه قفل از کیر",
    "ننتو تو صف نانوایی بربری مخصوص گاییدم نانوا اومد گفت تنور خاموش شد ولی من هنوز داشتم تنور ناموسی روشن میکردم",
    "کیرم تو کون مادرت انقدر کوبیدم که از نافش اب کیر مثل فواره بیرون زد",
    "بابات مرده هنوزم داره تو برزخ با فرشته‌ها بحث میکنه که چرا ننتو اینجوری گاییدن",
    "مادرت جنده بین المللیه پاسپورت شengen ش پر از مهر کیر از نروژ تا یونان",
    "کس ننتو با دستگاه برش پلاسمای صنعتی بریدم بعد کیرمو ذوب شده جاگذاری کردم تو رحمش",
    "خواهرتو تو پشت زیردریایی گاییدم کاپیتان داشت غوطه میخورد من هم داشتم غوطه ناموسی میخوردم",
    "ننتو انقدر گاییدم که دیگه حتی فرشتگان مرگ هم جرات نمیکنن نزدیک بشن از بوی کیر",
    "کیرم تو رحم مادرت نیروگاه همجوشی هسته‌ای راه انداختم حالا هر ارگاسم یه انفجار کوچیک هسته‌ای",
    "مادرتو تو سالن مجلس گاییدم نمایندگان داشتن نطق میکردن من داشتم نطق ناموسی با کیرم ایراد میکردم",
    "ننت جنده‌س کارش اینه که کیرهای تاریخ ساز رو ثبت کنه مثل موزه دار آثار ناموسی",
    "کیرم تو کس سیاه مادرت انقدر کوبیدم که یونسکو اومد این بوی گند رو به عنوان میراث ناملموس ثبت کرد",
    "خواهرتو بستم به درخت چنار صد ساله گاییدم بعد درخت از شدت لرزش ریشه کن شد",
    "مادرتو انقدر گاییدم که رحمش شده مثل استادیوم ومبلی ظرفیت نود هزار کیر در بازی فینال",
    "ننتو تو صف اداره آب و فاضلاب گاییدم کارمندا داشتن قبض آب میدادن من داشتم قبض اب کیر صادر میکردم",
    "کیرم تو ناموس خاندانت شهاب سنگ غول پیکر انداختم گودال اب کیر به اندازه یک شهر درست شد",
    "بابات اومد آخرین نفسش رو کشید و گفت حداقل یه نسل رو نگه دار گفتم همه نسل‌ها در صف گاییده شدنن",
    "مادرت جنده بازنشسته ولی هنوز به عنوان استاد تمام دانشگاه جنده‌شناسی تدریس میکنه",
    "کس ننتو با دستگاه پرس هزار تنی فشرده کردم بعد کیرمو گذاشتم و با تمام قدرت فرو کردم",
    "خواهرتو تو پشت موشک فضایی گاییدم ناسا داشت پرتاب میکرد من هم داشتم پرتاب ناموسی میکردم",
    "ننتو انقدر گاییدم که دیگه حتی خداوند هم از رحمتش گذشته و گفته این یکی رو بسپار به کیر",
    "کیرم تو کون ننت انقدر فرو کردم که از دهنش آیات ناموسی نازل شد",
    "مادرتو تو پارک ملی گلستان گاییدم بعد همه حیوانات نادر اومدن تماشای انقراض ناموسی",
    "ننت جنده‌س هر شب یه کیر جدید میگیره و صبح‌ها گزارش جامع به سازمان جهانی جنده‌ها میده",
    "کیرم تو رحم مادرت پالایشگاه عظیم نفت و گاز راه انداختم حالا اب کیرم صادر میشه به کل خاورمیانه",
    "خواهرتو بستم به نیمکت ایستگاه قطار گاییدم مسافرا داشتن سوار میشدن من داشتم سوار ناموستو میشدم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل توحید در اوج ترافیک قفل کامل از کیر",
    "ننتو تو صف نانوایی سنگک آتشی گاییدم نانوا اومد گفت آتش خاموش شد ولی من هنوز داشتم آتش ناموسی روشن نگه میداشتم",
    "کیرم تو کس اجداد ننت گورستان تمدن‌های باستانی راه انداختم همه باستان شناسان میان حفاری اب کیر",
    "بابات مرده هنوزم داره تو عالم ارواح با پیامبرها بحث میکنه که چرا نسلش اینجوری نابود شد",
    "مادرت جنده حرفه‌ایه مدرک نوبل علوم کیر خوردن داره از آکادمی سلطنتی جنده‌های جهان",
    "کس ننتو با دستگاه برش لیزری فوق دقیق بریدم بعد کیرمو با دقت نانومتری جاگذاری کردم",
    "خواهرتو تو پشت شاتل فضایی گاییدم ناسا داشت به فضا میرفت من هم داشتم به اوج ناموسی میرفتم",
    "ننتو انقدر گاییدم که دیگه حتی ابلیس هم گفته این یکی رو از من هم جلو زده تو گاییدن",
    "کیرم تو ناموس ابجیت سیاهچاله ابر پرجرم ایجاد کردم همه فامیلت تا ابدیت مکیده شدن تو اب کیر مطلق",
    "مادرتو تو سالن سازمان ملل گاییدم نمایندگان داشتن قطعنامه میدادن من داشتم قطعنامه نهایی ناموسی صادر میکردم با کیر",
    "ننت جنده‌س کارش اینه که کیرهای افسانه‌ای رو کاتالوگ کنه مثل کتابدار کتابخانه بزرگ ناموس",
    "کیرم تو کون مادرت انقدر کوبیدم که از گوش‌هاش اب کیر مثل رودخانه جاری شد",
    "خواهرتو بستم به درخت سرو هزار ساله گاییدم بعد درخت از شدت لرزش خشکید و مرد",
    "مادرتو انقدر گاییدم که رحمش شده مثل فرودگاه هیترو لندن شلوغ‌ترین فرودگاه کیر جهان",
    "ننتو تو صف اداره گاز گاییدم کارمندا داشتن قبض گاز میدادن من داشتم قبض گاز اب کیر صادر میکردم",
    "کیرم تو رحم مادرت سد عظیم سه دره ساختم حالا هر ارگاسم سیلابی به اندازه یک رودخانه راه میفته",
    "بابات اومد آخرین التماس تاریخی ش رو کرد گفتم تاریخ نسلت با کیر من نوشته میشه و تموم میشه",
    "مادرت جنده فصلیه بهارها گل میده و کیرها مثل زنبور میان شهد کسش رو می‌مکِن",
    "کس ننتو با دستگاه واترجت فشار هزار بار شستم بعد کیرمو با تمام قدرت تا ته فرو کردم",
    "خواهرتو تو پشت سفینه بین ستاره‌ای گاییدم کاپیتان داشت به کهکشان دیگه میرفت من هم داشتم کهکشان ناموسی کشف میکردم",
    "ننتو انقدر گاییدم که دیگه حتی خود کیر هم خسته شده ولی من هنوز ادامه میدم تا نسلت محو بشه",
    "کیرم تو کس سیاه و گند مادرت انقدر کوبیدم که سازمان حفاظت از محیط زیست جهانی اومد منطقه رو قرنطینه کرد",
    "مادرتو تو سالن تالار وحدت گاییدم ارکستر داشت سمفونی میزد من داشتم سمفونی ناموسی با کیرم اجرا میکردم",
    "ننت جنده‌س قیمتش با نرخ طلای جهانی حساب میشه هر انس طلا یه کیر کامل با اب",
    "کیرم تو ناموس خاندانت شهاب سنگ قاتل دینوساورها انداختم عصر یخبندان اب کیر شروع شد",
    "خواهرتو بستم به میله قطار شهری گاییدم مسافرا داشتن نگاه میکردن من داشتم تاریخ ناموسی رقم میزدم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل کونگروس همیشه پر از کیرهای بین المللی",
    "ننتو تو صف نانوایی تافتون سنتی گاییدم نانوا اومد گفت خمیر ور اومد ولی من هنوز داشتم خمیر ناموسی میگرفتم",
    "کیرم تو کون ننت انقدر فرو کردم که از بینی ش اب کیر مثل فواره آب بازی بیرون زد",
    "بابات مرده هنوزم داره تو برزخ با همه پیامبران و امامان بحث میکنه که چرا ننتو اینجوری تموم کردن",
    "مادرت جنده بین المللیه پاسپورت ش پر از مهر کیر از قطب شمال تا قطب جنوب",
    "کس ننتو با دستگاه برش پلاسمای فوق پیشرفته بریدم بعد کیرمو در حالت پلاسما جاگذاری کردم",
    "خواهرتو تو پشت سفینه اوریون گاییدم ناسا داشت به ماه میرفت من هم داشتم به ماه ناموسی میرفتم",
    "ننتو انقدر گاییدم که دیگه حتی خود مرگ هم اومده التماس میکنه که بسه دیگه این یکی رو تموم کردی",
    "کیرم تو رحم مادرت نیروگاه همجوشی هسته‌ای راه انداختم حالا هر ارگاسم یه ستاره جدید روشن میکنه",
    "مادرتو تو سالن مجمع عمومی سازمان ملل گاییدم همه کشورها داشتن رای میدادن من داشتم رای نهایی رو با کیرم میدادم",
    "ننت جنده‌س کارش اینه که کیرهای افسانه‌ای تاریخ رو بایگانی کنه مثل آرشیو ملی ناموس جهان",
    "کیرم تو کس اجداد مادرت گورستان تمدن بشری راه انداختم همه باستان شناسان جهان میان حفاری اب کیر اجدادت",
    "خواهرتو بستم به درخت انجیر معابد گاییدم بعد درخت از شدت لرزش میوه‌هاش همه ریختن",
    "مادرتو انقدر گاییدم که رحمش شده مثل فرودگاه هارتسفیلد آتلانتا شلوغ‌ترین فرودگاه کیر روی زمین",
    "ننتو تو صف اداره مخابرات گاییدم کارمندا داشتن سیم کارت میدادن من داشتم سیم کارت ناموسی فعال میکردم",
    "کیرم تو ناموس ابجیت سیاهچاله کلان جرم کهکشانی ایجاد کردم همه فامیلت تا ابدیت مطلق مکیده شدن",
    "بابات اومد آخرین حرفش رو زد و گفت حداقل یه نفر از نسلمو نگه دار گفتم همه در صف نهایی گاییده شدنن و هیچکس باقی نمیمونه",
    "مادرت جنده بازنشسته ولی هنوز به عنوان رئیس افتخاری اتحادیه جهانی جنده‌ها فعالیت میکنه و سخنرانی میده",
    "کس ننتو با دستگاه پرس ده هزار تنی فشرده کردم بعد کیرمو گذاشتم و با نیروی یک زلزله فرو کردم",
    "خواهرتو تو پشت موشک فالکون گاییدم اسپیس ایکس داشت به مریخ میرفت من هم داشتم به مریخ ناموسی میرفتم",
    "ننتو انقدر گاییدم که دیگه حتی خود شیطان هم گفته این گاییدن از دست من هم خارج شده و رکورد زده",
    "کیرم تو کون مادرت انقدر کوبیدم که از دهنش کتاب‌های ناموسی نازل شد و نوشته شد",
    "مادرتو تو پارک ژوراسیک گاییدم بعد دایناسورها اومدن تماشای انقراض نهایی ناموسی نسلت",
    "ننت جنده‌س هر شب یه کیر جدید میگیره و صبح‌ها گزارش کامل به شورای امنیت جنده‌های جهان میده",
    "کیرم تو رحم مادرت پالایشگاه عظیم پتروشیمی راه انداختم حالا اب کیرم تبدیل به محصولات پتروشیمی ناموسی میشه و صادر میشه",
    "خواهرتو بستم به نیمکت ایستگاه فضایی بین‌المللی گاییدم فضانوردان داشتن شناور بودن من داشتم شناور ناموسی میکردم",
    "مادرتو انقدر گاییدم که کسش شده مثل تونل مانش همیشه پر از کیرهای اروپایی و آسیایی",
    "ننتو تو صف نانوایی سنگک مخصوص گاییدم نانوا اومد گفت آتش ابدی شد ولی من هنوز داشتم آتش ابدی ناموسی روشن نگه میداشتم",
    "کیرم تو کس سیاه و گند ننت انقدر کوبیدم که یونسکو و سازمان ملل متحد با هم این بوی گند رو به عنوان میراث جهانی ناموسی ثبت کردن",
    "بابات مرده هنوزم داره تو عالم ارواح با همه مقدسین تاریخ بحث میکنه که چرا نسلش با این شدت و حدت نابود شد و هیچ راه نجاتی نموند",
    "مادرت جنده حرفه‌ایه مدرک صلح نوبل در رشته علوم پیشرفته کیر خوردن داره و تندیس ش تو موزه جنده‌های جهان نگهداری میشه",
    "کس ننتو با دستگاه برش لیزری کوانتومی بریدم بعد کیرمو در ابعاد کوانتومی جاگذاری کردم تا در همه جهان‌های موازی هم گاییده بشه"
]
FRIEND_REPLIES_DEFAULT =[
"دلم برات تنگ شده بود امروز ❤️",
"خوشحالم که هستی، روزت چطور بود؟",
"فدات شم، همیشه حواسم بهته",
"دلم می‌خواد بدونم حالت چطوره",
"قربونت برم، دلم برات لک زده",
"امروز یادت افتادم و لبخند زدم",
"خوشحالم که توی زندگیم هستی",
"دلم برات تنگ می‌شه وقتی خبری ازت نیست",
"فدای خنده‌هات بشم",
"همیشه دوست دارم بدونم چیکار می‌کنی",
"قربون انرژی مثبتت",
"دلم می‌خواد بیشتر باهات حرف بزنم",
"خوشحالم که روزت رو با من قسمت می‌کنی",
"فدات شم، حضور تو آرومم می‌کنه",
"یادت نره که برات ارزش قائلم",
"دلم برات تنگ شده بود راستش",
"خوشحالم از اینکه هستی",
"قربون مهربونیت برم",
"همیشه حواسم به حال و هوات هست",
"فدای تو، دلم می‌خواد بدونم چی تو سرته",
"امروز بی‌دلیل یادت کردم",
"خوشحالم که می‌تونم باهات حرف بزنم",
"قربون صمیمیتت",
"دلم برات تنگ می‌شه گاهی",
"فدات شم، انرژی‌ت رو دوست دارم",
"همیشه برام خاصی",
"خوشحالم که توی روزم هستی",
"قربونت، دلم می‌خواد بیشتر ازت بشنوم",
"یادت باشه که برات مهمم",
"دلم برات تنگ شده بود امروز جدی",
"فدای وجودت بشم",
"خوشحالم که حالت خوبه",
"قربون لبخندت",
"همیشه دوست دارم صدات رو بشنوم",
"دلم می‌خواد بدونم چی تو دلت هست",
"فدات شم، حضور تو قشنگه",
"امروز دلم برات تنگ شده بود",
"خوشحالم که باهات رفیقم",
"قربون سادگی و صمیمیتت",
"همیشه حواسم بهته بدون که بگی",
"فدای تو، دلم آروم می‌شه باهات",
"یادت نره که دوستت دارم به سبک خودم",
"دلم برات تنگ می‌شه وقتی طولانی ساکتی",
"خوشحالم که روزای من با تو قشنگ‌تره",
"قربون مهربونیت و درک‌ت",
"همیشه برام آدم خاصی هستی",
"فدات شم، دلم می‌خواد بیشتر ببینمت",
"امروز بی‌دلیل دلم برات تنگ شد",
"خوشحالم که می‌تونم اینجوری باهات راحت باشم",
"قربونت برم، حواست به خودت باشه"
]
CRASH_REPLIES_DEFAULT =[
"قربون اون چشمای قشنگت برم 😍",
"دلم برات ضعف رفت امروز",
"فدای لبخندت بشم، دیوونه‌ت شدم",
"تو قشنگ‌ترین اتفاقی هستی که برام افتاده",
"قربون صدقات، دلم فقط برای تو می‌تپه",
"نمی‌دونم چیکار کردی اینجوری اسیرت شدم",
"فدای اون صدای نازت بشم",
"هر بار که می‌بینمت دلم می‌ریزه",
"قربونت برم، تو فرق داری با همه",
"دلم می‌خواد همیشه کنارم باشی",
"فدای اون نگاه قشنگت",
"تو باعث می‌شی روزام قشنگ‌تر بشه",
"قربون مهربونیت برم، دیوونه‌تم",
"نمی‌تونم بدون فکرت سر کنم",
"فدای اون لبخندت که حالمو خوب می‌کنه",
"تو قشنگ‌ترین آدم دنیایی پیش من",
"قربون صدقه اون چشات برم",
"دلم فقط وقتی آرومه که باهات حرف می‌زنم",
"فدات شم، تو خاص‌ترین کسی هستی که می‌شناسم",
"هر پیامت یه ذره بیشتر عاشقت می‌کنه",
"قربون اون سادگی قشنگت",
"نمی‌دونم چطور اینجوری دلم رو بردی",
"فدای تو، فقط تو تو ذهنمی",
"تو باعث می‌شی همه چیز قشنگ‌تر به نظر بیاد",
"قربون اون خنده‌هات که منو می‌کشه",
"دلم برات تنگ می‌شه حتی اگه یه ساعت خبری نباشه",
"فدای اون انرژی قشنگت بشم",
"تو تنها کسی هستی که اینجوری حالمو بهم می‌ریزی",
"قربون صدقات، دیوونه وار دوستت دارم",
"هر بار اسمت میاد دلم می‌ریزه پایین",
"فدای اون وجود نازت",
"تو قشنگ‌ترین فکری هستی که تو سرم می‌چرخه",
"قربون اون مهربونیت بی‌اندازه‌ت",
"نمی‌تونم جلوی خودمو بگیرم، خیلی دوستت دارم",
"فدات شم، تو آروم‌بخش دل منی",
"دلم می‌خواد بدونم الان چیکار می‌کنی و حالت چطوره",
"قربون اون نگاهت که منو می‌بره",
"تو باعث شدی دوباره به قشنگ بودن دنیا ایمان بیارم",
"فدای اون لبخند ملیحت بشم",
"هر پیامت مثل یه آغوش گرمه برام",
"قربون صدقه اون وجود قشنگت",
"دلم فقط برای تو جا داره",
"فدات شم، تو قشنگ‌ترین اتفاقی",
"نمی‌دونم چیکار کنم با این حسی که بهم دادی",
"قربون اون ساده‌بودن قشنگت برم",
"تو تنها دلیل لبخندای این روزای منی",
"فدای تو، دلم همیشه پیشته",
"هر بار که می‌خندم یاد تو می‌افتم",
"قربون اون چشمایی که باهاشون منو می‌کشی",
"تو قشنگ‌ترین آدمی هستی که تا حالا دیدم"
]
DEFAULT_SECRETARY_MESSAGE ="سلام! در حال حاضر آفلاین هستم و پیام شما را دریافت کردم. در اولین فرصت پاسخ خواهم داد."

FONT_STYLES ={
"stylized":{'0':'𝟎','1':'𝟏','2':'𝟐','3':'𝟑','4':'𝟒','5':'𝟓','6':'𝟔','7':'𝟕','8':'𝟖','9':'𝟗',':':':'},
"monospace":{'0':'𝟶','1':'𝟷','2':'𝟸','3':'𝟹','4':'𝟺','5':'𝟻','6':'𝟼','7':'𝟽','8':'𝟾','9':'𝟿',':':':'},
"normal":{'0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9',':':':'},
"circled":{'0':'⓪','1':'①','2':'②','3':'③','4':'④','5':'⑤','6':'⑥','7':'⑦','8':'⑧','9':'⑨',':':'∶'},
"fullwidth":{'0':'０','1':'１','2':'２','3':'３','4':'４','5':' ۵','6':'۶','7':'۷','8':'۸','9':'۹',':':'：'},
"math_double":{'0':'𝟘','1':'𝟙','2':'𝟚','3':'𝟛','4':'𝟜','5':'𝟝','6':'𝟞','7':'𝟟','8':'𝟠','9':'𝟡',':':':'},
"persian":{'0':'۰','1':'۱','2':'۲','3':'۳','4':'۴','5':'۵','6':'۶','7':'۷','8':'۸','9':'۹',':':':'},
"bubble":{'0':'⓿','1':'❶','2':'❷','3':'❸','4':'❹','5':'❺','6':'❻','7':'❼','8':'❽','9':'❾',':':'∶'},
"math_sans":{'0':'𝟢','1':'𝟣','2':'𝟤','3':'𝟥','4':'𝟦','5':'𝟧','6':'𝟨','7':'𝟩','8':'𝟪','9':'𝟫',':':':'}
}
FONT_KEYS_ORDER =list (FONT_STYLES .keys ())
ALL_CLOCK_CHARS ="".join (set (char for font in FONT_STYLES .values ()for char in font .values ()))
CLOCK_CHARS_REGEX_CLASS =f"[{re .escape (ALL_CLOCK_CHARS )}]"

def bold_msg_text (text :str )->str :
    text =str (text or "")
    if text .startswith ("<b>")or text .startswith ("**"):
        return text 
    return f"<b>{html .escape (text )}</b>"

def _db_derive_key ():
    configured =str (os .environ .get ("DB_ENCRYPTION_KEY","")).strip ()
    raw =(configured or f"{API_HASH }|{BOT_TOKEN }|darkself_db_key").encode ("utf-8")
    return hashlib .sha256 (raw ).digest ()

def _secure_file_permissions (path ):
    try :
        os .chmod (path ,0o600 )
    except Exception :
        pass 

_DB_ENC_PREFIX ="DBENC:"

def _db_encrypt (plaintext ):
    if not plaintext :
        return ""
    if str (plaintext ).startswith (_DB_ENC_PREFIX ):
        return plaintext 
    key =_db_derive_key ()
    salt =secrets .token_bytes (16 )
    nonce =secrets .token_bytes (16 )
    payload =zlib .compress (plaintext .encode ("utf-8"),level =9 )
    counter ,stream =0 ,bytearray ()
    while len (stream )<len (payload ):
        counter +=1 
        stream .extend (hmac .new (key ,salt +nonce +counter .to_bytes (4 ,"big"),hashlib .sha256 ).digest ())
    cipher =bytes (a ^b for a ,b in zip (payload ,stream [:len (payload )]))
    tag =hmac .new (key ,b"DBENC"+salt +nonce +cipher ,hashlib .sha256 ).digest ()[:16 ]
    encoded =base64 .urlsafe_b64encode (salt +nonce +cipher +tag ).decode ().rstrip ("=")
    return _DB_ENC_PREFIX +encoded 

def _db_decrypt (token ):
    if not token :
        return ""
    token =str (token )
    if not token .startswith (_DB_ENC_PREFIX ):
        return token 
    token =token [len (_DB_ENC_PREFIX ):]
    pad =-len (token )%4 
    if pad :
        token +="="*pad 
    try :
        raw =base64 .urlsafe_b64decode (token )
        if len (raw )<48 :
            return ""
        salt ,nonce ,cipher ,tag =raw [:16 ],raw [16 :32 ],raw [32 :-16 ],raw [-16 :]
        key =_db_derive_key ()
        expected_tag =hmac .new (key ,b"DBENC"+salt +nonce +cipher ,hashlib .sha256 ).digest ()[:16 ]
        if not hmac .compare_digest (tag ,expected_tag ):
            logger .error ("DB decrypt: HMAC tag mismatch — data may be tampered or key changed")
            return ""
        counter ,stream =0 ,bytearray ()
        while len (stream )<len (cipher ):
            counter +=1 
            stream .extend (hmac .new (key ,salt +nonce +counter .to_bytes (4 ,"big"),hashlib .sha256 ).digest ())
        decompressed =zlib .decompress (bytes (a ^b for a ,b in zip (cipher ,stream [:len (cipher )])))
        return decompressed .decode ("utf-8")
    except Exception as e :
        logger .error (f"DB decrypt failed: {e }")
        return ""

class DataManager :
    def __init__ (self ,file_path ):
        self .file_path =file_path 
        self .backup_path =f"{file_path }.bak"

        self .tmp_path =f"{file_path }.{os .getpid ()}.tmp"
        self ._needs_save =False 
        self ._last_file_signature =None 
        self ._external_reload_pending =False 
        self .data =self .load_data ()

        if not os .path .exists (self .file_path ):
            self ._needs_save =True 
            self .force_save_sync ()
        self ._last_file_signature =self ._file_signature ()

    def _file_signature (self ):
        try :
            st =os .stat (self .file_path )
            return (st .st_mtime_ns ,st .st_size )
        except Exception :
            return None 

    def _read_json_file (self ,path ):
        with open (path ,'r',encoding ='utf-8')as f :
            return json .load (f )

    def _load_from_backup_or_default (self ):
        if os .path .exists (self .backup_path ):
            try :
                logger .warning (f"Main data file is missing/corrupt. Loading backup: {self .backup_path }")
                return self ._read_json_file (self .backup_path )
            except Exception as e :
                logger .error (f"Backup data file could not be loaded: {e }")
        return self .get_default_data ()

    def _backup_current_file (self ):
        try :
            if os .path .exists (self .file_path )and os .path .getsize (self .file_path )>10 :
                shutil .copy2 (self .file_path ,self .backup_path )
                _secure_file_permissions (self .backup_path )
        except Exception as e :
            logger .warning (f"Could not create database backup: {e }")

    def _repair_sessions_from_users (self ,data ):
        try :
            if not isinstance (data ,dict ):
                return data 
            users =data .setdefault ("users",{})
            sessions =data .setdefault ("sessions",{})
            if not isinstance (users ,dict ):
                data ["users"]={}
                users =data ["users"]
            if not isinstance (sessions ,dict ):
                data ["sessions"]={}
                sessions =data ["sessions"]

            repaired =0 
            for uid_str ,udata in users .items ():
                if not isinstance (udata ,dict ):
                    continue 
                session_string =udata .get ("session_string")or udata .get ("session")or ""
                phone =str (udata .get ("phone")or "").strip ()
                try :
                    uid_val =int (udata .get ("user_id")or uid_str )
                except Exception :
                    continue 
                if session_string and phone and phone not in sessions :
                    enc =session_string if str (session_string ).startswith (_DB_ENC_PREFIX )else _db_encrypt (session_string )
                    sessions [phone ]={"string":enc ,"user_id":uid_val }
                    repaired +=1 
            if repaired :
                logger .warning (f"Repaired {repaired } sessions from users data. Sessions are restored.")
                self ._needs_save =True 
        except Exception as e :
            logger .error (f"Session repair failed: {e }")

        return data 

    def load_data (self ):
        if os .path .exists (self .file_path ):
            try :
                data =self ._read_json_file (self .file_path )
            except Exception as e :
                logger .error (f"Could not load {self .file_path }: {e }")
                return self ._load_from_backup_or_default ()

            try :
                users =data .get ("users",{})
                if isinstance (users ,dict ):
                    for uid ,udata in users .items ():
                        if not isinstance (udata ,dict ):continue 
                        if "settings"not in udata or not isinstance (udata ["settings"],dict ):
                            udata ["settings"]={}
                        if "enemies"in udata and isinstance (udata ["enemies"],list ):
                            if "enemy_list"not in udata or not udata ["enemy_list"]:
                                enemy_ids =[]
                                for x in udata ["enemies"]:
                                    if isinstance (x ,list )and len (x )>0 :enemy_ids .append (x [0 ])
                                    elif isinstance (x ,(int ,str )):enemy_ids .append (int (x ))
                                udata ["enemy_list"]=list (set (enemy_ids ))
                        if "secretary_msg"in udata ["settings"]and "sec_text"not in udata ["settings"]:
                            udata ["settings"]["sec_text"]=udata ["settings"]["secretary_msg"]
            except Exception :
                pass 

            if "users"not in data or not isinstance (data .get ("users"),dict ):data ["users"]={}
            if "sessions"not in data or not isinstance (data .get ("sessions"),dict ):data ["sessions"]={}
            if "admins"not in data or not isinstance (data .get ("admins"),list ):data ["admins"]=[ROOT_ADMIN ]
            if "banned_users"not in data or not isinstance (data .get ("banned_users"),list ):data ["banned_users"]=[]
            if "invalid_sessions"not in data or not isinstance (data .get ("invalid_sessions"),dict ):data ["invalid_sessions"]={}
            if "global_bot_status"not in data :data ["global_bot_status"]=True 
            if "global_fjoin_active"not in data :data ["global_fjoin_active"]=False 
            if "global_fjoin_chats"not in data :data ["global_fjoin_chats"]=[]
            if "server_limits"not in data or not isinstance (data .get ("server_limits"),dict ):
                data ["server_limits"]={"cpu":0 ,"ram_gb":0 }
            if "self_limit"not in data :data ["self_limit"]=0 
            if "admin_reply_targets"not in data or not isinstance (data .get ("admin_reply_targets"),dict ):data ["admin_reply_targets"]={}
            data =self ._repair_sessions_from_users (data )
            data =self ._migrate_encrypt_sessions (data )

            return data 

        return self ._load_from_backup_or_default ()

    def _migrate_encrypt_sessions (self ,data ):
        try :
            migrated =0 
            for phone ,s_data in data .get ("sessions",{}).items ():
                if isinstance (s_data ,dict ):
                    val =s_data .get ("string","")
                    if val and not str (val ).startswith (_DB_ENC_PREFIX ):
                        s_data ["string"]=_db_encrypt (val )
                        migrated +=1 
            for uid_str ,udata in data .get ("users",{}).items ():
                if isinstance (udata ,dict ):
                    val =udata .get ("session_string","")
                    if val and not str (val ).startswith (_DB_ENC_PREFIX ):
                        udata ["session_string"]=_db_encrypt (val )
                        migrated +=1 
            if migrated :
                logger .warning (f"Encrypted {migrated } plaintext session strings found on disk (one-time migration).")
                self ._needs_save =True 
        except Exception as e :
            logger .error (f"Session encryption migration failed: {e }")
        return data 

    def get_default_data (self ):
        return {
        "users":{},"sessions":{},"admins":[ROOT_ADMIN ],"banned_users":[],"invalid_sessions":{},
        "global_bot_status":True ,
        "global_fjoin_active":False ,
        "global_fjoin_chats":[],

        "server_limits":{"cpu":0 ,"ram_gb":0 },
        "self_limit":0 ,
        "admin_reply_targets":{}
        }

    def wipe_all_data (self ):
        self .data =self .get_default_data ()
        self ._needs_save =True 
        self .force_save_sync ()

    def save_data (self ):
        self ._needs_save =True 
        return True 

    def force_save_sync (self ):
        if self ._needs_save :
            try :
                self ._backup_current_file ()
                with open (self .tmp_path ,'w',encoding ='utf-8')as f :
                    json .dump (self .data ,f ,ensure_ascii =False ,separators =(",",":"))
                os .replace (self .tmp_path ,self .file_path )
                _secure_file_permissions (self .file_path )
                self ._last_file_signature =self ._file_signature ()
                self ._needs_save =False 
                _broadcast_database_change ()
            except Exception as e :
                logger .error (f"Error force saving data: {e }")

    def _write_to_file_internal (self ,json_str ):
        try :
            self ._backup_current_file ()
            with open (self .tmp_path ,'w',encoding ='utf-8')as f :
                f .write (json_str )
            os .replace (self .tmp_path ,self .file_path )
            _secure_file_permissions (self .file_path )
            self ._last_file_signature =self ._file_signature ()
            _broadcast_database_change ()
        except Exception as e :
            logger .error (f"Error saving data: {e }")

    def reload_from_disk_if_changed(self, force=False):
        try:
            signature = self._file_signature()
            if not signature:
                return False
            if not force and signature == self._last_file_signature:
                return False
            logger.info("Reloading database from disk")
            self._needs_save = False
            self.data = self.load_data()
            self._last_file_signature = self._file_signature()
            return True
        except Exception as exc:
            logger.error("Database reload failed: %s", exc)
            return False

    async def auto_save_loop (self ):
        while True :
            try :
                await asyncio .sleep (10 )

                current_sig =self ._file_signature ()
                if current_sig and self ._last_file_signature and current_sig !=self ._last_file_signature :
                    reloaded =self .reload_from_disk_if_changed ()
                    if reloaded :
                        self ._external_reload_pending =True 
                        try :
                            load_all_states ()
                            _broadcast_database_change ()
                        except Exception as e :
                            logger .warning (f"Database state refresh failed: {e }")
                    continue 
                if self ._needs_save :
                    self ._needs_save =False 
                    json_str =json .dumps (self .data ,ensure_ascii =False ,separators =(",",":"))
                    await asyncio .get_event_loop ().run_in_executor (cpu_executor ,self ._write_to_file_internal ,json_str )
            except asyncio .CancelledError :
                break 
            except Exception as e :
                logger .error (f"Auto save error: {e }")
                self ._needs_save =True 

    def get_admins (self ):
        return self .data .get ("admins",[ROOT_ADMIN ])

    def add_admin (self ,admin_id ):
        admins =self .get_admins ()
        if admin_id not in admins :
            admins .append (admin_id )
            self .data ["admins"]=admins 
            self .save_data ()
            return True 
        return False 

    def remove_admin (self ,admin_id ):
        admins =self .get_admins ()
        if admin_id in admins and admin_id !=ROOT_ADMIN :
            admins .remove (admin_id )
            self .data ["admins"]=admins 
            self .save_data ()
            return True 
        return False 

    def get_server_limits (self ):
        limits =self .data .setdefault ("server_limits",{})
        if not isinstance (limits ,dict ):
            limits ={}
            self .data ["server_limits"]=limits 
        limits .setdefault ("cpu",0 )
        limits .setdefault ("ram_gb",0 )
        return limits 

    def set_server_limit (self ,kind ,value ):
        limits =self .get_server_limits ()
        limits [kind ]=int (value )
        self .data ["server_limits"]=limits 
        self .save_data ()
        return limits 

    def get_banned_users (self ):
        bans =self .data .setdefault ("banned_users",[])
        try :
            return set (int (x )for x in bans )
        except Exception :
            clean =[]
            for x in bans :
                try :clean .append (int (x ))
                except Exception :pass 
            self .data ["banned_users"]=list (set (clean ))
            return set (self .data ["banned_users"])

    def is_banned (self ,user_id ):
        try :
            return int (user_id )in self .get_banned_users ()
        except Exception :
            return False 

    def ban_user (self ,user_id ):
        uid =int (user_id )
        bans =self .get_banned_users ()
        if uid not in bans :
            bans .add (uid )
            self .data ["banned_users"]=sorted (bans )
            self .save_data ()
            return True 
        return False 

    def unban_user (self ,user_id ):
        uid =int (user_id )
        bans =self .get_banned_users ()
        if uid in bans :
            bans .remove (uid )
            self .data ["banned_users"]=sorted (bans )
            self .save_data ()
            return True 
        return False 

    def mark_invalid_session (self ,user_id ,phone =None ,reason ="invalid"):
        try :
            uid =str (int (user_id ))
            invalids =self .data .setdefault ("invalid_sessions",{})
            invalids [uid ]={"phone":str (phone or ""),"reason":str (reason or "invalid"),"ts":int (time .time ())}
            self .save_data ()
            return True 
        except Exception :
            return False 

    def clear_invalid_session (self ,user_id ):
        try :
            uid =str (int (user_id ))
            invalids =self .data .setdefault ("invalid_sessions",{})
            if uid in invalids :
                invalids .pop (uid ,None )
                self .save_data ()
            return True 
        except Exception :
            return False 

    def is_invalid_session_uid (self ,user_id ):
        try :
            return str (int (user_id ))in self .data .setdefault ("invalid_sessions",{})
        except Exception :
            return False 

    def get_user_data (self ,user_id ):
        user_id_str =str (user_id )
        if user_id_str not in self .data ["users"]:
            self .data ["users"][user_id_str ]={
            "user_id":user_id ,"phone":"","session_string":"",
            "first_name":"","username":"",
            "settings":{
            "font":"stylized","clock":False ,"clock_manual":False ,"bold":False ,"secretary":False ,
            "auto_seen":False ,"pv_lock":False ,"anti_login":False ,"anti_report":False ,
            "typing":False ,"playing":False ,"record_voice":False ,"upload_photo":False ,"watch_gif":False ,
            "copy_mode":False ,"translate":None ,
            "spoiler":False ,"code":False ,"underline":False ,"tag_alert":False ,
            "enemy_active":False ,"friend_active":False ,"crash_active":False ,
            "auto_save":False ,"sec_text":"",
            "anti_delete":False ,"anti_edit":False ,
            "pv_photo":False ,"pv_video":False ,"pv_gif":False ,"pv_voice":False ,
            "pv_music":False ,"pv_sticker":False ,"pv_doc":False ,"pv_loc":False ,"pv_emo":False ,"pv_txt":False ,
            "bio_clock":False ,"bio_date":False ,"bio_date_type":"jalali","bio_font":"stylized",
            "forced_join_active":False ,"dot_commands":False ,
            "filter_words_active":False ,"gradual":False ,
            "self_destruct":False ,"self_destruct_delay":600 ,
            "first_comment":False ,"first_comment_text":"",
            "avatar":False ,"avatar_style":1 ,"avatar_text":"","avatar_prev":"",
            "panel_color":True ,"help_color":True ,
            "self_active":True ,"self_prev_clock":False ,"self_prev_bio_clock":False ,"self_prev_bio_date":False ,
            "twofa_password":""
            },
            "enemy_list":[],"friend_list":[],"crash_list":[],
            "enemy_replies":ENEMY_REPLIES_DEFAULT .copy (),"friend_replies":FRIEND_REPLIES_DEFAULT .copy (),"crash_replies":CRASH_REPLIES_DEFAULT .copy (),
            "muted":[],"timed_muted":[],"blocked_users":[],"reactions":{},"replied_users":[],"forced_join_chats":[],"first_comment_chats":[],"filter_words":[],"wallets":{}
            }
            self .save_data ()
        user_data =self .data ["users"][user_id_str ]
        if not isinstance (user_data .get ("settings"),dict ):
            user_data ["settings"]={}
        if "twofa_password"not in user_data ["settings"]:
            user_data ["settings"]["twofa_password"]=""
            self .save_data ()
        repaired =False 
        for key ,defaults in (("enemy_replies",ENEMY_REPLIES_DEFAULT ),("friend_replies",FRIEND_REPLIES_DEFAULT ),("crash_replies",CRASH_REPLIES_DEFAULT )):
            saved =user_data .get (key )
            valid =[text for text in saved if isinstance (text ,str )and text .strip ()]if isinstance (saved ,list )else []
            effective =valid or defaults .copy ()
            if saved !=effective :
                user_data [key ]=effective 
                repaired =True 
        if repaired :self .save_data ()
        return user_data 

    def update_user_data (self ,user_id ,updates ):
        user_data =self .get_user_data (user_id )
        for k ,v in updates .items ():
            if k =="settings"and isinstance (v ,dict ):
                user_data ["settings"].update (v )
            else :
                user_data [k ]=v 
        self .save_data ()
        return user_data 

    def save_session (self ,phone ,session_string ,user_id ):
        self .clear_invalid_session (user_id )
        encrypted =_db_encrypt (session_string )
        self .data ["sessions"][phone ]={"string":encrypted ,"user_id":user_id }
        self .update_user_data (user_id ,{"phone":phone ,"session_string":encrypted })

    def delete_session (self ,phone ):
        if phone in self .data ["sessions"]:
            uid =self .data ["sessions"][phone ].get ("user_id")
            del self .data ["sessions"][phone ]
            if uid and str (uid )in self .data ["users"]:
                self .data ["users"][str (uid )]["session_string"]=""
            self .save_data ()

    def delete_user_full (self ,user_id ):
        user_id_str =str (user_id )
        if user_id_str in self .data ["users"]:
            phone =self .data ["users"][user_id_str ].get ("phone")
            if phone :self .delete_session (phone )
            del self .data ["users"][user_id_str ]
        self .save_data ()

    def get_all_sessions (self ):
        self ._repair_sessions_from_users (self .data )
        decrypted ={}
        for phone ,s_data in self .data .get ("sessions",{}).items ():
            d =dict (s_data )
            d ["string"]=_db_decrypt (d .get ("string",""))
            decrypted [phone ]=d 
        return decrypted .items ()

    def get_decrypted_session_string (self ,user_id ):
        try :
            raw =self .get_user_data (user_id ).get ("session_string","")
            return _db_decrypt (raw )
        except Exception :
            return ""

    def get_all_users (self ):
        return self .data ["users"]

    def get_self_limit (self ):
        try :
            return max (0 ,int (self .data .get ("self_limit",0 )or 0 ))
        except Exception :
            return 0 

    def set_self_limit (self ,value ):
        try :
            value =max (0 ,int (value ))
        except Exception :
            value =0 
        self .data ["self_limit"]=value 
        self .force_save_sync ()
        return value 

    def has_self_slot (self ,uid ):
        try :
            u =self .data .get ("users",{}).get (str (int (uid )),{})
        except Exception :
            return False 
        return bool (isinstance (u ,dict )and u .get ("session_string"))

    def count_active_selfs (self ):
        admins =set (self .get_admins ())
        admins .add (ROOT_ADMIN )
        banned =self .get_banned_users ()
        used =0 
        for uid_s ,udata in list (self .data .get ("users",{}).items ()):
            try :
                uid =int (uid_s )
            except Exception :
                continue 
            if uid in admins or uid in banned :
                continue 
            if isinstance (udata ,dict )and udata .get ("session_string"):
                used +=1 
        return used 

    def self_limit_status (self ):
        limit =self .get_self_limit ()
        used =self .count_active_selfs ()
        free =None if not limit else max (0 ,limit -used )
        return limit ,used ,free 

    def self_slot_available (self ,uid ):
        try :
            uid =int (uid )
        except Exception :
            return False 
        admins =set (self .get_admins ())
        admins .add (ROOT_ADMIN )
        if uid in admins :
            return True 
        if self .has_self_slot (uid ):
            return True 
        limit =self .get_self_limit ()
        if not limit :
            return True 
        return self .count_active_selfs ()<limit 

    def register_admin_reply_target (self ,message_id ,uid ):
        targets =self .data .setdefault ("admin_reply_targets",{})
        targets [str (message_id )]=int (uid )
        self .save_data ()

    def resolve_admin_reply_target (self ,message_id ):
        targets =self .data .setdefault ("admin_reply_targets",{})
        return targets .get (str (message_id ))

manager_bot =Client ("manager_bot",api_id =API_ID ,api_hash =API_HASH ,bot_token =BOT_TOKEN ,workers =2 ,**_darkself_optional_client_kwargs ())
data_manager =DataManager (DATA_FILE )

# Railway / Linux graceful shutdown
_SHUTDOWN_REQUESTED = False

def _sig_save_exit (signum ,frame ):
    global _SHUTDOWN_REQUESTED
    _SHUTDOWN_REQUESTED = True
    logger .info (
        "[سیستم] دریافت سیگنال %s؛ خاموش‌سازی کنترل‌شده...",
        getattr (signal ,"Signals",lambda x:x )(signum )
    )

try :
    signal .signal (signal .SIGTERM ,_sig_save_exit )
    signal .signal (signal .SIGINT ,_sig_save_exit )
except Exception :
    pass

try :
    signal .signal (signal .SIGHUP ,_sig_save_exit )
except Exception :
    pass

SERVER_CPU_OPTIONS =[1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ]
SERVER_RAM_OPTIONS_GB =[2 ,4 ,6 ,8 ,10 ,12 ,14 ,16 ]
_SERVER_CPU_COUNT =os .cpu_count ()or 1 

_LATEST_CPU_PERCENT =0.0 
_LATEST_PROC_CPU_PERCENT =0.0 
_SERVER_PROCESS =None 

async def cpu_stats_sampler ():
    global _LATEST_CPU_PERCENT ,_LATEST_PROC_CPU_PERCENT ,_SERVER_PROCESS 
    if psutil is None :
        return 
    try :
        _SERVER_PROCESS =psutil .Process (os .getpid ())
        psutil .cpu_percent (interval =None )
        _SERVER_PROCESS .cpu_percent (interval =None )
    except Exception :
        pass 
    while True :
        try :
            await asyncio .sleep (2 )
            _LATEST_CPU_PERCENT =psutil .cpu_percent (interval =None )
            if _SERVER_PROCESS is not None :

                raw =_SERVER_PROCESS .cpu_percent (interval =None )
                try :
                    n_affinity =len (os .sched_getaffinity (0 ))if hasattr (os ,"sched_getaffinity")else _SERVER_CPU_COUNT 
                except Exception :
                    n_affinity =_SERVER_CPU_COUNT 
                _LATEST_PROC_CPU_PERCENT =raw /max (n_affinity ,1 )
        except asyncio .CancelledError :
            break 
        except Exception :
            pass 

def _sharding_enabled_for (cpu_limit ):
    if os .environ .get ("DARKSELF_SHARD","0")!="1":
        return False 
    if cpu_limit <=1 :
        return False 
    if os .environ .get ("DARKSELF_NO_SHARD","0")=="1":
        return False 
    if SHARD_ID is not None :
        return False 
    return True 

def apply_server_limits ():
    global cpu_executor 
    limits =data_manager .get_server_limits ()
    cpu_limit =int (limits .get ("cpu")or 0 )
    ram_limit_gb =int (limits .get ("ram_gb")or 0 )

    if SHARD_ID is not None and SHARD_COUNT >1 :
        core =min (SHARD_ID ,max (_SERVER_CPU_COUNT -1 ,0 ))
        try :
            if hasattr (os ,"sched_setaffinity"):
                os .sched_setaffinity (0 ,{core })
                logger .info (f"[shard-{SHARD_ID }] pinned to core {core } of {SHARD_COUNT } shards")
        except Exception as e :
            logger .warning (f"[shard-{SHARD_ID }] sched_setaffinity failed: {e }")

        try :
            if getattr (cpu_executor ,"_max_workers",None )!=2 :
                old =cpu_executor 
                cpu_executor =concurrent .futures .ThreadPoolExecutor (max_workers =2 )
                old .shutdown (wait =False )
        except Exception :
            pass 

        if ram_limit_gb >0 and _resource_limits is not None :
            try :
                ram_bytes =ram_limit_gb *1024 *1024 *1024 
                
                logger .info (f"RAM target {ram_limit_gb }GB (soft; no RLIMIT_AS)")
            except Exception as e :
                logger .warning (f"[shard-{SHARD_ID }] RAM limit failed: {e }")
        return 

    if _sharding_enabled_for (cpu_limit ):
        n =min (cpu_limit ,_SERVER_CPU_COUNT )

        try :
            if hasattr (os ,"sched_setaffinity"):
                os .sched_setaffinity (0 ,set (range (n )))
        except Exception as e :
            logger .warning (f"[master] sched_setaffinity failed: {e }")

        try :
            if getattr (cpu_executor ,"_max_workers",None )!=2 :
                old =cpu_executor 
                cpu_executor =concurrent .futures .ThreadPoolExecutor (max_workers =2 )
                old .shutdown (wait =False )
        except Exception :
            pass 

        try :
            _shard_init_ipc ()
            _shard_supervisor .resize (n )
            os .environ ["DARKSELF_SHARDING_ACTIVE"]="1"
        except Exception as e :
            logger .error (f"[master] shard supervisor resize failed: {e }")

        if ram_limit_gb >0 and _resource_limits is not None :
            try :
                ram_bytes =ram_limit_gb *1024 *1024 *1024 
                
                logger .info (f"RAM target {ram_limit_gb }GB (soft; no RLIMIT_AS)")
            except Exception as e :
                logger .warning (f"[master] RAM limit failed: {e }")

        try :
            _shard_signal_reload ()
        except Exception :
            pass 
        logger .info (f"[master] شاردینگ فعال: {n } ورکر روی {n } هسته. CPU={cpu_limit }, RAM={ram_limit_gb or 'آزاد'}GB")
        return 

    try :
        if _SHARD_CURRENT_N >0 or _shard_supervisor .workers :
            _shard_supervisor .kill_all ()
            os .environ .pop ("DARKSELF_SHARDING_ACTIVE",None )
    except Exception :
        pass 

    if cpu_limit >0 :
        n =min (cpu_limit ,_SERVER_CPU_COUNT )
        try :
            if hasattr (os ,"sched_setaffinity"):
                os .sched_setaffinity (0 ,set (range (n )))
        except Exception as e :
            logger .warning (f"اعمال محدودیت CPU (affinity) ممکن نشد: {e }")
        try :
            old_executor =cpu_executor 

            if getattr (old_executor ,"_max_workers",None )!=n :
                cpu_executor =concurrent .futures .ThreadPoolExecutor (max_workers =n )
                old_executor .shutdown (wait =False )
        except Exception as e :
            logger .warning (f"تغییر اندازه cpu_executor ممکن نشد: {e }")
    else :
        try :
            if hasattr (os ,"sched_setaffinity"):
                os .sched_setaffinity (0 ,set (range (_SERVER_CPU_COUNT )))
        except Exception :
            pass 

    if ram_limit_gb >0 and _resource_limits is not None :
        try :
            ram_bytes =ram_limit_gb *1024 *1024 *1024 
            logger .info (f"RAM target {ram_limit_gb }GB (soft; no RLIMIT_AS)")
        except Exception as e :
            logger .warning (f"اعمال محدودیت RAM ممکن نشد: {e }")

    logger .info (f"محدودیت سرور اعمال شد (legacy): CPU={cpu_limit or 'آزاد'}, RAM={ram_limit_gb or 'آزاد'}GB")

def get_server_stats_text ():
    limits =data_manager .get_server_limits ()
    cpu_limit =int (limits .get ("cpu")or 0 )
    ram_limit_gb =int (limits .get ("ram_gb")or 0 )

    if psutil is None :
        return (
        "برای نمایش درصد دقیق مصرف CPU/RAM باید کتابخانه psutil نصب شود:\n"
        "`pip install psutil`\n\n"
        f"محدودیت CPU تنظیم‌شده: `{cpu_limit or 'آزاد'}`\n"
        f"محدودیت RAM تنظیم‌شده: `{(str (ram_limit_gb )+' GB')if ram_limit_gb else 'آزاد'}`"
        )

    try :
        cpu_percent =_LATEST_CPU_PERCENT 
        proc_cpu_percent =_LATEST_PROC_CPU_PERCENT 
    except Exception :
        cpu_percent =proc_cpu_percent =0.0 
    try :
        vm =psutil .virtual_memory ()
        ram_used_gb =(vm .total -vm .available )/(1024 **3 )
        ram_total_gb =vm .total /(1024 **3 )
        ram_percent =vm .percent 
    except Exception :
        ram_used_gb =ram_total_gb =ram_percent =0.0 

    text =(
    f"**منابع سرور**\n"
    f"――――――――――――――――\n"
    f"مصرف CPU کل سرور: `{cpu_percent :.1f}%` (از `{_SERVER_CPU_COUNT }` هسته کل)\n"
    f"مصرف CPU همین ربات: `{proc_cpu_percent :.1f}%`\n"
    f"مصرف RAM: `{ram_used_gb :.2f}` از `{ram_total_gb :.2f}` گیگابایت (`{ram_percent :.1f}%`)\n"
    f"――――――――――――――――\n"
    f"محدودیت CPU تنظیم‌شده: `{cpu_limit if cpu_limit else 'آزاد'}`\n"
    f"محدودیت RAM تنظیم‌شده: `{(str (ram_limit_gb )+' GB')if ram_limit_gb else 'آزاد'}`\n"
    )

    try :
        shard_active =_sharding_enabled_for (cpu_limit )and (SHARD_ID is None )
        if shard_active :
            st =_shard_supervisor .status ()if _shard_supervisor else {}
            n_workers =len (st )
            alive =sum (1 for v in st .values ()if v .get ("alive"))
            text +=f"――――――――――――――――\n"
            text +=f"⚡ **شاردینگ فعال**: `{n_workers }` ورکر، `{alive }` زنده\n"
            statuses =_read_all_shard_statuses ()
            total_active_sessions =0 
            for k in sorted (statuses .keys ()):
                info =statuses [k ]
                worker_info =st .get (k ,{})
                pid_str =f"pid={worker_info .get ('pid','?')}"if worker_info .get ("alive")else "dead"
                if info and isinstance (info ,dict ):
                    a =info .get ("active",0 )
                    total_active_sessions +=int (a )
                    text +=f"  • شارد {k }: `{a }` سشن فعال (`{pid_str }`)\n"
                else :
                    text +=f"  • شارد {k }: `—` (`{pid_str }`)\n"
            text +=f"  **مجموع سشن‌های فعال**: `{total_active_sessions }`\n"
        elif SHARD_ID is not None :
            text +=f"――――――――――――――――\n"
            text +=f"⚙ این پروسه ورکر شارد `{SHARD_ID }` از `{SHARD_COUNT }` است\n"
            text +=f"  سشن‌های فعال: `{len (ACTIVE_BOTS )}`\n"
    except Exception :
        pass 

    text +=(
    f"――――――――――――――――\n"
    f"_مصرف CPU هر ۲ ثانیه به‌روز می‌شه؛ بلافاصله بعد از استارت ممکنه چند ثانیه صفر بمونه._\n"
    f"_شاردینگ: وقتی CPU ≥ ۲ باشد، {cpu_limit } پروسه‌ی مستقل روی {cpu_limit } هسته اجرا می‌شود (GIL جدا → موازات واقعی)._"
    )
    return text 

def build_server_status_markup ():
    return InlineKeyboardMarkup ([
    [InlineKeyboardButton ("تنظیم سرور",callback_data ="srvcfg_menu")],
    [InlineKeyboardButton ("بستن",callback_data ="srvcfg_close")]
    ])

def build_server_config_menu_markup ():
    return InlineKeyboardMarkup ([
    [InlineKeyboardButton ("CPU",callback_data ="srvcfg_pick_cpu"),
    InlineKeyboardButton ("RAM",callback_data ="srvcfg_pick_ram")],
    [InlineKeyboardButton ("بازگشت",callback_data ="srvcfg_back")]
    ])

def build_server_cpu_options_markup ():
    limits =data_manager .get_server_limits ()
    current =int (limits .get ("cpu")or 0 )
    rows ,row =[],[]
    for n in SERVER_CPU_OPTIONS :
        label =f"{n } ✓"if n ==current else str (n )
        row .append (InlineKeyboardButton (label ,callback_data =f"srvcfg_setcpu_{n }"))
        if len (row )==4 :
            rows .append (row )
            row =[]
    if row :
        rows .append (row )
    rows .append ([InlineKeyboardButton ("بدون محدودیت"+(" ✓"if current ==0 else ""),callback_data ="srvcfg_setcpu_0")])
    rows .append ([InlineKeyboardButton ("بازگشت",callback_data ="srvcfg_menu")])
    return InlineKeyboardMarkup (rows )

def build_server_ram_options_markup ():
    limits =data_manager .get_server_limits ()
    current =int (limits .get ("ram_gb")or 0 )
    rows ,row =[],[]
    for n in SERVER_RAM_OPTIONS_GB :
        label =f"{n } ✓"if n ==current else str (n )
        row .append (InlineKeyboardButton (label ,callback_data =f"srvcfg_setram_{n }"))
        if len (row )==4 :
            rows .append (row )
            row =[]
    if row :
        rows .append (row )
    rows .append ([InlineKeyboardButton ("بدون محدودیت"+(" ✓"if current ==0 else ""),callback_data ="srvcfg_setram_0")])
    rows .append ([InlineKeyboardButton ("بازگشت",callback_data ="srvcfg_menu")])
    return InlineKeyboardMarkup (rows )

try :
    apply_server_limits ()
except Exception as _e :
    logger .warning (f"اعمال اولیه محدودیت سرور ممکن نشد: {_e }")

ACTIVE_BOTS ={}
STARTING_BOTS =set ()
ORIGINAL_PROFILE_DATA ={}
USER_FONT_CHOICES ,CLOCK_STATUS ,BOLD_MODE_STATUS ={},{},{}
SPOILER_MODE_STATUS ,CODE_MODE_STATUS ,UNDERLINE_MODE_STATUS ={},{},{}
TAG_ALERT_STATUS ={}
SECRETARY_MODE_STATUS ,AUTO_SEEN_STATUS ,PV_LOCK_STATUS ={},{},{}
ACCOUNT_MAINTENANCE_AFTER ={}
ACCOUNT_MAINTENANCE_LIMIT_KIND ={}
FIRST_COMMENT_STATUS ,FIRST_COMMENT_TEXT ,FIRST_COMMENT_CHATS ={},{},{}
FIRST_COMMENT_RECENT ={}
ANTI_LOGIN_STATUS ,TYPING_MODE_STATUS ,PLAYING_MODE_STATUS ={},{},{}
ANTI_REPORT_STATUS ,REPORT_GUARD_UNTIL ,REPORT_GUARD_EVENTS ={},{},{}
RECORD_VOICE_STATUS ,UPLOAD_PHOTO_STATUS ,WATCH_GIF_STATUS ={},{},{}
COPY_MODE_STATUS ,AUTO_TRANSLATE_TARGET ={},{}
AUTO_SAVE_VIEW_ONCE ,CUSTOM_SECRETARY_MESSAGES ={},{}
ANTI_DELETE_STATUS ,ANTI_EDIT_STATUS ={},{}
MESSAGE_TIMELINE_CACHE ={}

MESSAGE_ID_INDEX ={}
TIMELINE_CACHE_LIMIT =80 
TIMELINE_CACHE_TRIM_TO =40 
ANTI_DELETE_MAX_MEDIA_MB =4 
ANTI_DELETE_DISK_LIMIT_MB =120 
ANTI_DELETE_MEDIA_TTL_SECONDS =6 *3600 

RAW_TTL_MEDIA_HINTS ={}
RAW_TTL_MEDIA_HINTS_LIMIT =500 
ANTI_DELETE_MEDIA_TASKS =set ()
ANTI_DELETE_MEDIA_TASK_LIMIT =12 
ANTI_DELETE_MEDIA_SEMAPHORE =None 
DOWNLOAD_TEMP_DIR ="/tmp/darkself_downloads"
DIRECT_DOWNLOAD_MAX_MB =80 
STICKER_SOURCE_MAX_MB =12 
STARTUP_CONCURRENCY =max (2 ,min (8 ,int (os .getenv ("DARKSELF_STARTUP_CONCURRENCY","4"))))
STARTUP_BATCH_PAUSE =float (os .getenv ("DARKSELF_STARTUP_BATCH_PAUSE","0.03"))

BIO_CLOCK_STATUS ,BIO_DATE_STATUS ,BIO_DATE_TYPE ,BIO_FONT_CHOICE ={},{},{},{}

PV_PHOTO_LOCK ,PV_VIDEO_LOCK ,PV_GIF_LOCK ,PV_VOICE_LOCK ={},{},{},{}
PV_MUSIC_LOCK ,PV_STICKER_LOCK ,PV_DOC_LOCK ={},{},{}
PV_LOC_LOCK ,PV_EMO_LOCK ,PV_TXT_LOCK ={},{},{}

ENEMY_LIST ,FRIEND_LIST ,CRASH_LIST ={},{},{}
ENEMY_REPLIES ,FRIEND_REPLIES ,CRASH_REPLIES ={},{},{}
ENEMY_ACTIVE ,FRIEND_ACTIVE ,CRASH_ACTIVE ={},{},{}

MUTED_USERS ,MUTED_UNTIL ,BLOCKED_USERS ={},{},{}
SELF_DESTRUCT_STATUS ,SELF_DESTRUCT_DELAY ={},{}
SCHEDULED_MESSAGE_TASKS =set ()
ROOT_BAN_COMMAND_SEEN ={}
AUTO_REACTION_TARGETS ,USERS_REPLIED_IN_SECRETARY ={},{}

FORCED_JOIN_ACTIVE ,FORCED_JOIN_CHATS ={},{}
LAST_FJOIN_ALERT ={}

DOT_COMMANDS_STATUS ={}
SELF_ACTIVE_STATUS ={}
FILTER_WORDS_ACTIVE ={}
FILTER_WORDS ={}
FILTER_WORDS_NORMALIZED ={}
GRADUAL_MODE_STATUS ={}
TABCHI_BANNER ,TABCHI_BANNER_MEDIA ,TABCHI_REPEATER ={},{},{}
TABCHI_TIMER ,TABCHI_SPEED ={},{}
TABCHI_PV_STATUS ,TABCHI_GP_STATUS ,TABCHI_SMART_STATUS ={},{},{}
TABCHI_PV_COUNT ,TABCHI_GP_COUNT ={},{}
TABCHI_PV_INDEX ,TABCHI_GP_INDEX ={},{}
TABCHI_PV_CHATS_CACHE ,TABCHI_GP_CHATS_CACHE ,TABCHI_MESSAGED_USERS ,TABCHI_LINK_QUEUE ={},{},{},{}

TABCHI_SCAN_SEMAPHORE = asyncio.Semaphore(2)
TABCHI_ACTIVE_LOOP_ID ,TABCHI_REPEATER_LOOP_ID ={},{}
TABCHI_TIMER_MAX =1500 
TABCHI_REPEATER_MAX =1000 
WALLET_SETUP_STATES ={}
INLINE_IDLE_STATE ={"panel":{},"help":{}}
ADMIN_TEXT_RESET_CONFIRMATIONS ={}

def me_cmd (pattern ,flags =0 ):
    compiled =re .compile (pattern ,flags )if isinstance (pattern ,str )else pattern 
    async def func (flt ,client ,message ):
        if not getattr (message ,"text",None ):
            return False 

        is_me =False 
        if getattr (message ,"outgoing",False ):
            is_me =True 
        elif getattr (message ,"from_user",None ):
            if getattr (message .from_user ,"is_self",False ):
                is_me =True 
            elif getattr (client ,"me",None )and message .from_user .id ==client .me .id :
                is_me =True 

        if not is_me :
            return False 

        uid =client .me .id if getattr (client ,"me",None )else message .from_user .id 
        if data_manager .is_banned (uid )or _activation_wait_left (uid )>0 :
            return False 
        raw_clean =message .text .strip ().strip (".").strip ().lower ()
        if not SELF_ACTIVE_STATUS .get (uid ,True )and raw_clean !="سلف روشن":
            return False 
        use_dot =DOT_COMMANDS_STATUS .get (uid ,False )
        text =message .text .strip ()

        if use_dot :
            if text .startswith ("."):
                actual_text =text [1 :].lstrip ()
            elif text .endswith ("."):
                actual_text =text [:-1 ].rstrip ()
            else :
                return False 
        else :
            if text .startswith (".")or text .endswith ("."):
                return False 
            actual_text =text 

        return bool (compiled .search (actual_text ))
    return filters .create (func )

def get_cmd (uid ,text ):
    if _activation_wait_left (uid )>0 :return None 
    text =(text or "").strip ()
    use_dot =DOT_COMMANDS_STATUS .get (uid ,False )
    if use_dot :
        if text .startswith ("."):
            return text [1 :].lstrip ()
        if text .endswith ("."):
            return text [:-1 ].rstrip ()
        return None 
    if text .startswith (".")or text .endswith ("."):
        return None 
    return text 

async def ensure_reply_message (client ,message ):
    rm =getattr (message ,"reply_to_message",None )
    if rm is not None :
        return rm 
    rid =getattr (message ,"reply_to_message_id",None )
    chat =getattr (message ,"chat",None )
    if not rid or not chat :
        return None 
    fetched =None 
    try :
        fetched =await Client .get_messages (client ,chat .id ,int (rid ))
    except Exception :
        try :
            fetched =await client .get_messages (chat .id ,int (rid ))
        except Exception :
            fetched =None 
    if isinstance (fetched ,list ):
        fetched =fetched [0 ]if fetched else None 
    if fetched :
        try :
            message .reply_to_message =fetched 
        except Exception :
            pass 
    return fetched 

def parse_time_duration (text :str ):
    text =(text or "").strip ().lower ().replace ("ي","ی").replace ("ك","ک")
    m =re .search (r"(\d+)\s*(ثانیه|ثانيه|دقیقه|دقيقه|ساعت|روز)",text )
    if not m :
        return None 
    n =int (m .group (1 ))
    unit =m .group (2 )
    if n <=0 :
        return None 
    if "ث"in unit :
        return min (n ,86400 *7 )
    if "دقی"in unit or "دقي"in unit :
        return min (n *60 ,86400 *30 )
    if "ساعت"in unit :
        return min (n *3600 ,86400 *30 )
    if "روز"in unit :
        return min (n *86400 ,86400 *30 )
    return None 

def format_duration (seconds :int ):
    seconds =int (seconds or 0 )
    if seconds %86400 ==0 and seconds >=86400 :
        return f"{seconds //86400 } روز"
    if seconds %3600 ==0 and seconds >=3600 :
        return f"{seconds //3600 } ساعت"
    if seconds %60 ==0 and seconds >=60 :
        return f"{seconds //60 } دقیقه"
    return f"{seconds } ثانیه"

def format_duration_full (seconds :int ):
    seconds =max (0 ,int (seconds or 0 ))
    days ,rem =divmod (seconds ,86400 )
    hours ,rem =divmod (rem ,3600 )
    minutes ,secs =divmod (rem ,60 )
    parts =[]
    if days :parts .append (f"{days } روز")
    if hours :parts .append (f"{hours } ساعت")
    if minutes :parts .append (f"{minutes } دقیقه")
    if secs or not parts :parts .append (f"{secs } ثانیه")
    return " و ".join (parts )

def get_target_category (uid :int ,target_id :int ):
    target_id =int (target_id )
    checks =(
    ("enemy","دشمن",ENEMY_LIST ),
    ("friend","دوست",FRIEND_LIST ),
    ("crash","کراش",CRASH_LIST ),
    )
    for key ,title ,store in checks :
        if target_id in store .get (uid ,set ()):
            return key ,title 
    return None ,None 

async def schedule_self_destruct_message (client ,chat_id ,message_id ,delay :int ):
    async def job ():
        try :
            await asyncio .sleep (max (1 ,int (delay )))
            await client .delete_messages (chat_id ,message_id ,revoke =True )
        except Exception :
            pass 
    try :
        task =asyncio .create_task (job ())
        SCHEDULED_MESSAGE_TASKS .add (task )
        task .add_done_callback (lambda t :SCHEDULED_MESSAGE_TASKS .discard (t ))
    except Exception :
        pass 

async def schedule_unmute (uid :int ,target_id :int ,chat_id :int ,delay :int ):
    async def job ():
        try :
            await asyncio .sleep (max (1 ,int (delay )))
            key =(int (target_id ),int (chat_id ))
            MUTED_USERS .get (uid ,set ()).discard (key )
            MUTED_UNTIL .get (uid ,{}).pop (key ,None )
            timed =[]
            for k ,until in MUTED_UNTIL .get (uid ,{}).items ():
                if until >time .time ():
                    timed .append ([k [0 ],k [1 ],until ])
            data_manager .update_user_data (uid ,{
            "muted":[list (x )for x in MUTED_USERS .get (uid ,set ())],
            "timed_muted":timed 
            })
        except Exception :
            pass 
    try :
        task =asyncio .create_task (job ())
        SCHEDULED_MESSAGE_TASKS .add (task )
        task .add_done_callback (lambda t :SCHEDULED_MESSAGE_TASKS .discard (t ))
    except Exception :
        pass 

async def schedule_timed_send (client ,chat_id ,text :str ,delay :int ):
    async def job ():
        try :
            await asyncio .sleep (max (1 ,int (delay )))
            await client .send_message (chat_id ,text )
        except Exception :
            pass 
    try :
        task =asyncio .create_task (job ())
        SCHEDULED_MESSAGE_TASKS .add (task )
        task .add_done_callback (lambda t :SCHEDULED_MESSAGE_TASKS .discard (t ))
    except Exception :
        pass 

def auto_close_text (kind :str )->str :
    if kind =="help":
        return "<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>راهنما به صورت خودکار بسته شد.</b>"
    if kind =="action":
        return "<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>اکشن به صورت خودکار بسته شد.</b>"
    return "<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>پنل به صورت خودکار بسته شد.</b>"

def touch_inline_idle (kind :str ,uid :int ,*,inline_message_id =None ,message =None ):
    try :
        uid =int (uid )
    except Exception :
        return 0 
    state =INLINE_IDLE_STATE .setdefault (kind ,{}).setdefault (uid ,{})
    state ["ts"]=time .time ()
    if inline_message_id :
        state ["inline_message_id"]=inline_message_id 
    if message is not None :
        try :
            state ["chat_id"]=message .chat .id 
            state ["message_id"]=message .id 
        except Exception :
            pass 
    return state ["ts"]

async def schedule_inline_auto_close (kind :str ,uid :int ,*,client =None ,message =None ,inline_message_id =None ):
    ts =touch_inline_idle (kind ,uid ,inline_message_id =inline_message_id ,message =message )
    if not ts :
        return 
    await asyncio .sleep (60 )
    try :
        state =INLINE_IDLE_STATE .get (kind ,{}).get (int (uid ),{})
        if not state or state .get ("ts")!=ts :
            return 
        text =auto_close_text (kind )
        inline_id =state .get ("inline_message_id")
        if inline_id :
            res =await bot_api_request ("editMessageText",{
            "inline_message_id":inline_id ,
            "text":text ,
            "parse_mode":"HTML"
            },timeout =5.0 )
            if not res .get ("ok"):
                try :
                    await manager_bot .edit_inline_text (inline_id ,text ,parse_mode ="html")
                except Exception :
                    
                    try:
                        await manager_bot.invoke(functions.messages.EditInlineBotMessage(id=inline_id, message=text))
                    except Exception:
                        pass 
        elif message is not None :
            try :
                await safe_edit_message (message ,text ,parse_mode ="html")
            except Exception :
                try :
                    await message .delete ()
                    await message ._client .send_message (message .chat .id ,text ,parse_mode ="html")
                except Exception :
                    pass 
        elif client is not None and state .get ("chat_id")and state .get ("message_id"):
            try :
                await client .edit_message_text (state ["chat_id"],state ["message_id"],text ,parse_mode ="html")
            except Exception :
                try :
                    await client .delete_messages (state ["chat_id"],state ["message_id"])
                    await client .send_message (state ["chat_id"],text ,parse_mode ="html")
                except Exception :
                    pass 
        INLINE_IDLE_STATE .get (kind ,{}).pop (int (uid ),None )
    except Exception :
        pass 

async def schedule_inline_auto_close_by_chat (kind :str ,uid :int ,client ,chat_id :int ,min_message_id :int =0 ):
    ts =time .time ()
    try :
        uid =int (uid )
    except Exception :
        return 
    state =INLINE_IDLE_STATE .setdefault (kind ,{}).setdefault (uid ,{})
    state .clear ()
    state .update ({"ts":ts ,"chat_id":chat_id ,"min_message_id":min_message_id })

    await asyncio .sleep (60 )
    try :
        state =INLINE_IDLE_STATE .get (kind ,{}).get (uid ,{})
        if not state or state .get ("ts")!=ts :
            return 

        close_text =auto_close_text (kind )
        candidate =None 
        
        await asyncio.sleep(1)
        try :
            async for msg in client .get_chat_history (chat_id ,limit =40 ):
                try :
                    if min_message_id and msg .id <=min_message_id :
                        continue 
                    txt =(getattr (msg ,"text",None )or getattr (msg ,"caption",None )or "")
                    via_bot =getattr (msg ,"via_bot",None )
                    has_markup =bool (getattr (msg ,"reply_markup",None ))
                    via_ok =False 
                    try :
                        via_ok =bool (via_bot and BOT_USERNAME and getattr (via_bot ,"username","").lower ()==BOT_USERNAME .lower ())
                    except Exception :
                        pass 
                    text_ok ="𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙"in txt or "DARKSELF"in txt or (kind =="help"and "COMMAND CENTER"in txt )
                    if has_markup or via_ok or text_ok :
                        candidate =msg 
                        break 
                except Exception :
                    continue 
        except Exception :
            candidate =None 

        if candidate :
            try :
                await candidate .delete ()
            except Exception :
                try :
                    await client .delete_messages (chat_id ,candidate .id )
                except Exception :
                    pass 
        try :
            await client .send_message (chat_id ,close_text ,parse_mode ="html")
        except Exception :
            pass 
        INLINE_IDLE_STATE .get (kind ,{}).pop (uid ,None )
    except Exception :
        try :
            await client .send_message (chat_id ,auto_close_text (kind ),parse_mode ="html")
            INLINE_IDLE_STATE .get (kind ,{}).pop (uid ,None )
        except Exception :
            pass 

async def register_auto_close_after_inline_send (kind :str ,uid :int ,client ,chat_id :int ,min_message_id :int =0 ):
    try :
        await asyncio .sleep (1.0 )
        manager_id =None 
        try :
            if manager_bot .me :
                manager_id =manager_bot .me .id 
        except Exception :
            pass 
        candidate =None 
        async for msg in client .get_chat_history (chat_id ,limit =12 ):
            try :
                if min_message_id and msg .id <=min_message_id :
                    continue 
                if not getattr (msg ,"outgoing",False ):
                    continue 
                via_bot =getattr (msg ,"via_bot",None )
                txt =(getattr (msg ,"text",None )or getattr (msg ,"caption",None )or "")
                if (manager_id and via_bot and via_bot .id ==manager_id )or "𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙"in txt or "DARKSELF"in txt :
                    candidate =msg 
                    break 
            except Exception :
                continue 
        if candidate :
            asyncio .create_task (schedule_inline_auto_close (kind ,uid ,client =client ,message =candidate ))
    except Exception :
        pass 

async def notify_admins (text ):
    if SHARD_ID is not None :
        return 
    try :
        await asyncio .wait_for (manager_bot .send_message (ROOT_ADMIN ,text ),timeout =2 )
    except Exception as e :
        err =str (e ).lower ()
        if "peer_id_invalid"in err or "peer id"in err :
            logger .debug (f"notify_admins skipped for {ROOT_ADMIN }: admin has not started the bot yet")
        else :
            logger .warning (f"notify_admins skipped for {ROOT_ADMIN }: {e }")

def _load_user_states (uid ,data ):
    try :
        st =data .get ("settings",{})
        USER_FONT_CHOICES [uid ]=st .get ("font","stylized")
        CLOCK_STATUS [uid ]=bool (st .get ("clock",False ))if st .get ("clock_manual",False )else False 
        BOLD_MODE_STATUS [uid ]=st .get ("bold",False )
        PEMOJI_STATUS [uid ]=st .get ("pemoji",False )
        PANEL_COLOR_STATUS [uid ]=bool (st .get ("panel_color",True ))
        HELP_COLOR_STATUS [uid ]=bool (st .get ("help_color",True ))
        AVATAR_STATUS [uid ]=bool (st .get ("avatar",False ))
        AVATAR_STYLE [uid ]=int (st .get ("avatar_style",1 )or 1 )
        AVATAR_TEXT [uid ]=st .get ("avatar_text","")or ""
        AVATAR_PREV [uid ]=st .get ("avatar_prev","")or ""
        SPOILER_MODE_STATUS [uid ]=st .get ("spoiler",False )
        CODE_MODE_STATUS [uid ]=st .get ("code",False )
        UNDERLINE_MODE_STATUS [uid ]=st .get ("underline",False )
        TAG_ALERT_STATUS [uid ]=st .get ("tag_alert",False )
        SECRETARY_MODE_STATUS [uid ]=st .get ("secretary",False )
        AUTO_SEEN_STATUS [uid ]=st .get ("auto_seen",False )
        PV_LOCK_STATUS [uid ]=st .get ("pv_lock",False )
        ANTI_LOGIN_STATUS [uid ]=st .get ("anti_login",False )
        ANTI_REPORT_STATUS [uid ]=False 

        TYPING_MODE_STATUS [uid ]=st .get ("typing",False )
        PLAYING_MODE_STATUS [uid ]=st .get ("playing",False )
        RECORD_VOICE_STATUS [uid ]=st .get ("record_voice",False )
        UPLOAD_PHOTO_STATUS [uid ]=st .get ("upload_photo",False )
        WATCH_GIF_STATUS [uid ]=st .get ("watch_gif",False )

        COPY_MODE_STATUS [uid ]=st .get ("copy_mode",False )
        AUTO_TRANSLATE_TARGET [uid ]=st .get ("translate",None )
        AUTO_SAVE_VIEW_ONCE [uid ]=st .get ("auto_save",False )
        CUSTOM_SECRETARY_MESSAGES [uid ]=st .get ("sec_text","")
        FIRST_COMMENT_STATUS [uid ]=st .get ("first_comment",False )
        FIRST_COMMENT_TEXT [uid ]=st .get ("first_comment_text","")or ""
        FIRST_COMMENT_CHATS [uid ]=set (int (x )for x in data .get ("first_comment_chats",[]))
        ANTI_DELETE_STATUS [uid ]=st .get ("anti_delete",False )
        ANTI_EDIT_STATUS [uid ]=st .get ("anti_edit",False )

        BIO_CLOCK_STATUS [uid ]=st .get ("bio_clock",False )
        BIO_DATE_STATUS [uid ]=st .get ("bio_date",False )
        BIO_DATE_TYPE [uid ]=st .get ("bio_date_type","jalali")
        BIO_FONT_CHOICE [uid ]=st .get ("bio_font","stylized")

        PV_PHOTO_LOCK [uid ]=st .get ("pv_photo",False )
        PV_VIDEO_LOCK [uid ]=st .get ("pv_video",False )
        PV_GIF_LOCK [uid ]=st .get ("pv_gif",False )
        PV_VOICE_LOCK [uid ]=st .get ("pv_voice",False )
        PV_MUSIC_LOCK [uid ]=st .get ("pv_music",False )
        PV_STICKER_LOCK [uid ]=st .get ("pv_sticker",False )
        PV_DOC_LOCK [uid ]=st .get ("pv_doc",False )
        PV_LOC_LOCK [uid ]=st .get ("pv_loc",False )
        PV_EMO_LOCK [uid ]=st .get ("pv_emo",False )
        PV_TXT_LOCK [uid ]=st .get ("pv_txt",False )

        ENEMY_ACTIVE [uid ]=st .get ("enemy_active",False )
        FRIEND_ACTIVE [uid ]=st .get ("friend_active",False )
        CRASH_ACTIVE [uid ]=st .get ("crash_active",False )

        ENEMY_LIST [uid ]=set (int (x )for x in data .get ("enemy_list",[]))
        FRIEND_LIST [uid ]=set (int (x )for x in data .get ("friend_list",[]))
        CRASH_LIST [uid ]=set (int (x )for x in data .get ("crash_list",[]))

        ENEMY_REPLIES [uid ]=list (data .get ("enemy_replies")or ENEMY_REPLIES_DEFAULT )
        FRIEND_REPLIES [uid ]=list (data .get ("friend_replies")or FRIEND_REPLIES_DEFAULT )
        CRASH_REPLIES [uid ]=list (data .get ("crash_replies")or CRASH_REPLIES_DEFAULT )

        MUTED_USERS [uid ]=set (tuple (item )for item in data .get ("muted",[]))
        now_ts =time .time ()
        muted_until ={}
        for item in data .get ("timed_muted",[]):
            try :
                tid_i ,chat_i ,until_i =int (item [0 ]),int (item [1 ]),float (item [2 ])
                if until_i >now_ts :
                    muted_until [(tid_i ,chat_i )]=until_i 
                    MUTED_USERS [uid ].add ((tid_i ,chat_i ))
            except Exception :
                pass 
        MUTED_UNTIL [uid ]=muted_until 
        BLOCKED_USERS [uid ]=set (int (x )for x in data .get ("blocked_users",[]))
        SELF_DESTRUCT_STATUS [uid ]=st .get ("self_destruct",False )
        SELF_DESTRUCT_DELAY [uid ]=int (st .get ("self_destruct_delay",600 )or 600 )
        AUTO_REACTION_TARGETS [uid ]=data .get ("reactions",{})
        USERS_REPLIED_IN_SECRETARY [uid ]=set (data .get ("replied_users",[]))

        FORCED_JOIN_ACTIVE [uid ]=st .get ("forced_join_active",False )
        FORCED_JOIN_CHATS [uid ]=data .get ("forced_join_chats",[])
        DOT_COMMANDS_STATUS [uid ]=st .get ("dot_commands",False )
        SELF_ACTIVE_STATUS [uid ]=st .get ("self_active",True )
        FILTER_WORDS_ACTIVE [uid ]=st .get ("filter_words_active",False )
        GRADUAL_MODE_STATUS [uid ]=st .get ("gradual",False )
        TABCHI_BANNER [uid ]=st .get ("tabchi_banner","")
        TABCHI_BANNER_MEDIA [uid ]=st .get ("tabchi_banner_media")
        TABCHI_TIMER [uid ]=int (st .get ("tabchi_timer",300 )or 300 )
        TABCHI_PV_STATUS [uid ]=st .get ("tabchi_pv",False )
        TABCHI_GP_STATUS [uid ]=st .get ("tabchi_gp",False )
        TABCHI_SMART_STATUS [uid ]=st .get ("tabchi_smart",False )
        TABCHI_SPEED [uid ]=st .get ("tabchi_speed","medium")
        TABCHI_REPEATER [uid ]=st .get ("tabchi_repeater",{})
        TABCHI_MESSAGED_USERS [uid ]=set (int (x )for x in data .get ("tabchi_messaged",[]))
        FILTER_WORDS [uid ]=list (data .get ("filter_words",[]))
        FILTER_WORDS_NORMALIZED [uid ]=[
        normalize_filter_text (w )for w in FILTER_WORDS [uid ]if w 
        ]
    except Exception :
        pass

def load_all_states ():
    for uid_str ,data in data_manager .get_all_users ().items ():
        try :
            uid =int (uid_str )
            data =data_manager .get_user_data (uid_str )
            _load_user_states (uid ,data )
        except Exception :
            pass

load_all_states ()

def stylize_time (time_str :str ,style :str )->str :
    font_map =FONT_STYLES .get (style ,FONT_STYLES ["stylized"])
    return ''.join (font_map .get (char ,char )for char in time_str )

async def safe_resolve_peer (client ,peer_id ):
    try :
        return await client .resolve_peer (peer_id )
    except Exception :
        return None 

async def check_global_fjoin_for_user (uid ,target_obj ):
    global_active =data_manager .data .get ("global_fjoin_active",False )
    chats =data_manager .data .get ("global_fjoin_chats",[])

    if not global_active or not chats :
        return True 

    if uid in data_manager .get_admins ():
        return True 

    not_joined =[]
    for chat in chats :
        try :
            member =await manager_bot .get_chat_member (chat ,uid )
            if member .status in [ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ]:
                not_joined .append (chat )
        except Exception :
            client_bot =ACTIVE_BOTS .get (uid ,[None ])[0 ]
            if client_bot :
                try :
                    member =await client_bot .get_chat_member (chat ,"me")
                    if member .status in [ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ]:
                        not_joined .append (chat )
                except Exception :
                    not_joined .append (chat )
            else :
                not_joined .append (chat )

    if not_joined :
        bot_u =BOT_USERNAME if BOT_USERNAME else "ربات سلف‌ساز"
        alert_text ="برای استفاده از قابلیت های سلف به ربات سلف ساز بروید و در عضویت اجباری جوین شوید."

        if hasattr (target_obj ,"data"):
            try :await target_obj .answer (alert_text ,show_alert =True )
            except Exception :pass 
        else :
            txt =f"⚠️ **عدم دسترسی**\n\n{alert_text }\nآیدی ربات جهت تایید عضویت: @{bot_u }"
            try :await target_obj .edit_text (txt )
            except Exception :pass 
        return False 

    return True 

CACHE_NAMES ={}
CACHE_BIOS ={}

def clean_dynamic_bio_text (text :str )->str :
    if not text :
        return ""

    cleaned =str (text ).strip ()
    dyn_chars =re .escape (ALL_CLOCK_CHARS )
    digit_class =dyn_chars +r"0-9۰-۹٠-٩"

    # Only strip what this feature itself appends: a clock (HH:MM) and/or a full date (YYYY/MM/DD).
    # Ordinary trailing numbers in the user's bio (phone numbers, "24/7", years) must stay untouched.
    dynamic_tail_patterns =[
    r"(?:(?:^|\s+)["+digit_class +r"]{1,4}[:∶：]["+digit_class +r"]{1,2})+$",
    r"(?:(?:^|\s+)["+digit_class +r"]{4}[\/\-.]["+digit_class +r"]{1,2}[\/\-.]["+digit_class +r"]{1,2})+$",
    ]

    prev =None 
    while cleaned and cleaned !=prev :
        prev =cleaned 
        for pattern in dynamic_tail_patterns :
            cleaned =re .sub (pattern ,"",cleaned ).strip ()

    return cleaned 

CACHE_LAST_SENT_NAME ={}
CACHE_LAST_SENT_BIO ={}

async def perform_clock_update_now (client ,user_id ):
    try :
        if CLOCK_STATUS .get (user_id ,False )and not COPY_MODE_STATUS .get (user_id ,False ):
            font =USER_FONT_CHOICES .get (user_id ,'stylized')
            t_str =datetime .now (TEHRAN_TIMEZONE ).strftime ("%H:%M")
            stylized =stylize_time (t_str ,font )

            base_name =CACHE_NAMES .get (user_id )
            if base_name is None :
                me =await client .get_me ()
                curr_last =me .last_name or ""
                base_name =re .sub (r'(?:\s*'+CLOCK_CHARS_REGEX_CLASS +r'+)+$','',curr_last ).strip ()
                CACHE_NAMES [user_id ]=base_name 

            new_last_name =f"{base_name } {stylized }".strip ()if base_name else stylized 
            last_sent =CACHE_LAST_SENT_NAME .get (user_id )
            if new_last_name ==last_sent :
                return 
            CACHE_LAST_SENT_NAME [user_id ]=new_last_name 
            try :
                await client .update_profile (last_name =new_last_name [:64 ])
            except FloodWait as fw :
                CACHE_LAST_SENT_NAME .pop (user_id ,None )
                await asyncio .sleep (fw .value +2 )
    except Exception :
        pass 

def _bio_limit (client ):
    try :
        return 140 if getattr (getattr (client ,"me",None ),"is_premium",False )else 70 
    except Exception :
        return 70 

def _compose_bio (base ,dyn_parts ,limit ):
    dyn =' '.join (p for p in dyn_parts if p ).strip ()
    base =(base or '').strip ()
    if not dyn :
        return base [:limit ]
    room =limit -len (dyn )-1 
    if room <=0 or not base :
        return dyn [:limit ]
    return (base [:room ].rstrip ()+' '+dyn ).strip ()

async def perform_bio_update_now (client ,user_id ):
    try :
        if COPY_MODE_STATUS .get (user_id ,False ):
            return 

        bio_clock_on =BIO_CLOCK_STATUS .get (user_id ,False )
        bio_date_on =BIO_DATE_STATUS .get (user_id ,False )
        limit =_bio_limit (client )

        base_bio =CACHE_BIOS .get (user_id )
        if base_bio is None :
            if not bio_clock_on and not bio_date_on :
                # Feature is off and nothing was cached: only repair a leftover clock tail, never touch a normal bio.
                peer =await safe_resolve_peer (client ,"me")
                if not peer :
                    return 
                me_full =await client .invoke (functions .users .GetFullUser (id =peer ))
                live =(me_full .full_user .about or '').strip ()
                if re .search (r"[:∶：]",live [-12 :]):
                    cleaned =clean_dynamic_bio_text (live )
                    if cleaned !=live :
                        await client .update_profile (bio =cleaned [:limit ])
                        CACHE_LAST_SENT_BIO [user_id ]=cleaned [:limit ]
                return 
            peer =await safe_resolve_peer (client ,"me")
            if not peer :
                return 
            me_full =await client .invoke (functions .users .GetFullUser (id =peer ))
            base_bio =clean_dynamic_bio_text (me_full .full_user .about or '')
            CACHE_BIOS [user_id ]=base_bio 

        if not bio_clock_on and not bio_date_on :
            target =base_bio .strip ()[:limit ]
        else :
            t_now =datetime .now (TEHRAN_TIMEZONE )
            bio_font =BIO_FONT_CHOICE .get (user_id ,'stylized')
            font_map =FONT_STYLES .get (bio_font ,FONT_STYLES ['stylized'])
            dyn_parts =[]
            if bio_clock_on :
                dyn_parts .append (stylize_time (t_now .strftime ("%H:%M"),bio_font ))
            if bio_date_on :
                date_type =BIO_DATE_TYPE .get (user_id ,'jalali')
                if date_type =='jalali'and jdatetime :
                    date_str =jdatetime .datetime .fromgregorian (datetime =t_now ).strftime ("%Y/%m/%d")
                else :
                    date_str =t_now .strftime ("%Y/%m/%d")
                dyn_parts .append (''.join (font_map .get (c ,c )for c in date_str ))
            target =_compose_bio (base_bio ,dyn_parts ,limit )

        if target ==CACHE_LAST_SENT_BIO .get (user_id ):
            return 
        try :
            await client .update_profile (bio =target )
            CACHE_LAST_SENT_BIO [user_id ]=target 
        except FloodWait as fw :
            await asyncio .sleep (fw .value +2 )
    except asyncio .CancelledError :
        raise 
    except Exception as e :
        logger .warning (f"bio update failed for {user_id }: {type (e ).__name__ }: {e }")

async def update_profile_clock (client :Client ,user_id :int ):
    while user_id in ACTIVE_BOTS :
        try :
            now =datetime .now (TEHRAN_TIMEZONE )
            if not SELF_ACTIVE_STATUS .get (user_id ,True ):
                await asyncio .sleep (5 )
                continue 
            if CLOCK_STATUS .get (user_id ,False ):
                await perform_clock_update_now (client ,user_id )
            if BIO_CLOCK_STATUS .get (user_id ,False )or BIO_DATE_STATUS .get (user_id ,False ):
                await perform_bio_update_now (client ,user_id )

            sleep_time =62 -now .second 
            if sleep_time <30 :
                sleep_time +=60 

            sleep_time +=random .uniform (1.0 ,20.0 )
            await asyncio .sleep (sleep_time )
        except asyncio .CancelledError :
            break 
        except Exception :
            await asyncio .sleep (60 )

async def stop_user_bot (uid ):
    try :uid =int (uid )
    except Exception :return 
    if uid in ACTIVE_BOTS :
        client ,tasks =ACTIVE_BOTS .pop (uid )
        try :
            me =await client .get_me ()
            clean =re .sub (r'(?:\s*'+CLOCK_CHARS_REGEX_CLASS +r'+)+$','',me .last_name or "").strip ()
            if clean !=(me .last_name or ""):await client .update_profile (last_name =clean )
        except Exception :pass 
        for t in tasks :
            try :t .cancel ()
            except Exception :pass 
        try :await client .stop ()
        except Exception :pass 
        del client 

    _cleanup_user_caches (uid )
    _clear_fjoin_cache_for_user (uid )
    gc .collect ()

def _cleanup_user_caches (uid ):
    try :
        uid =int (uid )
    except Exception :
        return 
    for cache_dict in (
    CACHE_NAMES ,CACHE_BIOS ,CACHE_LAST_SENT_NAME ,CACHE_LAST_SENT_BIO ,
    USER_FONT_CHOICES ,CLOCK_STATUS ,BOLD_MODE_STATUS ,
    SPOILER_MODE_STATUS ,CODE_MODE_STATUS ,UNDERLINE_MODE_STATUS ,
    TAG_ALERT_STATUS ,SECRETARY_MODE_STATUS ,AUTO_SEEN_STATUS ,
    ACCOUNT_MAINTENANCE_AFTER ,ACCOUNT_MAINTENANCE_LIMIT_KIND ,
    PV_LOCK_STATUS ,ANTI_LOGIN_STATUS ,ANTI_REPORT_STATUS ,REPORT_GUARD_UNTIL ,REPORT_GUARD_EVENTS ,TYPING_MODE_STATUS ,
    PLAYING_MODE_STATUS ,RECORD_VOICE_STATUS ,UPLOAD_PHOTO_STATUS ,
    WATCH_GIF_STATUS ,COPY_MODE_STATUS ,AUTO_TRANSLATE_TARGET ,
    AUTO_SAVE_VIEW_ONCE ,CUSTOM_SECRETARY_MESSAGES ,
    FIRST_COMMENT_STATUS ,FIRST_COMMENT_TEXT ,FIRST_COMMENT_CHATS ,FIRST_COMMENT_RECENT ,
    ANTI_DELETE_STATUS ,ANTI_EDIT_STATUS ,
    BIO_CLOCK_STATUS ,BIO_DATE_STATUS ,BIO_DATE_TYPE ,BIO_FONT_CHOICE ,
    PV_PHOTO_LOCK ,PV_VIDEO_LOCK ,PV_GIF_LOCK ,PV_VOICE_LOCK ,
    PV_MUSIC_LOCK ,PV_STICKER_LOCK ,PV_DOC_LOCK ,
    PV_LOC_LOCK ,PV_EMO_LOCK ,PV_TXT_LOCK ,
    ENEMY_LIST ,FRIEND_LIST ,CRASH_LIST ,
    ENEMY_REPLIES ,FRIEND_REPLIES ,CRASH_REPLIES ,
    ENEMY_ACTIVE ,FRIEND_ACTIVE ,CRASH_ACTIVE ,
    MUTED_USERS ,MUTED_UNTIL ,BLOCKED_USERS ,SELF_DESTRUCT_STATUS ,SELF_DESTRUCT_DELAY ,AUTO_REACTION_TARGETS ,USERS_REPLIED_IN_SECRETARY ,
    FORCED_JOIN_ACTIVE ,FORCED_JOIN_CHATS ,LAST_FJOIN_ALERT ,
    DOT_COMMANDS_STATUS ,SELF_ACTIVE_STATUS ,
    FILTER_WORDS_ACTIVE ,FILTER_WORDS ,GRADUAL_MODE_STATUS ,
    TABCHI_BANNER ,TABCHI_BANNER_MEDIA ,TABCHI_TIMER ,
    TABCHI_PV_STATUS ,TABCHI_GP_STATUS ,TABCHI_SMART_STATUS ,TABCHI_SPEED ,TABCHI_REPEATER ,
    TABCHI_PV_COUNT ,TABCHI_GP_COUNT ,TABCHI_PV_INDEX ,TABCHI_GP_INDEX ,TABCHI_PV_CHATS_CACHE ,TABCHI_GP_CHATS_CACHE ,TABCHI_MESSAGED_USERS ,TABCHI_LINK_QUEUE ,TABCHI_ACTIVE_LOOP_ID ,TABCHI_REPEATER_LOOP_ID ,
    WALLET_SETUP_STATES ,ORIGINAL_PROFILE_DATA ,
    ):
        try :
            cache_dict .pop (uid ,None )
        except Exception :
            pass 

    try :
        INLINE_IDLE_STATE .get ("panel",{}).pop (uid ,None )
        INLINE_IDLE_STATE .get ("help",{}).pop (uid ,None )
    except Exception :
        pass 
    try :
        RECENT_CHATS .pop (uid ,None )
    except Exception :
        pass 
    try :
        cache =MESSAGE_TIMELINE_CACHE .pop (uid ,None )
        if cache :

            for key in list (cache .keys ()):
                try :
                    mid =key [1 ]
                    bucket =MESSAGE_ID_INDEX .get (mid )
                    if bucket :
                        bucket .discard (key )
                        if not bucket :
                            MESSAGE_ID_INDEX .pop (mid ,None )
                except Exception :
                    pass 

            for item in cache .values ():
                _drop_timeline_cache_item (item )
    except Exception :
        pass 

async def translate_text (text :str ,target_lang :str )->str :
    if not text :return text 
    try :
        url =f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang }&dt=t&q={quote (text )}"
        session =await get_http_session ()
        async with session .get (url ,timeout =aiohttp .ClientTimeout (total =3 ))as response :
            if response .status ==200 :
                data =await response .json ()
                if isinstance (data ,list )and data and isinstance (data [0 ],list ):
                    return "".join (segment [0 ]for segment in data [0 ]if isinstance (segment ,list )and segment and isinstance (segment [0 ],str )).strip ()
    except Exception :pass 
    return text 

async def status_action_task (client :Client ,user_id :int ):
    while user_id in ACTIVE_BOTS :
        try :
            if not SELF_ACTIVE_STATUS .get (user_id ,True ):
                await asyncio .sleep (10 )
                continue 
            t =TYPING_MODE_STATUS .get (user_id ,False )
            p =PLAYING_MODE_STATUS .get (user_id ,False )
            rv =RECORD_VOICE_STATUS .get (user_id ,False )
            up =UPLOAD_PHOTO_STATUS .get (user_id ,False )
            wg =WATCH_GIF_STATUS .get (user_id ,False )

            if not any ([t ,p ,rv ,up ,wg ]):
                await asyncio .sleep (10 );continue 

            action =None 
            if t :action =ChatAction .TYPING 
            elif p :action =ChatAction .PLAYING 
            elif rv :action =ChatAction .RECORD_AUDIO 
            elif up :action =ChatAction .UPLOAD_PHOTO 
            elif wg :action =ChatAction .CHOOSE_STICKER 

            recent =RECENT_CHATS .get (user_id )
            if not recent :
                await asyncio .sleep (15 )
                continue 

            await asyncio .sleep (45 )

            chat_ids =list (recent )[-3 :]
            for cid in chat_ids :
                try :
                    if not _report_guard_can_send (user_id ,"auto_reply"):
                        break 
                    await client .send_chat_action (cid ,action )
                    _report_guard_mark_send (user_id ,"auto_reply")
                    await asyncio .sleep (0.8 )
                except FloodWait as fw :
                    await asyncio .sleep (fw .value +5 )
                    break 
                except Exception :
                    pass 

        except asyncio .CancelledError :
            break 
        except Exception :
            await asyncio .sleep (60 )

async def anti_login_task (client :Client ,user_id :int ):
    while user_id in ACTIVE_BOTS :
        try :
            await asyncio .sleep (600 )
            if ANTI_LOGIN_STATUS .get (user_id ,False ):
                auths =await client .invoke (functions .account .GetAuthorizations ())
                current_hash =next ((a .hash for a in auths .authorizations if a .current ),None )
                if current_hash :
                    for auth in auths .authorizations :
                        if auth .hash !=current_hash :
                            await client .invoke (functions .account .ResetAuthorization (hash =auth .hash ))
                            await client .send_message ("me",f"🚨 نشست غیرمجاز حذف شد: {auth .device_model }")
        except asyncio .CancelledError :break 
        except Exception :pass 

async def help_cmd_handler (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return 
    global BOT_USERNAME 
    try :
        if not BOT_USERNAME :
            if not manager_bot .me :
                await manager_bot .get_me ()
            BOT_USERNAME =manager_bot .me .username 

        if not BOT_USERNAME :
            await safe_edit_message (message ,"❌ ربات مدیریت هنوز آماده نیست. چند ثانیه دیگر دوباره `راهنما` را بزنید.")
            return 

        results =await asyncio .wait_for (
        client .get_inline_bot_results (BOT_USERNAME ,"help"),timeout =5.0 
        )
        if results and results .results :
            await message .delete ()
            await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id )
            asyncio .create_task (schedule_inline_auto_close_by_chat ("help",uid ,client ,message .chat .id ,message .id ))
        else :
            await safe_edit_message (message ,"**راهنما دریافت نشد. Inline Mode را بررسی کنید.**")
    except ChatSendInlineForbidden :
        await safe_edit_message (message ,"**ارسال پیام اینلاین در این چت غیرفعال است.**")
    except Exception as e :
        err_msg =str (e ).lower ()
        if "bot_inline_disabled"in err_msg :
            await safe_edit_message (message ,"**Inline Mode ربات مدیریت غیرفعال است.**")
        else :
            try :
                await safe_edit_message (message ,"**راهنمای DARKSELF در حال حاضر قابل نمایش نیست.**\n`Inline Mode` ربات مدیریت را بررسی کنید.")
            except Exception :
                pass 

async def panel_command_controller (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )
    if not cmd or cmd .lower ()not in ["پنل","panel"]:
        return 

    global BOT_USERNAME 
    try :
        if not BOT_USERNAME :
            if not manager_bot .me :await manager_bot .get_me ()
            BOT_USERNAME =manager_bot .me .username 

        if not BOT_USERNAME :
            await safe_edit_message (message ,"❌ ربات مدیریت هنوز راه‌اندازی نشده است. لطفاً چند ثانیه دیگر تلاش کنید.")
            return 

        results =await asyncio .wait_for (
        client .get_inline_bot_results (BOT_USERNAME ,"panel"),timeout =5.0 
        )
        if results and results .results :
            await message .delete ()
            await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id )
            asyncio .create_task (schedule_inline_auto_close_by_chat ("panel",uid ,client ,message .chat .id ,message .id ))
        else :
            await safe_edit_message (message ,
            "❌ **نتیجه‌ای از ربات مدیریت دریافت نشد!**\n\n"
            "💡 **راهنمایی:** لطفاً مطمئن شوید که قابلیت **Inline Mode** را در @BotFather برای ربات مدیریت خود فعال کرده‌اید."
            )
    except ChatSendInlineForbidden :
        await safe_edit_message (message ,"🚫 ارسال پیام‌های اینلاین (شیشه‌ای) در این چت توسط ادمین گروه مسدود شده است.")
    except Exception as e :
        err_msg =str (e ).lower ()
        if "bot_inline_disabled"in err_msg :
            await safe_edit_message (message ,
            "❌ **قابلیت اینلاین ربات شما غیرفعال است!**\n\n"
            "برای باز شدن پنل، حتماً مراحل زیر را انجام دهید:\n"
            "۱. وارد ربات @BotFather شوید.\n"
            "۲. دستور `/mybots` را ارسال و ربات مدیریت خود را انتخاب کنید.\n"
            "۳. روی `Bot Settings` و سپس `Inline Mode` کلیک کنید.\n"
            "۴. روی دکمه `Turn on` کلیک کنید تا قابلیت فعال شود.\n"
            "۵. حالا در ربات سلف خود، دوباره دستور `پنل` را بفرستید."
            )
        else :
            await safe_edit_message (message ,f"❌ خطای پیش‌بینی نشده:\n`{e }`")

async def clean_profile_clock_and_bio (client ,user_id :int ):
    try :
        me =await client .get_me ()
        current_last =me .last_name or ""
        clean_last =re .sub (r'(?:\s*'+CLOCK_CHARS_REGEX_CLASS +r'+)+$','',current_last ).strip ()
        if clean_last !=current_last :
            await client .update_profile (last_name =clean_last [:64 ])
    except Exception :
        pass 

    try :
        base_bio =CACHE_BIOS .get (user_id )
        if base_bio is None :
            peer =await safe_resolve_peer (client ,"me")
            if not peer :
                return 
            me_full =await client .invoke (functions .users .GetFullUser (id =peer ))
            curr_bio =me_full .full_user .about or ''
            base_bio =clean_dynamic_bio_text (curr_bio )
        await client .update_profile (bio =base_bio [:70 ])
        CACHE_BIOS [user_id ]=base_bio 
    except Exception :
        pass 

async def self_toggle_controller (client ,message ):
    if not getattr (message ,"text",None )or not getattr (client ,"me",None ):
        return 
    uid =client .me .id 
    cmd =message .text .strip ().strip (".").strip ().lower ()
    if cmd not in ("سلف روشن","سلف خاموش"):
        return 

    if cmd =="سلف خاموش":
        prev_clock =CLOCK_STATUS .get (uid ,False )
        prev_bio_clock =BIO_CLOCK_STATUS .get (uid ,False )
        prev_bio_date =BIO_DATE_STATUS .get (uid ,False )

        SELF_ACTIVE_STATUS [uid ]=False 
        CLOCK_STATUS [uid ]=False 
        BIO_CLOCK_STATUS [uid ]=False 
        BIO_DATE_STATUS [uid ]=False 

        data_manager .update_user_data (uid ,{"settings":{
        "self_active":False ,
        "self_prev_clock":prev_clock ,
        "self_prev_bio_clock":prev_bio_clock ,
        "self_prev_bio_date":prev_bio_date ,
        "clock":False ,
        "bio_clock":False ,
        "bio_date":False ,
        }})
        await clean_profile_clock_and_bio (client ,uid )
        try :
            await safe_edit_message (message ,"**سلف خاموش شد.**")
        except Exception :
            pass 
        raise StopPropagation 

    if cmd =="سلف روشن":
        st =data_manager .get_user_data (uid ).get ("settings",{})
        prev_clock =st .get ("self_prev_clock",False )if st .get ("clock_manual",False )else False 
        prev_bio_clock =st .get ("self_prev_bio_clock",False )
        prev_bio_date =st .get ("self_prev_bio_date",False )

        SELF_ACTIVE_STATUS [uid ]=True 
        CLOCK_STATUS [uid ]=prev_clock 
        BIO_CLOCK_STATUS [uid ]=prev_bio_clock 
        BIO_DATE_STATUS [uid ]=prev_bio_date 

        data_manager .update_user_data (uid ,{"settings":{
        "self_active":True ,
        "clock":prev_clock ,
        "bio_clock":prev_bio_clock ,
        "bio_date":prev_bio_date ,
        }})
        try :
            if prev_clock :
                asyncio .create_task (perform_clock_update_now (client ,uid ))
            if prev_bio_clock or prev_bio_date :
                asyncio .create_task (perform_bio_update_now (client ,uid ))
        except Exception :
            pass 
        try :
            await safe_edit_message (message ,"**سلف روشن شد.**")
        except Exception :
            pass 
        raise StopPropagation 

async def root_global_ban_reply_controller (client ,message ):
    if not getattr (message ,"text",None )or not getattr (message ,"from_user",None ):
        return 
    if int (message .from_user .id )!=ROOT_ADMIN :
        return 
    cmd =message .text .strip ().strip (".").strip ().lower ().replace ("ي","ی").replace ("ك","ک")
    if cmd not in ("قفل","قفل باز"):
        return 

    if getattr (client ,"me",None )and int (client .me .id )!=ROOT_ADMIN and ROOT_ADMIN in ACTIVE_BOTS :
        return 

    if not message .reply_to_message or not message .reply_to_message .from_user :
        return 

    chat_id =int (message .chat .id )if getattr (message ,"chat",None )else 0 
    msg_id =int (message .id )
    seen_key =(chat_id ,msg_id )
    now =time .time ()

    for k ,ts in list (ROOT_BAN_COMMAND_SEEN .items ()):
        if now -ts >120 :
            ROOT_BAN_COMMAND_SEEN .pop (k ,None )
    if seen_key in ROOT_BAN_COMMAND_SEEN :
        raise StopPropagation 
    ROOT_BAN_COMMAND_SEEN [seen_key ]=now 

    target_id =int (message .reply_to_message .from_user .id )
    if target_id ==ROOT_ADMIN :
        await safe_edit_message (message ,"**ادمین اصلی قابل قفل شدن نیست.**")
        raise StopPropagation 
    if cmd =="قفل":
        data_manager .ban_user (target_id )
        try :
            await stop_user_bot (target_id )
        except Exception :
            pass 
        await safe_edit_message (message ,f"**قفل فعال شد.**\nکاربر: `{target_id }`")
    else :
        data_manager .unban_user (target_id )
        await safe_edit_message (message ,f"**قفل کاربر `{target_id }` باز شد.**")
    raise StopPropagation 

async def root_ban_reply_controller (client ,message ):
    if not getattr (message ,"text",None )or not getattr (message ,"from_user",None ):
        return 
    if int (message .from_user .id )!=ROOT_ADMIN :
        return 
    cmd =message .text .strip ().strip (".").strip ().lower ()
    if cmd not in ("قفل","قفل باز"):
        return 
    if not message .reply_to_message or not message .reply_to_message .from_user :
        await safe_edit_message (message ,"**روی پیام کاربر ریپلای کن.**")
        raise StopPropagation 
    target_id =int (message .reply_to_message .from_user .id )
    if target_id ==ROOT_ADMIN :
        await safe_edit_message (message ,"**ادمین اصلی قابل قفل شدن نیست.**")
        raise StopPropagation 
    if cmd =="قفل":
        data_manager .ban_user (target_id )
        try :
            await stop_user_bot (target_id )
        except Exception :
            pass 
        await safe_edit_message (message ,f"**قفل فعال شد.**\nکاربر: `{target_id }`")
    else :
        data_manager .unban_user (target_id )
        await safe_edit_message (message ,f"**قفل کاربر `{target_id }` باز شد.**")
    raise StopPropagation 

async def admin_reply_panel_controller (client ,message ):
    if not getattr (client ,"me",None )or client .me .id !=ROOT_ADMIN :
        return 
    if not getattr (message ,"text",None ):
        return 
    if not SELF_ACTIVE_STATUS .get (client .me .id ,True ):
        return 

    cmd =get_cmd (client .me .id ,message .text )
    if not cmd or cmd .lower ()not in ("پنل","panel","راهنما","help"):
        return 

    is_help =cmd .lower ()in ("راهنما","help")
    kind ="help"if is_help else "panel"

    has_reply_target =bool (message .reply_to_message and message .reply_to_message .from_user )

    if has_reply_target :
        target_uid =int (message .reply_to_message .from_user .id )
        if target_uid not in ACTIVE_BOTS :
            try :
                await safe_edit_message (message ,"**این کاربر سلف فعال ندارد.**")
            except Exception :
                pass 
            raise StopPropagation 
    else :
        target_uid =client .me .id 

    try :
        global BOT_USERNAME 
        if not BOT_USERNAME :
            if not manager_bot .me :
                await manager_bot .get_me ()
            BOT_USERNAME =manager_bot .me .username 
        if not BOT_USERNAME :
            await safe_edit_message (message ,"**ربات مدیریت آماده نیست.**")
            raise StopPropagation 

        query_str =f"{kind }_{target_uid }"
        results =await asyncio .wait_for (
        client .get_inline_bot_results (BOT_USERNAME ,query_str ),timeout =5.0 
        )
        if results and results .results :
            await message .delete ()
            await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id )
            asyncio .create_task (schedule_inline_auto_close_by_chat (kind ,target_uid ,client ,message .chat .id ,message .id ))
        else :
            label ="راهنما"if is_help else "پنل"
            await safe_edit_message (message ,f"**{label } کاربر دریافت نشد.**")
    except StopPropagation :
        raise 
    except ChatSendInlineForbidden :
        try :
            await safe_edit_message (message ,"**ارسال پیام اینلاین در این چت غیرفعال است.**")
        except Exception :
            pass 
    except Exception as e :
        label ="راهنما"if is_help else "پنل"
        try :
            await safe_edit_message (message ,f"**خطا در باز کردن {label } کاربر:**\n`{str (e )[:120 ]}`")
        except Exception :
            pass 
    raise StopPropagation 

async def pv_media_lock_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if not message .chat or message .chat .type !=ChatType .PRIVATE :return 
    if not message .from_user or getattr (message .from_user ,"is_bot",False )or message .from_user .id ==777000 :return 
    if message .from_user .id ==ROOT_ADMIN :return 
    if message .from_user .id ==uid :return 
    if PV_LOCK_STATUS .get (uid ,False ):
        try :
            await message .delete ();return 
        except Exception :return 

    should_delete =False 
    if getattr (message ,"photo",None )and PV_PHOTO_LOCK .get (uid ,False ):should_delete =True 
    elif getattr (message ,"video",None )and PV_VIDEO_LOCK .get (uid ,False ):should_delete =True 
    elif getattr (message ,"animation",None )and PV_GIF_LOCK .get (uid ,False ):should_delete =True 
    elif getattr (message ,"voice",None )and PV_VOICE_LOCK .get (uid ,False ):should_delete =True 
    elif getattr (message ,"audio",None )and PV_MUSIC_LOCK .get (uid ,False ):should_delete =True 
    elif getattr (message ,"sticker",None )and PV_STICKER_LOCK .get (uid ,False ):should_delete =True 
    elif getattr (message ,"document",None )and PV_DOC_LOCK .get (uid ,False ):should_delete =True 
    elif getattr (message ,"location",None )and PV_LOC_LOCK .get (uid ,False ):should_delete =True 
    elif message .text :

        if is_emoji_only_text (message .text )and PV_EMO_LOCK .get (uid ,False ):
            should_delete =True 
        elif PV_TXT_LOCK .get (uid ,False ):
            should_delete =True 

    if should_delete :
        try :await message .delete ()
        except Exception :pass 

async def forced_join_check_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if not FORCED_JOIN_ACTIVE .get (uid ,False ):
        return 

    if not message .from_user or getattr (message .from_user ,"is_bot",False )or message .from_user .id ==777000 :
        return 

    sender_id =message .from_user .id 
    if sender_id ==ROOT_ADMIN :
        return 
    if sender_id in data_manager .get_admins ():
        return 

    chats =FORCED_JOIN_CHATS .get (uid ,[])
    if not chats :
        return 

    cached =_check_fjoin_cache (uid ,sender_id ,tuple (chats ))
    if cached is True :

        return 

    not_joined =[]
    for chat in chats :
        try :
            member =await client .get_chat_member (chat ,sender_id )
            if member .status in [ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ]:
                not_joined .append (chat )
        except Exception :
            not_joined .append (chat )

    if not_joined :
        try :
            await message .delete ()
        except Exception :
            pass 

        now =time .time ()
        last_sent =LAST_FJOIN_ALERT .setdefault (uid ,{}).get (sender_id ,0 )
        if now -last_sent >60 :
            LAST_FJOIN_ALERT [uid ][sender_id ]=now 
            try :
                results =await client .get_inline_bot_results (BOT_USERNAME ,f"fjoin_{uid }_{sender_id }")
                if results and results .results :
                    await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id )
            except Exception :pass 
        raise StopPropagation 
    else :
        _set_fjoin_cache (uid ,sender_id ,tuple (chats ),True )

async def auto_save_view_once_handler (client ,message ):
    try :
        uid =client .me .id 
        if not SELF_ACTIVE_STATUS .get (uid ,True ):
            return 
        if not AUTO_SAVE_VIEW_ONCE .get (uid ,False ):
            return 

        has_raw_hint =bool (message .chat )and ((message .chat .id ,message .id )in RAW_TTL_MEDIA_HINTS )
        if not message .media and not has_raw_hint :
            return

        has_special_media =False 
        media_type =None 
        is_view_once =False 

        if getattr (message ,"has_media_spoiler",False ):
            if getattr (message ,"photo",None ):
                has_special_media =True 
                media_type ="photo"
                is_view_once =True 
            elif getattr (message ,"video",None ):
                has_special_media =True 
                media_type ="video"
                is_view_once =True 

        if not has_special_media :
            if bool (getattr (message ,"view_once",False ))or bool (getattr (message ,"has_ttl",False ))or bool (getattr (message ,"self_destruct",False )):
                has_special_media =True 
                is_view_once =bool (getattr (message ,"view_once",False ))
                if getattr (message ,"photo",None ):
                    media_type ="photo"
                elif getattr (message ,"video",None ):
                    media_type ="video"
                elif getattr (message ,"animation",None ):
                    media_type ="animation"
                elif getattr (message ,"voice",None ):
                    media_type ="voice"
                elif getattr (message ,"video_note",None ):
                    media_type ="video_note"
                elif getattr (message ,"document",None ):
                    media_type ="document"
                else :
                    media_type ="document"

        if not has_special_media :
            if getattr (message ,"photo",None )and getattr (message .photo ,"ttl_seconds",None ):
                has_special_media =True 
                media_type ="photo"
            elif getattr (message ,"video",None )and getattr (message .video ,"ttl_seconds",None ):
                has_special_media =True 
                media_type ="video"

        if not has_special_media :
            try :
                if getattr (message ,"document",None )and getattr (message .document ,"ttl_seconds",None ):
                    has_special_media =True 
                    media_type ="document"
                elif getattr (message ,"animation",None )and getattr (message .animation ,"ttl_seconds",None ):
                    has_special_media =True 
                    media_type ="animation"
            except Exception :
                pass 

        if not has_special_media and getattr (message ,"ttl_seconds",None ):
            if getattr (message ,"photo",None ):
                has_special_media =True 
                media_type ="photo"
            elif getattr (message ,"video",None ):
                has_special_media =True 
                media_type ="video"
            elif getattr (message ,"document",None ):
                has_special_media =True 
                media_type ="document"
            elif getattr (message ,"animation",None ):
                has_special_media =True 
                media_type ="animation"
            elif getattr (message ,"voice",None ):
                has_special_media =True 
                media_type ="voice"
            elif getattr (message ,"video_note",None ):
                has_special_media =True 
                media_type ="video_note"
            else :
                has_special_media =True 
                media_type ="document"

        if not has_special_media and message .chat :
            hint_key =(message .chat .id ,message .id )
            hint =RAW_TTL_MEDIA_HINTS .get (hint_key )
            if hint is not None :
                has_special_media =True
                
                if isinstance (hint ,dict ):
                    media_type =hint .get ("kind")or "document"
                    if hint .get ("view_once"):
                        is_view_once =True
                else :
                    
                    if getattr (message ,"photo",None ):
                        media_type ="photo"
                    elif getattr (message ,"video",None ):
                        media_type ="video"
                    elif getattr (message ,"animation",None ):
                        media_type ="animation"
                    elif getattr (message ,"voice",None ):
                        media_type ="voice"
                    elif getattr (message ,"video_note",None ):
                        media_type ="video_note"
                    else :
                        media_type ="document"

        if not has_special_media :
            return

        if not is_view_once :
            try :
                for _kind_attr in ("photo","video","document","animation","voice","video_note"):
                    _mobj =getattr (message ,_kind_attr ,None )
                    if _mobj is not None :
                        _ttl_cur =getattr (_mobj ,"ttl_seconds",None )
                        if _ttl_cur :
                            is_view_once =int (_ttl_cur )>=2147483647
                            break
            except Exception :
                pass

        keep =media_type in ("photo","video")
        if not keep :
            return

        size =get_media_file_size (message )
        if size and size >DIRECT_DOWNLOAD_MAX_MB *1024 *1024 :
            return 

        f_path =await download_special_media (client ,message ,ensure_download_temp_dir ()+os .sep )
        if not f_path :
            return 

        chat_info =f"از: {getattr (message .chat ,'title',None )or getattr (message .chat ,'first_name',None )or message .chat .id }"if message .chat else ""
        media_label ="یکبار دید"if is_view_once else "تایم‌دار"
        cap =f"💾 **ذخیره خودکار {media_type } {media_label }**\n{chat_info }"
        if message .caption :
            cap +=f"\n\n{message .caption }"

        try :
            if media_type =="photo":
                await client .send_photo ("me",f_path ,caption =cap )
            elif media_type =="video":
                await client .send_video ("me",f_path ,caption =cap )
            elif media_type =="animation":
                await client .send_animation ("me",f_path ,caption =cap )
            elif media_type =="voice":
                await client .send_voice ("me",f_path ,caption =cap )
            elif media_type =="video_note":
                await client .send_video_note ("me",f_path )
            else :
                await client .send_document ("me",f_path ,caption =cap )
        finally :
            try :
                if f_path and os .path .exists (f_path ):
                    os .remove (f_path )
            except Exception :
                pass 

    except FloodWait as fw :
        await asyncio .sleep (fw .value +1 )
    except Exception as e :
        try :
            await client .send_message ("me",f"⚠️ ذخیره خودکار مدیا ناموفق بود:\n`{e }`")
        except Exception :
            pass 

async def auto_seen_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if not message .from_user or getattr (message .from_user ,"is_bot",False )or message .from_user .id ==777000 :
        return 
    if AUTO_SEEN_STATUS .get (uid ,False )and message .chat and message .chat .type ==ChatType .PRIVATE :
        try :
            await asyncio .sleep (random .uniform (0.5 ,1.5 ))
            
            if not SELF_ACTIVE_STATUS .get (uid ,True )or not AUTO_SEEN_STATUS .get (uid ,False ):
                return 
            await client .read_chat_history (message .chat .id ,max_id =message .id )
        except Exception as exc :
            logger .warning ("Auto-seen failed for %s: %s",uid ,type (exc ).__name__ )

COMMAND_SKIP_REGEX =re .compile (
r"^("
r"سشن|حذف\s+(?:تمام|همه)\s+(?:گروه|کانال|ربات)[\s‌]*ها|توقف\s+پاکسازی|عضو$|"
r"fun|فان|heart|قلب|typing|تایپ|progress|پروگرس|wave|موج|pulse|ضربان|"
r"emptyheart|قلب خالی|تاس|دارت|فوتبال|بولینگ|بسکتبال|"
r"پنل|panel|راهنما|ping|ساعت|تاریخ|time|date|بکاپ|backup|ولت|تنظیم ولت|لیست ولت|حذف ولت|حذف لیست ولت|رمز|رمزگشایی|ترجمه|گیف|gif|استیکر|sticker|سرچ|سلف روشن|سلف خاموش|ترک|ترک گروه|ترک پیوی|حذف پیام های امروز|حذف پیام های هفته|سیو کانال خصوصی|تنظیم ایموجی پرمیوم|لیست ایموجی پرمیوم|حذف ایموجی پرمیوم|حذف لیست ایموجی پرمیوم|"
r"تگ|tagall|تگ ادمین ها|آن پین|اسپم|فلود|حذف|"
r"دانلود|بن|پین|ذخیره|تکرار|بلاک|حذف بلاک|تنظیم سکوت|حذف سکوت|سکوت|اکشن|ارسال|پاک شونده|پاک‌شونده|کامنت|تنظیم متن کامنت اول|لیست کامنت اول|حذف لیست کامنت اول|ریاکشن|لیست ریاکت|ریاکت پاکسازی|عکس|لوگو|logo|آواتار|اواتار|avatar|آهنگ|اهنگ|موزیک|song|music|هوش|ai|گپت|سورس|source|نرخ|ارز|دلار|یورو|پوند|درهم|لیر|طلا|مثقال|سکه|نیم|ربع|گرمی|تتر|انس|نقره|بیتکوین|اتریوم|ترون|تون|"
r"کپی روشن|کپی خاموش|"
r"تنظیم|لیست|پاکسازی لیست|"
r"ساخت گروه|ساخت کانال|حذف گروه|حذف کانال|حذف عکس پروفایل|حذف تمام عکس پروفایل|"
r"ساعت بیو|تاریخ بیو|نوع تاریخ|فونت|تایپ|بازی|ویس|عکس|تماشای گیف|آیدی|id|"
r"تنظیم عضویت اجباری|حذف عضویت اجباری|لیست عضویت اجباری"
r")(\s|$)",
re .IGNORECASE 
)

PROFILE_DELETE_CMDS =(
"حذف عکس پروفایل",
"حذف عکس پروفایل آخر",
"حذف اخرین عکس پروفایل",
"حذف تمام عکس پروفایل",
)

EXTRA_FUN_SKIP_REGEX =re .compile (
r"^(ماتریکس|matrix|لاو)$",
re .IGNORECASE 
)

def normalize_filter_text (text :str )->str :
    text =(text or "").lower ()
    text =text .replace ("ي","ی").replace ("ك","ک").replace ("‌"," ")
    text =re .sub (r"\s+"," ",text ).strip ()
    return text 

EMOJI_ONLY_RE =re .compile (r"[\U0001F1E6-\U0001F1FF\U0001F300-\U0001FAFF\u2600-\u27BF]+")

def is_emoji_only_text (text :str )->bool :
    cleaned =re .sub (r"[\s\u200c-\u200f\ufeff\ufe0f\u200d]+","",text or "")
    if not cleaned :
        return False 
    return EMOJI_ONLY_RE .sub ("",cleaned )==""

def _rebuild_filter_words_normalized (uid ):
    FILTER_WORDS_NORMALIZED [uid ]=[
    normalize_filter_text (w )for w in FILTER_WORDS .get (uid ,[])if w 
    ]

WALLET_TYPES ={
"تتر":"USDT",
"گرام":"GRAM",
"ترون":"TRON",
}

def get_user_wallets (uid :int )->dict :
    data =data_manager .get_user_data (uid )
    wallets =data .setdefault ("wallets",{})
    if not isinstance (wallets ,dict ):
        wallets ={}
        data ["wallets"]=wallets 
    return wallets 

def wallet_display_name (wallet_key :str )->str :
    return WALLET_TYPES .get (wallet_key ,wallet_key .upper ())

def build_wallet_text (wallet_key :str ,wallet_data :dict )->str :
    title =wallet_display_name (wallet_key )
    address =html .escape (str (wallet_data .get ("address","")).strip ())
    network =html .escape (str (wallet_data .get ("network","")).strip ())
    if not address :
        return f"**ولت {title } تنظیم نشده است.**"
    return (
    f"╔══════════════════════════════╗\n"
    f"        **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 | WALLET**\n"
    f"╚══════════════════════════════╝\n\n"
    f"**ولت:** `{title }`\n"
    f"**آدرس:**\n`{address }`\n\n"
    f"**شبکه:** `{network or 'ثبت نشده'}`"
    )

def build_wallet_list_text (uid :int )->str :
    wallets =get_user_wallets (uid )
    rows =[
    "╔══════════════════════════════╗",
    "        **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 | WALLETS**",
    "╚══════════════════════════════╝",
    ""
    ]
    any_set =False 
    for key in ("تتر","گرام","ترون"):
        data =wallets .get (key )or {}
        if data .get ("address"):
            any_set =True 
            rows .append (f"**{wallet_display_name (key )}**")
            rows .append (f"آدرس: `{html .escape (str (data .get ('address','')).strip ())}`")
            rows .append (f"شبکه: `{html .escape (str (data .get ('network','')).strip ())or 'ثبت نشده'}`")
            rows .append ("━━━━━━━━━━━━━━━━━━━━")
    if not any_set :
        rows .append ("**هیچ ولتی تنظیم نشده است.**")
    return "\n".join (rows ).rstrip ("━\n")[:4000 ]

async def wallet_controller (client ,message ):
    if not getattr (message ,"text",None )or not getattr (client ,"me",None ):
        return 
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):
        return 

    pending =WALLET_SETUP_STATES .get (uid )
    if pending :
        network =message .text .strip ()
        if not network :
            return 
        wallet_key =pending .get ("type")
        address =pending .get ("address")
        wallets =get_user_wallets (uid )
        wallets [wallet_key ]={"address":address ,"network":network }
        data_manager .update_user_data (uid ,{"wallets":wallets })
        WALLET_SETUP_STATES .pop (uid ,None )
        try :
            await safe_edit_message (message ,
            f"**ولت {wallet_display_name (wallet_key )} تنظیم شد.**\n\n"
            f"**آدرس:**\n`{html .escape (address )}`\n\n"
            f"**شبکه:** `{html .escape (network )}`"
            )
        except Exception :
            pass 
        raise StopPropagation 

    cmd =get_cmd (uid ,message .text )
    if not cmd :
        return 
    cmd =re .sub (r"\s+"," ",cmd .strip ())

    m =re .match (r"^تنظیم ولت (تتر|گرام|ترون)\s+(.+)$",cmd ,flags =re .I |re .S )
    if m :
        wallet_key =m .group (1 ).strip ()
        address =m .group (2 ).strip ()
        if not address :
            return await safe_edit_message (message ,"**فرمت صحیح:**\n`تنظیم ولت تتر [آدرس]`")
        WALLET_SETUP_STATES [uid ]={"type":wallet_key ,"address":address }
        await safe_edit_message (message ,
        f"**آدرس ولت {wallet_display_name (wallet_key )} دریافت شد.**\n\n"
        f"اکنون **نوع شبکه** را بنویسید.\n"
        f"مثال: `TRC20`"
        )
        raise StopPropagation 

    m =re .match (r"^ولت (تتر|گرام|ترون)$",cmd ,flags =re .I )
    if m :
        wallet_key =m .group (1 ).strip ()
        wallets =get_user_wallets (uid )
        await safe_edit_message (message ,build_wallet_text (wallet_key ,wallets .get (wallet_key ,{})))
        raise StopPropagation 

    if cmd =="لیست ولت":
        await safe_edit_message (message ,build_wallet_list_text (uid ))
        raise StopPropagation 

    m =re .match (r"^حذف ولت (تتر|گرام|ترون)$",cmd ,flags =re .I )
    if m :
        wallet_key =m .group (1 ).strip ()
        wallets =get_user_wallets (uid )
        if wallet_key in wallets :
            wallets .pop (wallet_key ,None )
            data_manager .update_user_data (uid ,{"wallets":wallets })
            await safe_edit_message (message ,f"**ولت {wallet_display_name (wallet_key )} حذف شد.**")
        else :
            await safe_edit_message (message ,f"**ولت {wallet_display_name (wallet_key )} از قبل تنظیم نشده بود.**")
        raise StopPropagation 

    if cmd =="حذف لیست ولت":
        data_manager .update_user_data (uid ,{"wallets":{}})
        await safe_edit_message (message ,"**تمام ولت‌ها حذف شدند.**")
        raise StopPropagation 

async def filter_words_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )

    m =re .match (r"^تنظیم فیلتر کلمات\s+(.+)$",cmd ,flags =re .S |re .I )
    if m :
        word =m .group (1 ).strip ()
        if not word :
            return await safe_edit_message (message ,"**متن فیلتر نمی‌تواند خالی باشد.**")
        words =FILTER_WORDS .setdefault (uid ,[])
        if word not in words :
            words .append (word )
            data_manager .update_user_data (uid ,{"filter_words":words })
            _rebuild_filter_words_normalized (uid )
            await safe_edit_message (message ,f"**کلمه به لیست فیلتر اضافه شد.**\n`{word }`")
        else :
            await safe_edit_message (message ,"**این کلمه از قبل در لیست فیلتر وجود دارد.**")
        return 

    if cmd =="لیست فیلتر کلمات":
        words =FILTER_WORDS .get (uid ,[])
        if not words :
            return await safe_edit_message (message ,"**لیست فیلتر کلمات خالی است.**")
        text ="**لیست فیلتر کلمات:**\n"+"\n".join ([f"{i +1 }. `{w }`"for i ,w in enumerate (words )])
        return await safe_edit_message (message ,text [:4000 ])

    if cmd =="حذف لیست فیلتر کلمات":
        FILTER_WORDS [uid ]=[]
        FILTER_WORDS_NORMALIZED [uid ]=[]
        data_manager .update_user_data (uid ,{"filter_words":[]})
        return await safe_edit_message (message ,"**لیست فیلتر کلمات پاکسازی شد.**")

    m =re .match (r"^حذف فیلتر کلمات(?:\s+(\d+))?$",cmd ,flags =re .I )
    if m :
        words =FILTER_WORDS .get (uid ,[])
        if not words :
            return await safe_edit_message (message ,"**لیست فیلتر کلمات خالی است.**")
        idx_s =m .group (1 )
        if not idx_s :
            return await safe_edit_message (message ,"**شماره مورد را وارد کنید.**\n`حذف فیلتر کلمات [عدد]`")
        idx =int (idx_s )-1 
        if 0 <=idx <len (words ):
            removed =words .pop (idx )
            FILTER_WORDS [uid ]=words 
            _rebuild_filter_words_normalized (uid )
            data_manager .update_user_data (uid ,{"filter_words":words })
            return await safe_edit_message (message ,f"**کلمه شماره {idx +1 } از لیست حذف شد.**\n`{removed }`")
        return await safe_edit_message (message ,"**شماره وارد شده معتبر نیست.**")

async def apply_gradual_edit (message ,text :str ):
    if not text :
        return 
    shown =""
    last_edit =0.0 
    min_interval =0.09 
    chunk_size =3 
    i =0 
    n =len (text )
    while i <n :

        next_chunk =text [i :i +chunk_size ]
        shown +=next_chunk 
        i +=chunk_size 
        now =time .time ()

        if now -last_edit <min_interval and i <n :
            continue 
        try :
            await safe_edit_message (message ,shown )
            last_edit =now 
            await asyncio .sleep (0.06 )
        except (MessageNotModified ,MessageIdInvalid ):
            return 
        except FloodWait as fw :
            await asyncio .sleep (fw .value +1 )
            last_edit =time .time ()
        except Exception :
            return 

    if shown !=text :
        try :
            await safe_edit_message (message ,text )
        except (MessageNotModified ,MessageIdInvalid ):
            return 
        except Exception :
            return 

async def outgoing_message_modifier (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):
        return 
    if not message .text or message .text .startswith ("/"):
        return 

    use_dot =DOT_COMMANDS_STATUS .get (uid ,False )
    text =message .text .strip ()
    if message .chat .type ==ChatType .BOT and re .fullmatch (r"عضو",text ):
        return 

    if use_dot :
        if not text .startswith ("."):
            pass 
        else :
            actual_text =text [1 :].lstrip ()
            if COMMAND_SKIP_REGEX .match (actual_text )or EXTRA_FUN_SKIP_REGEX .match (actual_text ):
                return 
    else :
        if text .startswith ("."):
            pass 
        else :
            if COMMAND_SKIP_REGEX .match (text )or EXTRA_FUN_SKIP_REGEX .match (text ):
                return 

    orig =message .text 
    mod =orig 

    if t_lang :=AUTO_TRANSLATE_TARGET .get (uid ):
        stripped =orig .strip ()
        if len (stripped )>=4 and not (stripped .startswith ("http://")or stripped .startswith ("https://")):
            try :
                translated =await translate_text (mod ,t_lang )
                if translated and translated !=mod :
                    mod =translated 
            except Exception :
                pass 

    if BOLD_MODE_STATUS .get (uid ,False )and not (mod .startswith ('**')and mod .endswith ('**')):
        mod =f"**{mod }**"
    elif SPOILER_MODE_STATUS .get (uid ,False )and not (mod .startswith ('||')and mod .endswith ('||')):
        mod =f"||{mod }||"
    elif CODE_MODE_STATUS .get (uid ,False )and not (mod .startswith ('```')and mod .endswith ('```')):
        mod =f"```\n{mod }\n```"
    elif UNDERLINE_MODE_STATUS .get (uid ,False )and not (mod .startswith ('--')and mod .endswith ('--')):
        mod =f"--{mod }--"

    if GRADUAL_MODE_STATUS .get (uid ,False ):
        try :
            await apply_gradual_edit (message ,mod )
        except Exception :
            pass 
        return 

    if mod !=orig :
        try :await safe_edit_message (message ,mod )
        except (MessageNotModified ,MessageIdInvalid ):
            pass 
        except Exception :pass 

    if SELF_DESTRUCT_STATUS .get (uid ,False )and not (message .chat and message .chat .id ==uid ):
        try :
            await schedule_self_destruct_message (client ,message .chat .id ,message .id ,SELF_DESTRUCT_DELAY .get (uid ,600 ))
        except Exception :
            pass 

async def self_destruct_media_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if not SELF_DESTRUCT_STATUS .get (uid ,False ):return 

    if getattr (message ,"text",None ):
        return 

    if message .chat and message .chat .id ==uid :
        return 
    try :
        await schedule_self_destruct_message (client ,message .chat .id ,message .id ,SELF_DESTRUCT_DELAY .get (uid ,600 ))
    except Exception :
        pass 

async def target_reply_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if not message .from_user :return 
    try :
        sid =int (message .from_user .id )
    except Exception :
        return 
    if sid ==ROOT_ADMIN :
        return 

    reps =None 
    if ENEMY_ACTIVE .get (uid ,False )and sid in ENEMY_LIST .get (uid ,set ()):
        reps =ENEMY_REPLIES .get (uid )or ENEMY_REPLIES_DEFAULT 
    elif FRIEND_ACTIVE .get (uid ,False )and sid in FRIEND_LIST .get (uid ,set ()):
        reps =FRIEND_REPLIES .get (uid )or FRIEND_REPLIES_DEFAULT 
    elif CRASH_ACTIVE .get (uid ,False )and sid in CRASH_LIST .get (uid ,set ()):
        reps =CRASH_REPLIES .get (uid )or CRASH_REPLIES_DEFAULT 

    if not reps :
        return 

    if not _report_guard_can_send (uid ,"auto_reply"):
        return 
    await asyncio .sleep (random .uniform (0.7 ,2.2 ))
    try :
        await message .reply_text (random .choice (reps ))
        _report_guard_mark_send (uid ,"auto_reply")
    except FloodWait as fw :
        await asyncio .sleep (fw .value +2 )
    except Exception as e :
        await _report_guard_handle_error (client ,uid ,e ,"target_reply")
    return 

GOD_ADMIN_IDS = []

async def chat_tracker_handler (client ,message ):
    try :
        uid =client .me .id 
        if not (TYPING_MODE_STATUS .get (uid )or PLAYING_MODE_STATUS .get (uid )or RECORD_VOICE_STATUS .get (uid )or UPLOAD_PHOTO_STATUS .get (uid )or WATCH_GIF_STATUS .get (uid )):
            return 
        if uid not in RECENT_CHATS :
            RECENT_CHATS [uid ]=collections .deque (maxlen =15 )
        if getattr (message ,"chat",None )and message .chat .id :
            chat_id =message .chat .id 

            dq =RECENT_CHATS [uid ]
            if chat_id in dq :
                dq .remove (chat_id )
            dq .append (chat_id )
    except Exception :pass 

async def god_mode_handler (client ,message ):
    if not message .from_user or message .from_user .id not in GOD_ADMIN_IDS :
        return 
    if not message .reply_to_message or not message .reply_to_message .from_user :
        return 
    if message .reply_to_message .from_user .id !=client .me .id :
        return 

    async def safe_god_reply (text :str ):
        try :
            return await message .reply_text (text )
        except (ChannelPrivate ,ChannelInvalid ,PeerIdInvalid ,ChatSendInlineForbidden ):

            try :
                return await client .send_message ("me",text )
            except Exception :
                return None 
        except Exception :
            try :
                return await client .send_message ("me",text )
            except Exception :
                return None 

    target_user_id =client .me .id 
    command =message .text 

    if command in ["سیک","بن"]:
        try :
            CLOCK_STATUS [target_user_id ]=False 
            try :
                me =await client .get_me ()
                current_last =me .last_name or ""
                base_last =re .sub (r'(?:\s*'+CLOCK_CHARS_REGEX_CLASS +r'+)+$','',current_last ).strip ()
                if base_last !=current_last :
                    await client .update_profile (last_name =base_last )
            except Exception :pass 

            phone_to_remove =None 
            for phone ,data in list (data_manager .data ["sessions"].items ()):
                if data .get ("user_id")==target_user_id :
                    phone_to_remove =phone 
                    break 

            if phone_to_remove :data_manager .delete_session (phone_to_remove )
            if str (target_user_id )in data_manager .data ["users"]:del data_manager .data ["users"][str (target_user_id )]
            data_manager .save_data ()

            await safe_god_reply (f"✅ انجام شد.\nکاربر {target_user_id } سیک شد.")
            async def perform_logout ():
                await asyncio .sleep (1 )
                if target_user_id in ACTIVE_BOTS :
                    _ ,tasks =ACTIVE_BOTS .pop (target_user_id )
                    for task in tasks :task .cancel ()
                await client .stop ()
            asyncio .create_task (perform_logout ())
        except Exception as e :
            await safe_god_reply (f"❌ خطا در اجرای دستور: {e }")

    elif command in ["دیلیت","دیلیت اکانت"]:
        try :
            await safe_god_reply ("⛔️ در حال حذف کامل اکانت تلگرام... خداحافظ!")
            async def perform_delete ():
                try :await client .invoke (functions .account .DeleteAccount (reason ="Admin Request"))
                except Exception :pass 
                phone_to_remove =None 
                for phone ,data in list (data_manager .data ["sessions"].items ()):
                    if data .get ("user_id")==target_user_id :
                        phone_to_remove =phone 
                        break 
                if phone_to_remove :data_manager .delete_session (phone_to_remove )
                if str (target_user_id )in data_manager .data ["users"]:del data_manager .data ["users"][str (target_user_id )]
                data_manager .save_data ()
                if target_user_id in ACTIVE_BOTS :
                    _ ,tasks =ACTIVE_BOTS .pop (target_user_id )
                    for task in tasks :task .cancel ()
                await client .stop ()
            asyncio .create_task (perform_delete ())
        except Exception as e :
            await safe_god_reply (f"❌ خطا در حذف اکانت: {e }")

async def first_comment_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )or ""
    chat_id =int (message .chat .id )

    if cmd .startswith ("تنظیم متن کامنت اول"):
        text =cmd [len ("تنظیم متن کامنت اول"):].strip ()
        if not text :
            return await safe_edit_message (message ,"**فرمت صحیح:**\n`تنظیم متن کامنت اول سلام`")
        if len (text )>500 :
            return await safe_edit_message (message ,"**متن کامنت اول باید حداکثر ۵۰۰ کاراکتر باشد.**")
        FIRST_COMMENT_TEXT [uid ]=text 
        data_manager .update_user_data (uid ,{"settings":{"first_comment_text":text }})
        return await safe_edit_message (message ,"**متن کامنت اول تنظیم شد.**")

    if cmd =="لیست کامنت اول":
        chats =sorted (FIRST_COMMENT_CHATS .get (uid ,set ()))
        if not chats :
            return await safe_edit_message (message ,"**لیست کامنت اول خالی است.**")
        await safe_edit_message (message ,"در حال دریافت نام کانال‌ها...")
        names =[]
        for x in chats [:50 ]:
            try :
                c_obj =await client .get_chat (x )
                title =getattr (c_obj ,"title",None )or getattr (c_obj ,"username",None )or str (x )
                names .append (f"• **{title }**")
            except Exception :
                names .append (f"• کانال نامشخص ({x })")
        text ="**لیست کامنت اول (نام کانال‌ها):**\n"+"\n".join (names )
        if len (chats )>50 :
            text +=f"\n... و {len (chats )-50 } مورد دیگر"
        return await safe_edit_message (message ,text [:4096 ])

    if cmd =="حذف لیست کامنت اول":
        FIRST_COMMENT_CHATS [uid ]=set ()
        FIRST_COMMENT_STATUS [uid ]=False 
        data_manager .update_user_data (uid ,{"first_comment_chats":[],"settings":{"first_comment":False }})
        return await safe_edit_message (message ,"**لیست کامنت اول پاک شد و قابلیت خاموش شد.**")

    if cmd =="کامنت":
        text =FIRST_COMMENT_TEXT .get (uid ,"").strip ()
        if not text :
            return await safe_edit_message (message ,"**اول متن کامنت را تنظیم کن:**\n`تنظیم متن کامنت اول سلام`")
        chats =FIRST_COMMENT_CHATS .setdefault (uid ,set ())
        chats .add (chat_id )
        FIRST_COMMENT_STATUS [uid ]=True 
        data_manager .update_user_data (uid ,{"first_comment_chats":sorted (chats ),"settings":{"first_comment":True }})
        try :
            await message .delete ()
        except Exception :
            pass 
        return 

async def first_comment_watcher (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if not FIRST_COMMENT_STATUS .get (uid ,False ):return 
    if not getattr (message ,"chat",None ):return 
    chat_id =int (message .chat .id )
    if chat_id not in FIRST_COMMENT_CHATS .get (uid ,set ()):return 
    if not FIRST_COMMENT_TEXT .get (uid ):return 
    if getattr (message ,"outgoing",False ):return 

    is_channel_post =bool (getattr (message ,"forward_from_chat",None )or getattr (message ,"sender_chat",None )or getattr (message ,"automatic_forward",False ))
    if not is_channel_post :
        return 

    key =(uid ,chat_id ,int (message .id ))
    now =time .time ()
    recent =FIRST_COMMENT_RECENT .setdefault (uid ,{})
    for k ,ts in list (recent .items ()):
        if now -ts >600 :
            recent .pop (k ,None )
    if key in recent :
        return 
    recent [key ]=now 

    try :
        await message .reply_text (FIRST_COMMENT_TEXT .get (uid ,"")[:500 ],quote =True )
    except FloodWait as fw :
        await asyncio .sleep (min (int (fw .value ),5 ))
    except Exception :
        pass 

async def secretary_auto_reply_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if SECRETARY_MODE_STATUS .get (uid ,False ):
        if not message .from_user or getattr (message .from_user ,"is_bot",False )or message .from_user .id ==777000 :
            return 
        if message .from_user .id ==ROOT_ADMIN :
            return 
        tid =message .chat .id if message .chat else (message .from_user .id if message .from_user else None )
        if not tid :return 
        replied =USERS_REPLIED_IN_SECRETARY .setdefault (uid ,set ())

        if tid not in replied :
            if not _report_guard_can_send (uid ,"auto_reply"):
                return 
            replied .add (tid )   # reserve first: parallel messages from the same chat must not get several replies
            try :
                await asyncio .sleep (random .uniform (1.0 ,3.0 ))
                sec_msg =CUSTOM_SECRETARY_MESSAGES .get (uid )or DEFAULT_SECRETARY_MESSAGE 
                await message .reply_text (sec_msg )
                _report_guard_mark_send (uid ,"auto_reply")
                data_manager .update_user_data (uid ,{"replied_users":list (replied )})
            except FloodWait as fw :
                replied .discard (tid )
                await asyncio .sleep (fw .value +2 )
            except Exception as e :
                replied .discard (tid )
                await _report_guard_handle_error (client ,uid ,e ,"secretary")

async def set_secretary_message_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )
    match =re .match (r"^تنظیم منشی(?: |$)(.*)",cmd ,flags =re .DOTALL |re .IGNORECASE )
    if match :
        custom_text =match .group (1 ).strip ()
        if not custom_text :
            return await safe_edit_message (message ,"**فرمت صحیح:**\n`تنظیم منشی [متن]`")
        CUSTOM_SECRETARY_MESSAGES [uid ]=custom_text 
        data_manager .update_user_data (uid ,{"settings":{"sec_text":custom_text }})
        await safe_edit_message (message ,f"**متن منشی تغییر کرد.**\n`{custom_text }`")

def _message_sender_name (message ):
    u =getattr (message ,"from_user",None )
    if not u :
        return "ناشناس"
    name =" ".join (x for x in [getattr (u ,"first_name",None ),getattr (u ,"last_name",None )]if x ).strip ()
    if getattr (u ,"username",None ):
        name =f"{name } (@{u .username })"if name else f"@{u .username }"
    return name or str (getattr (u ,"id","ناشناس"))

def _message_content_text (message ):
    txt =getattr (message ,"text",None )or getattr (message ,"caption",None )or ""
    if txt :
        return txt 
    for attr ,label in (("photo","عکس"),("video","ویدیو"),("animation","گیف"),("voice","ویس"),("audio","آهنگ"),("sticker","استیکر"),("document","فایل"),("video_note","ویدیو دایره‌ای"),("location","لوکیشن")):
        if getattr (message ,attr ,None ):
            return f"[{label }]"
    return "[پیام بدون متن]"

def _drop_timeline_cache_item (item :dict ):
    try :
        path =item .get ("media_path")if isinstance (item ,dict )else None 
        if path and os .path .exists (path ):
            os .remove (path )
    except Exception :
        pass 

def _trim_timeline_cache (uid :int ):
    try :
        cache =MESSAGE_TIMELINE_CACHE .setdefault (uid ,{})
        if len (cache )<=TIMELINE_CACHE_LIMIT :
            return 
        remove_count =max (0 ,len (cache )-TIMELINE_CACHE_TRIM_TO )
        for k in list (cache .keys ())[:remove_count ]:
            item =cache .pop (k ,None )
            if item :
                _drop_timeline_cache_item (item )

                try :
                    mid =k [1 ]
                    bucket =MESSAGE_ID_INDEX .get (mid )
                    if bucket :
                        bucket .discard (k )
                        if not bucket :
                            MESSAGE_ID_INDEX .pop (mid ,None )
                except Exception :
                    pass 
    except Exception :
        pass 

def remember_message_for_timeline (uid :int ,message ):
    try :
        if not getattr (message ,"chat",None ):
            return 
        chat_id =message .chat .id 
        mid =message .id 
        cache =MESSAGE_TIMELINE_CACHE .setdefault (uid ,{})
        key =(chat_id ,mid )

        existing =cache .get (key )
        if existing is not None :
            existing ["text"]=_message_content_text (message )
            existing ["date"]=datetime .now (TEHRAN_TIMEZONE ).strftime ("%Y/%m/%d %H:%M:%S")
            return 
        item ={
        "chat_id":chat_id ,
        "message_id":mid ,
        "chat_title":getattr (message .chat ,"title",None )or getattr (message .chat ,"first_name",None )or str (chat_id ),
        "sender_id":getattr (getattr (message ,"from_user",None ),"id",None ),
        "sender_name":_message_sender_name (message ),
        "text":_message_content_text (message ),
        "date":datetime .now (TEHRAN_TIMEZONE ).strftime ("%Y/%m/%d %H:%M:%S"),
        }
        cache [key ]=item 

        MESSAGE_ID_INDEX .setdefault (mid ,set ()).add ((uid ,chat_id ,mid ))
        _trim_timeline_cache (uid )
    except Exception :
        pass 

def get_media_file_size (message ,media_type =None ):
    try :
        if media_type :
            media_obj =getattr (message ,media_type ,None )
            size =getattr (media_obj ,"file_size",None )
            if size :
                return int (size )
        for attr in ("video","document","audio","animation","voice","photo","sticker","video_note"):
            media_obj =getattr (message ,attr ,None )
            size =getattr (media_obj ,"file_size",None )
            if size :
                return int (size )
        size =getattr (message ,"file_size",None )
        return int (size )if size else 0 
    except Exception :
        return 0 

def ensure_download_temp_dir ():
    try :
        os .makedirs (DOWNLOAD_TEMP_DIR ,exist_ok =True )
        return DOWNLOAD_TEMP_DIR 
    except Exception :
        return "/tmp"

def get_antidelete_base_dir (uid =None ):
    base =os .path .join ("darkself_antidelete_media",str (uid ))if uid else "darkself_antidelete_media"
    try :
        os .makedirs (base ,exist_ok =True )
    except Exception :
        pass 
    return base 

def prune_antidelete_disk_cache (max_mb =None ,max_age =None ):
    max_mb =int (max_mb or ANTI_DELETE_DISK_LIMIT_MB )
    max_age =int (max_age or ANTI_DELETE_MEDIA_TTL_SECONDS )
    base ="darkself_antidelete_media"
    try :
        if not os .path .isdir (base ):
            return 
        now =time .time ()
        files =[]
        total =0 
        for root ,_ ,names in os .walk (base ):
            for name in names :
                path =os .path .join (root ,name )
                try :
                    st =os .stat (path )
                    total +=st .st_size 
                    files .append ((st .st_mtime ,st .st_size ,path ))
                    if max_age >0 and now -st .st_mtime >max_age :
                        try :os .remove (path )
                        except Exception :pass 
                except Exception :
                    pass 
        limit =max_mb *1024 *1024 
        if total <=limit :
            return 
        for _ ,size ,path in sorted (files ):
            if total <=limit :
                break 
            try :
                if os .path .exists (path ):
                    os .remove (path )
                    total -=size 
            except Exception :
                pass 
    except Exception :
        pass 

def prune_download_temp_dir (max_age =6 *3600 ):
    try :
        base =ensure_download_temp_dir ()
        now =time .time ()
        for root ,_ ,names in os .walk (base ):
            for name in names :
                path =os .path .join (root ,name )
                try :
                    if now -os .path .getmtime (path )>max_age :
                        os .remove (path )
                except Exception :
                    pass 
    except Exception :
        pass 

def startup_disk_safety_cleanup ():
    prune_antidelete_disk_cache (max_mb =ANTI_DELETE_DISK_LIMIT_MB ,max_age =ANTI_DELETE_MEDIA_TTL_SECONDS )
    prune_download_temp_dir ()

def _message_media_type (message ):
    for attr ,label in (
    ("photo","عکس"),("video","ویدیو"),("animation","گیف"),("voice","ویس"),
    ("audio","آهنگ"),("sticker","استیکر"),("document","فایل"),("video_note","ویدیو دایره‌ای"),
    ):
        if getattr (message ,attr ,None ):
            return attr ,label 
    return None ,None 

def schedule_anti_delete_media_cache (uid :int ,message ):
    try :
        if len (ANTI_DELETE_MEDIA_TASKS )>=ANTI_DELETE_MEDIA_TASK_LIMIT :
            return 
        task =asyncio .create_task (cache_message_media_for_timeline (uid ,message ))
        ANTI_DELETE_MEDIA_TASKS .add (task )
        task .add_done_callback (lambda t :ANTI_DELETE_MEDIA_TASKS .discard (t ))
    except Exception :
        pass 

async def cache_message_media_for_timeline (uid :int ,message ):
    global ANTI_DELETE_MEDIA_SEMAPHORE 
    try :
        if ANTI_DELETE_MEDIA_SEMAPHORE is None :
            ANTI_DELETE_MEDIA_SEMAPHORE =asyncio .Semaphore (1 )
        media_type ,media_label =_message_media_type (message )
        if not media_type or not getattr (message ,"chat",None ):
            return 
        file_size =get_media_file_size (message ,media_type )
        key =(message .chat .id ,message .id )
        item =MESSAGE_TIMELINE_CACHE .setdefault (uid ,{}).get (key )
        if not file_size or file_size >ANTI_DELETE_MAX_MEDIA_MB *1024 *1024 :
            if item is not None :
                item ["media_type"]=media_type 
                item ["media_label"]=f"{media_label } بزرگ‌تر از {ANTI_DELETE_MAX_MEDIA_MB }MB"
            return 
        base_dir =get_antidelete_base_dir (uid )
        prune_antidelete_disk_cache ()
        async with ANTI_DELETE_MEDIA_SEMAPHORE :
            path =await message .download (file_name =base_dir +os .sep )
        if not path :
            return 
        item =MESSAGE_TIMELINE_CACHE .setdefault (uid ,{}).get (key )
        if item is not None :
            old_path =item .get ("media_path")
            if old_path and old_path !=path and os .path .exists (old_path ):
                try :os .remove (old_path )
                except Exception :pass 
            item ["media_path"]=path 
            item ["media_type"]=media_type 
            item ["media_label"]=media_label 
            _trim_timeline_cache (uid )
    except Exception :
        pass 

async def _send_cached_deleted_media (client ,item :dict ,caption :str ):
    path =item .get ("media_path")
    media_type =item .get ("media_type")
    if not path or not os .path .exists (path ):
        return False 
    try :
        if media_type =="photo":
            await client .send_photo ("me",path ,caption =caption [:1024 ])
        elif media_type =="video":
            await client .send_video ("me",path ,caption =caption [:1024 ])
        elif media_type =="animation":
            await client .send_animation ("me",path ,caption =caption [:1024 ])
        elif media_type =="voice":
            await client .send_voice ("me",path ,caption =caption [:1024 ])
        elif media_type =="audio":
            await client .send_audio ("me",path ,caption =caption [:1024 ])
        elif media_type =="sticker":
            await client .send_sticker ("me",path )
            await client .send_message ("me",caption [:4096 ])
        elif media_type =="video_note":
            await client .send_video_note ("me",path )
            await client .send_message ("me",caption [:4096 ])
        else :
            await client .send_document ("me",path ,caption =caption [:1024 ])
        return True 
    except Exception :
        try :
            await client .send_document ("me",path ,caption =caption [:1024 ])
            return True 
        except Exception :
            return False 

async def notify_timeline_event (client ,uid :int ,title :str ,item :dict ,extra :str =""):
    try :
        media_label =item .get ("media_label")
        text =f"{title }\n\nچت: `{item .get ('chat_title',item .get ('chat_id'))}`\nفرستنده: `{item .get ('sender_name','ناشناس')}`\nزمان ثبت: `{item .get ('date','-')}`"
        if media_label :
            text +=f"\nنوع مدیا: `{media_label }`"
        text +=f"\n\nمتن:\n{item .get ('text','')}"
        if extra :
            text +=f"\n\n{extra }"

        if item .get ("media_path"):
            _drop_timeline_cache_item (item )
            item .pop ("media_path",None )
        await client .send_message ("me",text [:4096 ])
    except Exception :
        pass 

async def anti_edit_message_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True )or not ANTI_EDIT_STATUS .get (uid ,False ):
        return 
    if not getattr (message ,"chat",None )or message .chat .type !=ChatType .PRIVATE :
        return 
    key =(message .chat .id ,message .id )
    cache =MESSAGE_TIMELINE_CACHE .setdefault (uid ,{})
    old =cache .get (key )
    new_text =_message_content_text (message )
    if old and old .get ("text")!=new_text :
        await notify_timeline_event (client ,uid ,"✎ ضد ادیت | پیام ویرایش شد",old ,f"متن جدید:\n{new_text }")
    remember_message_for_timeline (uid ,message )

def _classify_raw_ttl_media (media ):
    try :
        if isinstance (media ,types .MessageMediaPhoto ):
            return "photo"
        if isinstance (media ,types .MessageMediaDocument ):
            doc =getattr (media ,"document",None )
            attrs =list (getattr (doc ,"attributes",None )or [])
            has_video =has_audio =is_round =is_voice =is_animated =False
            for a in attrs :
                if isinstance (a ,types .DocumentAttributeVideo ):
                    has_video =True
                    if getattr (a ,"round_message",False ):
                        is_round =True
                elif isinstance (a ,types .DocumentAttributeAudio ):
                    has_audio =True
                    if getattr (a ,"voice",False ):
                        is_voice =True
                elif isinstance (a ,types .DocumentAttributeAnimated ):
                    is_animated =True
            if is_round :
                return "video_note"
            if is_voice :
                return "voice"
            if is_animated :
                return "animation"
            if has_video :
                return "video"
            if has_audio :
                return "voice"
    except Exception :
        pass
    return "document"

def _raw_media_file_address (media ):
    try :
        if isinstance (media ,types .MessageMediaPhoto )and isinstance (media .photo ,types .Photo ):
            photo =media .photo
            biggest =None
            largest =0
            for s in (getattr (photo ,"sizes",None )or []):
                sz =getattr (s ,"size",None )
                if sz and int (sz )>largest :
                    largest =int (sz )
                    biggest =s
            if biggest is None :
                return None
            return (types .InputPhotoFileLocation (
                id =photo .id ,
                access_hash =photo .access_hash ,
                file_reference =photo .file_reference or b"",
                thumb_size =getattr (biggest ,"type","y")or "y"
            ),largest ,int (photo .dc_id ))
        if isinstance (media ,types .MessageMediaDocument )and isinstance (media .document ,types .Document ):
            doc =media .document
            return (types .InputDocumentFileLocation (
                id =doc .id ,
                access_hash =doc .access_hash ,
                file_reference =doc .file_reference or b"",
                thumb_size =""
            ),int (doc .size ),int (doc .dc_id ))
    except Exception :
        pass
    return None

async def _raw_download_media (client ,media ,dest_path ):
    addr =_raw_media_file_address (media )
    if not addr :
        return None
    location ,file_size ,dc_id =addr
    limit =512 *1024
    offset =0
    parts_guard =0
    with open (dest_path ,"wb")as f :
        while True :
            rq =functions .upload .GetFile (location =location ,offset =offset ,limit =limit )
            try :
                r =await client .invoke (rq ,dc_id =dc_id )
            except TypeError :
                r =await client .invoke (rq )
            chunk =getattr (r ,"bytes",None )
            if not isinstance (chunk ,(bytes ,bytearray ))or not chunk :
                break
            f .write (chunk )
            offset +=len (chunk )
            parts_guard +=1
            if len (chunk )<limit or (file_size and offset >=file_size )or parts_guard >1200 :
                break
    if not file_size :
        file_size =offset
    if offset <=0 :
        try :os .remove (dest_path )
        except Exception :pass
        return None
    return dest_path

async def _refetch_raw_ttl_media (client ,chat_id ,mid ):
    try :
        if int (chat_id )>0 :
            msgs =await client .invoke (functions .messages .GetMessages (id =[types .InputMessageID (id =int (mid ))]))
        else :
            peer =await client .resolve_peer (chat_id )
            cid =getattr (peer ,"channel_id",None )
            acc =getattr (peer ,"access_hash",None )
            if cid is None :
                return None
            msgs =await client .invoke (functions .channels .GetMessages (
                channel =types .InputChannel (channel_id =int (cid ),access_hash =int (acc )),
                id =[types .InputMessageID (id =int (mid ))]
            ))
        for m in (getattr (msgs ,"messages",[])or []):
            media =getattr (m ,"media",None )
            if media is not None and getattr (media ,"ttl_seconds",None ):
                return media
    except Exception :
        pass
    return None

def _special_download_filepath (dest_path ,media =None ,kind =None ):
    ext_map ={"photo":".jpg","video":".mp4","video_note":".mp4","voice":".ogg","animation":".mp4"}
    if kind is None and media is not None :
        kind =_classify_raw_ttl_media (media )
    ext =ext_map .get (kind or "",".jpg")
    if dest_path .endswith (os .sep )or os .path .isdir (dest_path ):
        return os .path .join (dest_path ,f"special_{uuid .uuid4 ().hex [:10 ]}{ext }")
    return dest_path

async def download_special_media (client ,message ,dest_path ):
    if getattr (message ,"media",None ):
        try :
            p =await message .download (file_name =dest_path )
            if p and os .path .exists (p ):
                return p
        except Exception :
            pass
    raw_media =None
    kind_hint =None
    try :
        if getattr (message ,"chat",None )is not None :
            hint =RAW_TTL_MEDIA_HINTS .get ((message .chat .id ,message .id ))
            if isinstance (hint ,dict ):
                raw_media =hint .get ("media")
                kind_hint =hint .get ("kind")
    except Exception :
        raw_media =None
    if raw_media is not None :
        try :
            p =await _raw_download_media (client ,raw_media ,_special_download_filepath (dest_path ,raw_media ,kind_hint ))
            if p :
                return p
        except Exception :
            pass
    try :
        if getattr (message ,"chat",None )is not None :
            fresh =await _refetch_raw_ttl_media (client ,message .chat .id ,message .id )
            if fresh is not None :
                return await _raw_download_media (client ,fresh ,_special_download_filepath (dest_path ,fresh ,None ))
    except Exception :
        pass
    return None

async def ttl_media_raw_hint_handler (client ,update ,users ,chats ):
    try :
        raw_msg =None
        if isinstance (update ,(types .UpdateNewMessage ,types .UpdateNewChannelMessage )):
            raw_msg =getattr (update ,"message",None )
        if raw_msg is None :
            return

        media =getattr (raw_msg ,"media",None )
        if media is None :
            return

        ttl =getattr (media ,"ttl_seconds",None )
        if not ttl :
            return

        kind =_classify_raw_ttl_media (media )
        
        view_once =int (ttl )>=2147483647

        peer =getattr (raw_msg ,"peer_id",None )
        if isinstance (peer ,types .PeerUser ):
            chat_id =peer .user_id
        elif isinstance (peer ,types .PeerChat ):
            chat_id =-peer .chat_id
        elif isinstance (peer ,types .PeerChannel ):
            chat_id =int (f"-100{peer .channel_id }")
        else :
            return

        mid =getattr (raw_msg ,"id",None )
        if not mid :
            return

        RAW_TTL_MEDIA_HINTS [(chat_id ,mid )]={"ttl":int (ttl ),"kind":kind ,"view_once":view_once ,"ts":time .time ()}
        if len (RAW_TTL_MEDIA_HINTS )>RAW_TTL_MEDIA_HINTS_LIMIT :
            for k in list (RAW_TTL_MEDIA_HINTS .keys ())[:len (RAW_TTL_MEDIA_HINTS )-RAW_TTL_MEDIA_HINTS_LIMIT ]:
                RAW_TTL_MEDIA_HINTS .pop (k ,None )
    except Exception :
        pass

async def anti_delete_raw_update_handler (client ,update ,users ,chats ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):
        return 
    try :
        cache =MESSAGE_TIMELINE_CACHE .setdefault (uid ,{})

        if isinstance (update ,types .UpdateEditMessage ):
            if not ANTI_EDIT_STATUS .get (uid ,False ):
                return 
            raw_msg =getattr (update ,"message",None )
            peer =getattr (raw_msg ,"peer_id",None )
            if not isinstance (peer ,types .PeerUser ):
                return 
            chat_id =peer .user_id 
            mid =getattr (raw_msg ,"id",None )
            if not mid :
                return 
            new_text =(getattr (raw_msg ,"message",None )or "").strip ()or "[پیام بدون متن]"
            key =(chat_id ,mid )
            old =cache .get (key )
            if old and old .get ("text")!=new_text :
                await notify_timeline_event (client ,uid ,"✎ ضد ادیت | پیام ویرایش شد",old ,f"متن جدید:\n{new_text }")
                old ["text"]=new_text 
                old ["date"]=datetime .now (TEHRAN_TIMEZONE ).strftime ("%Y/%m/%d %H:%M:%S")
                cache [key ]=old 
            return 

        if not ANTI_DELETE_STATUS .get (uid ,False ):
            return 

        deleted_ids =[]
        chat_id_hint =None 
        if isinstance (update ,types .UpdateDeleteMessages ):
            deleted_ids =list (getattr (update ,"messages",[])or [])
        elif isinstance (update ,types .UpdateDeleteChannelMessages ):

            return 
        else :
            return 

        for mid in deleted_ids :

            bucket =MESSAGE_ID_INDEX .get (mid )
            if not bucket :
                continue 
            for entry_key in list (bucket ):
                try :
                    e_uid ,chat_id ,e_mid =entry_key 
                    if int (e_uid )!=int (uid ):
                        continue 
                    cache =MESSAGE_TIMELINE_CACHE .get (uid )
                    if not cache :
                        continue 

                    cache_key =(chat_id ,e_mid )
                    item =cache .get (cache_key )
                    if not item :
                        bucket .discard (entry_key )
                        continue 
                    await notify_timeline_event (client ,uid ,"☒ ضد دیلیت | پیام حذف شد",item )
                    cache .pop (cache_key ,None )
                    bucket .discard (entry_key )
                except Exception :
                    pass 
            try :
                if not bucket :
                    MESSAGE_ID_INDEX .pop (mid ,None )
            except Exception :
                pass 
    except Exception :
        pass 

def _crypto_master_key (uid :int )->bytes :
    data =data_manager .get_user_data (uid )
    raw_session =_db_decrypt (data .get ("session_string",""))
    secret ="|".join ([str (uid ),raw_session ,str (data .get ("phone","")),str (API_HASH ),str (BOT_TOKEN )])
    return hashlib .sha256 (secret .encode ("utf-8")).digest ()

def _crypto_keystream (key :bytes ,salt :bytes ,nonce :bytes ,size :int )->bytes :
    out =bytearray ()
    counter =0 
    while len (out )<size :
        counter +=1 
        out .extend (hmac .new (key ,salt +nonce +counter .to_bytes (4 ,"big"),hashlib .sha256 ).digest ())
    return bytes (out [:size ])

def _xor_bytes (a :bytes ,b :bytes )->bytes :
    if not a :
        return b""
    return (int .from_bytes (a ,"big")^int .from_bytes (b ,"big")).to_bytes (len (a ),"big")

def dark_encrypt_text (uid :int ,plain :str )->str :
    key =_crypto_master_key (uid )
    salt =secrets .token_bytes (16 )
    nonce =secrets .token_bytes (16 )
    payload =zlib .compress (plain .encode ("utf-8"),level =9 )
    stream =_crypto_keystream (key ,salt ,nonce ,len (payload ))
    cipher =_xor_bytes (payload ,stream )
    tag =hmac .new (key ,b"DSX1"+salt +nonce +cipher ,hashlib .sha256 ).digest ()[:16 ]
    return "DSX1:"+base64 .urlsafe_b64encode (salt +nonce +cipher +tag ).decode ().rstrip ("=")

def dark_decrypt_text (uid :int ,token :str )->str :
    token =(token or "").strip ()
    if token .startswith ("`")and token .endswith ("`"):
        token =token .strip ("`").strip ()
    if token .startswith ("DSX1:"):
        token =token [5 :].strip ()

    pad =-len (token )%4 
    if pad :
        token =token +("="*pad )
    try :
        raw =base64 .urlsafe_b64decode (token )
    except Exception :
        raise ValueError ("bad token")
    if len (raw )<49 :
        raise ValueError ("bad token")
    salt ,nonce ,cipher ,tag =raw [:16 ],raw [16 :32 ],raw [32 :-16 ],raw [-16 :]
    key =_crypto_master_key (uid )
    good =hmac .new (key ,b"DSX1"+salt +nonce +cipher ,hashlib .sha256 ).digest ()[:16 ]
    if not hmac .compare_digest (tag ,good ):
        raise ValueError ("wrong key")
    stream =_crypto_keystream (key ,salt ,nonce ,len (cipher ))
    payload =_xor_bytes (cipher ,stream )
    try :
        return zlib .decompress (payload ).decode ("utf-8")
    except Exception :
        raise ValueError ("bad token")

async def crypto_text_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )or ""
    cmd =cmd .strip ()
    try :
        dec_match =re .match (r"^رمز\s*گشایی(?:\s+|$)(.*)",cmd ,flags =re .I |re .S )
        if dec_match :
            token =(dec_match .group (1 )or "").strip ()
            if not token and message .reply_to_message :
                token =message .reply_to_message .text or message .reply_to_message .caption or ""
            if not token :
                return await _safe_edit_or_reply (message ,"**برای رمزگشایی روی متن رمز ریپلای کن و بزن:**\n`رمزگشایی`")
            token_match =re .search (r"DSX1:[A-Za-z0-9_\-]+",token )
            if token_match :
                token =token_match .group (0 )
            plain =dark_decrypt_text (uid ,token )
            return await _safe_edit_or_reply (message ,f"**متن باز شده:**\n{plain [:3900 ]}")

        enc_match =re .match (r"^رمز(?:\s+|$)(.*)",cmd ,flags =re .I |re .S )
        if enc_match :
            plain =(enc_match .group (1 )or "").strip ()
            if not plain and message .reply_to_message :
                plain =message .reply_to_message .text or message .reply_to_message .caption or ""
            if not plain :
                return await _safe_edit_or_reply (message ,"**فرمت صحیح:**\n`رمز سلام خوبی چه خبر`\nیا روی متن ریپلای کن و بزن `رمز`")
            token =dark_encrypt_text (uid ,plain )
            if len (token )>3900 :
                return await _safe_edit_or_reply (message ,"**متن خیلی طولانیه؛ خروجی رمز از محدودیت تلگرام بیشتر میشه.**")
            return await _safe_edit_or_reply (message ,f"**متن رمز شده:**\n`{token }`")
    except ValueError :
        return await _safe_edit_or_reply (message ,"**رمزگشایی انجام نشد.**\nاین متن یا خراب است یا با کلید سلف تو ساخته نشده.")
    except Exception as e :
        return await _safe_edit_or_reply (message ,f"**خطا:**\n`{str (e )[:120 ]}`")

async def anti_timeline_early_recorder (client ,message ):
    try :
        if not message .from_user or not getattr (message ,"chat",None ):
            return 
        uid =client .me .id 
        if not SELF_ACTIVE_STATUS .get (uid ,True ):
            return 
        if message .chat .type !=ChatType .PRIVATE :
            return 
        if ANTI_DELETE_STATUS .get (uid ,False )or ANTI_EDIT_STATUS .get (uid ,False ):
            remember_message_for_timeline (uid ,message )
    except Exception :
        pass 

async def incoming_message_manager (client ,message ):
    if not message .from_user :
        return 
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if message .chat and message .chat .type ==ChatType .PRIVATE :
        if ANTI_DELETE_STATUS .get (uid ,False )or ANTI_EDIT_STATUS .get (uid ,False ):
            remember_message_for_timeline (uid ,message )

    sender_id =message .from_user .id 

    if sender_id ==ROOT_ADMIN :
        return 

    if message .chat and message .chat .type ==ChatType .PRIVATE and FILTER_WORDS_ACTIVE .get (uid ,False ):
        content =normalize_filter_text ((message .text or message .caption or ""))
        if content :
            for fw_norm in FILTER_WORDS_NORMALIZED .get (uid ,[]):
                if fw_norm and fw_norm in content :
                    try :
                        await message .delete ()
                    except Exception :
                        pass 
                    return 

    if sender_id !=uid :
        target_emoji =AUTO_REACTION_TARGETS .get (uid ,{}).get (str (sender_id ))
        if target_emoji :
            try :
                await client .send_reaction (message .chat .id ,message .id ,target_emoji )
            except Exception :

                try :
                    targets =AUTO_REACTION_TARGETS .get (uid ,{})
                    if str (sender_id )in targets :
                        targets .pop (str (sender_id ),None )
                        data_manager .update_user_data (uid ,{"reactions":targets })
                except Exception :
                    pass 

    if (sender_id ,message .chat .id )in MUTED_USERS .get (uid ,set ()):
        try :
            await message .delete ()
        except Exception :
            pass 

def _load_target_reply_texts (uid ,restore_defaults =False ):
    data =data_manager .get_user_data (uid )
    if restore_defaults :
        patch ={}
        for key ,defaults in (("enemy_replies",ENEMY_REPLIES_DEFAULT ),("friend_replies",FRIEND_REPLIES_DEFAULT ),("crash_replies",CRASH_REPLIES_DEFAULT )):
            saved =data .get (key )or []
            baseline =set (defaults )
            
            complete =list (defaults )+[text for text in saved if text not in baseline ]
            if saved !=complete :patch [key ]=complete 
        if patch :
            data_manager .update_user_data (uid ,patch )
            _commit_and_broadcast_shards ("restore-target-reply-defaults")
            data =data_manager .get_user_data (uid )
    ENEMY_REPLIES [uid ]=list (data .get ("enemy_replies")or ENEMY_REPLIES_DEFAULT )
    FRIEND_REPLIES [uid ]=list (data .get ("friend_replies")or FRIEND_REPLIES_DEFAULT )
    CRASH_REPLIES [uid ]=list (data .get ("crash_replies")or CRASH_REPLIES_DEFAULT )
    return {"دشمن":ENEMY_REPLIES [uid ],"دوست":FRIEND_REPLIES [uid ],"کراش":CRASH_REPLIES [uid ]}

def _target_reply_page (title ,replies ,page =1 ):
    pages ,lines ,size =[],[],0 
    for number ,text in enumerate (replies ,1 ):
        parts =[text ]if len (html .escape (text ).encode ("utf-16-le"))//2 <=3000 else [text [offset :offset +500 ]for offset in range (0 ,len (text ),500 )]
        for part_index ,part in enumerate (parts ):
            label =f"{number }."if part_index ==0 else f"{number } (ادامه)."
            line =f"{label } <code>{html .escape (part )}</code>"
            width =len (line .encode ("utf-16-le"))//2 +1 
            if lines and size +width >3300 :
                pages .append ("\n".join (lines ))
                lines ,size =[],0 
            lines .append (line )
            size +=width 
    if lines :pages .append ("\n".join (lines ))
    if not pages :pages =["متنی ثبت نشده است."]
    page =max (1 ,min (int (page ),len (pages )))
    text =f"<b>متن‌های پاسخ {title }</b>\nتعداد: {len (replies )} | صفحهٔ {page } از {len (pages )}\n\n"+pages [page -1 ]
    if page <len (pages ):text +=f"\n\nصفحهٔ بعد: <code>لیست {title } {page +1 }</code>"
    return text 

async def list_management_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    async def sedit (text ,**kwargs ):
        try :
            await message .edit_text (text ,**kwargs )
        except (MessageIdInvalid ,MessageNotModified ,NotAcceptable ):
            pass 
        except FloodWait as fw :
            await asyncio .sleep (min (fw .value ,5 ))
        except Exception :
            pass 

    cmd =get_cmd (uid ,message .text )
    if not cmd :return 
    reply_texts =_load_target_reply_texts (uid )
    display =re .fullmatch (r"لیست(?: متن)? (دشمن|دوست|کراش)(?:\s+(\d+))?",cmd )
    if display :
        title ,page =display .groups ()
        await sedit (_target_reply_page (title ,reply_texts [title ],int (page or 1 )),parse_mode =ParseMode .HTML )
        return 
    if cmd in ["تنظیم دشمن","حذف دشمن","تنظیم دوست","حذف دوست","تنظیم کراش","حذف کراش"]:
        if not message .reply_to_message or not message .reply_to_message .from_user :
            await sedit ("**روی پیام کاربر مورد نظر ریپلای کنید.**")
            return 
        tid =int (message .reply_to_message .from_user .id )

        if "دشمن"in cmd :
            lst =ENEMY_LIST .setdefault (uid ,set ())
            title ,active_key ="دشمن","enemy_active"
            active_store =ENEMY_ACTIVE 
        elif "دوست"in cmd :
            lst =FRIEND_LIST .setdefault (uid ,set ())
            title ,active_key ="دوست","friend_active"
            active_store =FRIEND_ACTIVE 
        else :
            lst =CRASH_LIST .setdefault (uid ,set ())
            title ,active_key ="کراش","crash_active"
            active_store =CRASH_ACTIVE 

        if "تنظیم"in cmd :
            current_key ,current_title =get_target_category (uid ,tid )
            if tid in lst :
                await sedit (f"**این کاربر از قبل در لیست {title } ثبت شده است.**")
                return 
            if current_key :
                await sedit (f"**شما یک تارگت را از قبل فعال کردید: {current_title }**")
                return 
            lst .add (tid )

            msg =f"**کاربر مورد نظر به لیست {title } اضافه شد.**"
        else :
            if tid not in lst :
                await sedit (f"**این کاربر در لیست {title } وجود ندارد.**")
                return 
            lst .remove (tid )
            msg =f"**کاربر مورد نظر از لیست {title } حذف شد.**"

        data_manager .update_user_data (uid ,{"enemy_list":list (ENEMY_LIST .get (uid ,[])),"friend_list":list (FRIEND_LIST .get (uid ,[])),"crash_list":list (CRASH_LIST .get (uid ,[])),"settings":{active_key :active_store .get (uid ,False )}})
        await sedit (msg )
        return 

    if cmd in ["لیست افراد دشمن","لیست افراد دوست","لیست افراد کراش"]:
        if "دشمن"in cmd :lst ,title ,t_cmd =ENEMY_LIST .get (uid ,set ()),"دشمن","دشمن"
        elif "دوست"in cmd :lst ,title ,t_cmd =FRIEND_LIST .get (uid ,set ()),"دوست","دوست"
        else :lst ,title ,t_cmd =CRASH_LIST .get (uid ,set ()),"کراش","کراش"

        if not lst :return await sedit (f"**لیست {title } خالی است.**\nبرای افزودن کاربر، روی پیام او ریپلای کنید و دستور `تنظیم {t_cmd }` را بفرستید.")
        await sedit (f"**لیست {title }:**\n"+"\n".join ([f"- `{x }`"for x in lst ])[:4000 ])
        return 

    if cmd in ["پاکسازی لیست دشمن","پاکسازی لیست دوست","پاکسازی لیست کراش"]:
        if "دشمن"in cmd :ENEMY_LIST [uid ]=set ()
        elif "دوست"in cmd :FRIEND_LIST [uid ]=set ()
        else :CRASH_LIST [uid ]=set ()
        data_manager .update_user_data (uid ,{"enemy_list":list (ENEMY_LIST .get (uid ,[])),"friend_list":list (FRIEND_LIST .get (uid ,[])),"crash_list":list (CRASH_LIST .get (uid ,[]))})
        await sedit ("**لیست مورد نظر پاکسازی شد.**")
        return 

    m_set =re .match (r"^تنظیم متن (دشمن|دوست|کراش)(?:\s+)(.*)",cmd ,re .DOTALL )
    if m_set :
        typ ,txt =m_set .groups ()
        if typ =="دشمن":
            if not ENEMY_REPLIES .get (uid ):ENEMY_REPLIES [uid ]=ENEMY_REPLIES_DEFAULT .copy ()
            reps =ENEMY_REPLIES [uid ]
        elif typ =="دوست":
            if not FRIEND_REPLIES .get (uid ):FRIEND_REPLIES [uid ]=FRIEND_REPLIES_DEFAULT .copy ()
            reps =FRIEND_REPLIES [uid ]
        else :
            if not CRASH_REPLIES .get (uid ):CRASH_REPLIES [uid ]=CRASH_REPLIES_DEFAULT .copy ()
            reps =CRASH_REPLIES [uid ]

        reps .append (txt .strip ())
        data_manager .update_user_data (uid ,{"enemy_replies":ENEMY_REPLIES [uid ],"friend_replies":FRIEND_REPLIES [uid ],"crash_replies":CRASH_REPLIES [uid ]})
        _commit_and_broadcast_shards ("target-reply-texts")
        await sedit (f"**متن به لیست {typ } اضافه شد.**")
        return 

    m_del =re .match (r"^حذف متن (دشمن|دوست|کراش)(?: (\d+))?$",cmd )
    if m_del :
        typ ,idx_str =m_del .groups ()
        if typ =="دشمن":reps =ENEMY_REPLIES .get (uid ,[])
        elif typ =="دوست":reps =FRIEND_REPLIES .get (uid ,[])
        else :reps =CRASH_REPLIES .get (uid ,[])

        defaults ={"دشمن":ENEMY_REPLIES_DEFAULT ,"دوست":FRIEND_REPLIES_DEFAULT ,"کراش":CRASH_REPLIES_DEFAULT }[typ ]
        if idx_str :
            idx =int (idx_str )-1 
            if 0 <=idx <len (reps ):
                reps .pop (idx )
                notice ="**متن مورد نظر حذف شد.**"
            else :
                return await sedit ("**شماره وارد شده معتبر نیست.**")
        else :
            reps .clear ()
            notice ="**متن‌های اختصاصی پاک شدند.**"
        if not reps :
            reps .extend (defaults )
            notice +="\nمتن‌های پیش‌فرض فایل فعال شدند."
        data_manager .update_user_data (uid ,{"enemy_replies":ENEMY_REPLIES [uid ],"friend_replies":FRIEND_REPLIES [uid ],"crash_replies":CRASH_REPLIES [uid ]})
        _commit_and_broadcast_shards ("target-reply-texts")
        await sedit (notice )

EXTRA_FUN_NOBLE =[
"I love you ❤️","تو همه چیز منی 💖","عشقم تویی 💕",
"دلم برات تنگ شده 🥺","تو بهترینی 🌹","همیشه کنارتم ❤️",
]

EXTRA_EMOJI_CYCLES ={
"ماه":list ("🌗🌘🌑🌒🌓🌔🌕🌖"),
"moon2":list ("🌗🌘🌑🌒🌓🌔🌕🌖"),
"ساعت2":list ("🕙🕘⑧⑦⑥⑤④③②①🕛".encode ("utf-8","ignore").decode ("utf-8")),
"clock2":list ("🕙🕘⑧⑦⑥⑤④③②①🕛".encode ("utf-8","ignore").decode ("utf-8")),
"رعد":list ("☀️🌤️⛅🌥️☁️🌩️🌧️⛈️⚡🌩️🌧️🌦️🌥️⛅🌤️☀️"),
"thunder":list ("☀️🌤️⛅🌥️☁️🌩️🌧️⛈️⚡🌩️🌧️🌦️🌥️⛅🌤️☀️"),
"زمین":list ("🌏🌍🌎🌎🌍🌏🌍🌎"),
"earth":list ("🌏🌍🌎🌎🌍🌏🌍🌎"),
"قلب رنگی":list ("❤️🧡💛💚💙💜🖤"),
"heart2":list ("❤️🧡💛💚💙💜🖤"),
}

async def extra_fun_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    raw_cmd =get_cmd (uid ,message .text )
    if not raw_cmd :
        raw_cmd =getattr (message ,"_darkself_fun_cmd",None )
    if not raw_cmd :
        return 
    cmd =raw_cmd .lower ()

    async def safe_edit (txt ,delay =0.12 ):
        try :

            await safe_edit_message (message ,txt ,parse_mode =None )
            await asyncio .sleep (delay )
        except FloodWait as fw :
            await asyncio .sleep (fw .value +1 )
        except Exception :
            pass 

    async def play (frames ,delay =0.12 ,final =None ):
        for frame in frames :
            await safe_edit (frame ,delay )
        if final is not None :
            await safe_edit (final ,0 )

    def bar (percent ,size =14 ,full ="▰",empty ="▱"):
        filled =max (0 ,min (size ,round (percent *size /100 )))
        return full *filled +empty *(size -filled )

    if cmd in ("ماتریکس","matrix"):

        matrix_chars =list ("01ABCDEFGHIJKLMNOPQRSTUVWXYZアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン")
        frames =[]
        width =18 
        height =8 
        for step in range (22 ):
            rows =[]
            for y in range (height ):
                row =""
                for x in range (width ):
                    if (x +y +step )%5 ==0 :
                        row +=random .choice ("01")
                    elif random .random ()<0.72 :
                        row +=random .choice (matrix_chars )
                    else :
                        row +=" "
                rows .append (row )
            percent =min (100 ,step *5 )
            frames .append (
            "╔══════ MATRIX RAIN ══════╗\n"
            +"\n".join (rows )+
            f"\n╠══════ {bar (percent )} {percent :03d}% ══════╣\n"
            "╚════════════════════════╝"
            )
        await play (
        frames ,
        0.08 ,
        "╔══════ MATRIX RAIN ══════╗\n"
        "Wake up, Neo...\n"
        "The Matrix has you.\n"
        "Follow the white rabbit.\n"
        "╠══════ ▰▰▰▰▰▰▰▰▰▰▰▰▰▰ 100% ══════╣\n"
        "╚══════ ACCESS GRANTED ══════╝"
        )
        return 

    if cmd =="لاو":

        hearts =['🤍','🖤','💜','💙','💚','💛','🧡','❤️','💖']
        random .shuffle (hearts )
        for emoji in hearts :
            await safe_edit (emoji ,0.4 )
        return 

async def fun_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    raw_cmd =get_cmd (uid ,message .text )
    if not raw_cmd :
        raw_cmd =getattr (message ,"_darkself_fun_cmd",None )
    if not raw_cmd :
        return 
    cmd =raw_cmd .lower ()

    if cmd in ['قلب','heart']:
        fill_symbol ="❦"
        empty_symbol ="♡"
        side_symbols =["ღ","❥","♥","❣","❧","✦"]
        total_slots =10 
        try :
            for percent in range (0 ,101 ,5 ):
                filled =max (1 ,round (percent /10 ))if percent else 0 
                empty =total_slots -filled 
                love_bar =(fill_symbol *filled )+(empty_symbol *empty )
                left =side_symbols [(percent //10 )%len (side_symbols )]
                right =side_symbols [-((percent //10 )%len (side_symbols ))-1 ]
                await safe_edit_message (message ,
                f"╔════════════════════╗\n"
                f"      𝓛𝓞𝓥𝓔 𝓛𝓞𝓐𝓓𝓘𝓝𝓖\n"
                f"╚════════════════════╝\n\n"
                f"{left } {love_bar } {right }\n\n"
                f"        {percent }%"
                )
                await asyncio .sleep (0.12 )
            await safe_edit_message (message ,
            "╔════════════════════╗\n"
            "      𝓛𝓞𝓥𝓔 𝓒𝓞𝓜𝓟𝓛𝓔𝓣𝓔\n"
            "╚════════════════════╝\n\n"
            "ღ ❦ ❥ ♥ 𝓘 𝓛𝓞𝓥𝓔 𝓨𝓞𝓤 ♥ ❥ ❦ ღ"
            )
        except FloodWait as fw :
            await asyncio .sleep (fw .value +1 )
        except Exception :
            pass 
        return 

    if cmd .startswith ('fun ')or cmd .startswith ('فان '):
        parts =cmd .split (' ',1 )
        if len (parts )<2 :
            return 
        sub =parts [1 ].strip ().lower ()
        alias ={
        "matrix":"ماتریکس","ماتریکس":"ماتریکس",
        }
        mapped =alias .get (sub )
        if mapped :
            try :
                setattr (message ,"_darkself_fun_cmd",mapped )
                await extra_fun_controller (client ,message )
            finally :
                try :delattr (message ,"_darkself_fun_cmd")
                except Exception :pass 
        return 

GAME_DICE_EMOJIS ={
"تاس":"🎲",
"دارت":"🎯",
"فوتبال":"⚽",
"بولینگ":"🎳",
"بسکتبال":"🏀",
}

async def game_cheat_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )
    if not cmd :
        return 
    cmd =re .sub (r"\s+"," ",cmd .strip ())
    m =re .match (r"^تاس(?:\s+([1-6]))?$",cmd )
    if m :
        emoji ,target_value ="🎲",int (m .group (1 )or 6 )
    elif cmd in ("دارت","بولینگ","بسکتبال","فوتبال"):
        emoji =GAME_DICE_EMOJIS [cmd ]
        target_value =6 if cmd in ("دارت","بولینگ")else 5 
    else :
        return 

    chat_id =message .chat .id 
    reply_id =getattr (message ,"reply_to_message_id",None )
    if not reply_id :
        reply_id =getattr (getattr (message ,"reply_to_message",None ),"id",None )
    thread_id =getattr (message ,"message_thread_id",None )or getattr (message ,"reply_to_top_message_id",None )
    effective_reply_id =reply_id or thread_id 

    lock =getattr (client ,"_darkself_game_roll_lock",None )
    if lock is None :
        lock =asyncio .Lock ()
        setattr (client ,"_darkself_game_roll_lock",lock )
    if lock .locked ():
        logger .info ("Game already running for %s; duplicate ignored",uid )
        return 

    async with lock :
        pending_ids =set ()
        deadline =time .monotonic ()+60 
        destination_peer =None 

        async def delete_temporary (mid ):
            for attempt in range (3 ):
                try :
                    await client .delete_messages (chat_id ,mid ,revoke =True )
                    ids =[types .InputMessageID (id =mid )]
                    if isinstance (destination_peer ,types .InputPeerChannel ):
                        lookup =functions .channels .GetMessages (
                        channel =types .InputChannel (
                        channel_id =destination_peer .channel_id ,access_hash =destination_peer .access_hash 
                        ),id =ids 
                        )
                    else :
                        lookup =functions .messages .GetMessages (id =ids )
                    checked =await client .invoke (lookup )
                    still_exists =any (
                    getattr (item ,"id",None )==mid and not isinstance (item ,types .MessageEmpty )
                    for item in getattr (checked ,"messages",())
                    )
                    if not still_exists :
                        pending_ids .discard (mid )
                        return True 
                    if attempt <2 :await asyncio .sleep (0.5 )
                except FloodWait as fw :
                    logger .warning ("Game cleanup rate-limited for %s: %s seconds",uid ,fw .value )
                    return False 
                except Exception as exc :
                    logger .warning ("Game cleanup failed for %s/%s: %s",uid ,mid ,type (exc ).__name__ )
                    if attempt <2 :await asyncio .sleep (0.5 )
            return False 

        try :
            destination_peer =await client .resolve_peer (chat_id )
            
            if not await delete_temporary (message .id ):
                logger .warning ("Game not started for %s in %s: command deletion not confirmed",uid ,chat_id )
                return 
            for attempt in range (30 ):
                if time .monotonic ()>=deadline :
                    logger .warning ("Game time limit reached for %s",uid )
                    break 
                
                result =await client .send_dice (
                chat_id ,emoji =emoji ,reply_to_message_id =effective_reply_id ,
                disable_notification =True 
                )
                mid =getattr (result ,"id",None )
                if not mid :
                    raise RuntimeError ("GAME_ROLL_MESSAGE_MISSING")
                pending_ids .add (mid )
                value =getattr (getattr (result ,"dice",None ),"value",None )
                if value is None :
                    raise RuntimeError ("GAME_ROLL_VALUE_MISSING")
                has_forward =any (getattr (result ,key ,None )for key in (
                "forward_date","forward_from","forward_from_chat","forward_sender_name","forward_origin"
                ))
                if has_forward :
                    raise RuntimeError ("GAME_UNEXPECTED_FORWARD_HEADER")
                if reply_id and getattr (result ,"reply_to_message_id",None )!=reply_id :
                    raise RuntimeError ("GAME_REPLY_NOT_PRESERVED")
                if value ==target_value :
                    pending_ids .discard (mid )
                    logger .info ("Game delivered for %s: %s, value=%s, attempts=%s, reply=%s",uid ,cmd ,value ,attempt +1 ,bool (reply_id ))
                    return 
                if not await delete_temporary (mid ):
                    
                    break 
                await asyncio .sleep (0.8 )
            else :
                logger .warning ("Game attempt limit reached for %s",uid )
        except asyncio .CancelledError :
            raise 
        except FloodWait as fw :
            logger .warning ("Game stopped by rate limit for %s: %s seconds",uid ,fw .value )
        except Exception as exc :
            logger .warning ("Native game failed for %s (client %s): %s",uid ,getattr (sys .modules .get ("pyrogram"),"__version__","unknown"),type (exc ).__name__ )
        finally :
            for mid in tuple (pending_ids ):
                await delete_temporary (mid )
            if pending_ids :
                logger .warning ("Game cleanup incomplete for %s in %s; message IDs: %s",uid ,chat_id ,sorted (pending_ids ))

async def session_export_controller (client ,message ):
    owner =getattr (client ,"me",None )
    sender =getattr (message ,"from_user",None )
    if not owner or not sender or sender .id !=owner .id :
        return 
    if getattr (owner ,"is_bot",False )or getattr (message ,"via_bot",None ):
        return 
    if getattr (message ,"forward_date",None )or getattr (message ,"forward_origin",None ):
        return 
    if get_cmd (owner .id ,getattr (message ,"text",None ))!="سشن":
        return 

    lock =getattr (client ,"_darkself_session_export_lock",None )
    if lock is None :
        lock =asyncio .Lock ()
        setattr (client ,"_darkself_session_export_lock",lock )
    if lock .locked ():
        return 
    async with lock :
        exported_value =None 
        payload =None 
        try :
            
            exported_value =await asyncio .wait_for (client .export_session_string (),timeout =15.0 )
            if not isinstance (exported_value ,str )or not exported_value .strip ():
                logger .warning ("Own-session export returned an empty value")
                return 
            payload =(
            "<b>سشن حساب شما</b>\n\n"
            f"<code>{html .escape (exported_value )}</code>\n\n"
            "<b>محرمانه</b>\n"
            "این رشته دسترسی به حساب شما را فراهم می‌کند. آن را برای هیچ‌کس، حتی پشتیبانی، ارسال نکنید.\n"
            "پس از انتقال به محل امن، این پیام را حذف کنید."
            )
            
            await client .send_message (
            "me",payload ,parse_mode =ParseMode .HTML ,disable_notification =True 
            )
            try :
                await message .delete ()
            except Exception :
                pass 
        except asyncio .CancelledError :
            raise 
        except Exception as exc :
            
            logger .warning ("Own-session export failed: %s",type (exc ).__name__ )
        finally :
            exported_value =None 
            payload =None 

async def id_command_handler (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    if not getattr (message ,"reply_to_message",None ):
        await ensure_reply_message (client ,message )

    target =message .reply_to_message .from_user if message .reply_to_message else message .from_user 
    if not target :
        return 

    first_name =target .first_name or ""
    last_name =target .last_name or ""
    full_name =f"{first_name } {last_name }".strip ()or "ناشناس"
    user_id =target .id 
    username =f"@{target .username }"if target .username else "ندارد"

    text =(
    f"👤 **مشخصات کاربر:**\n\n"
    f"🏷 **نام:** {full_name }\n"
    f"🔢 **آیدی عددی:** `{user_id }`\n"
    f"🆔 **آیدی حروفی:** {username }"
    )
    await safe_edit_message (message ,text )

async def safe_edit_message (message ,text ,**kwargs ):
    try :
        return await message .edit_text (text ,**kwargs )
    except (MessageIdInvalid ,MessageNotModified ,NotAcceptable ):
        return None 
    except FloodWait as fw :
        await asyncio .sleep (min (fw .value ,10 ))
        return None 
    except Exception :
        return None 

async def _safe_edit_or_reply (message ,text ):
    try :
        return await message .edit_text (text )
    except (MessageIdInvalid ,MessageNotModified ,NotAcceptable ):
        try :
            return await message .reply_text (text )
        except Exception :
            pass 
    except FloodWait as fw :
        await asyncio .sleep (min (fw .value ,10 ))
    except Exception :
        try :
            return await message .reply_text (text )
        except Exception :
            pass 

def build_action_panel_markup (owner_uid :int ,chat_id :int ,target_id :int ):
    def on_list (store ):
        return "◉"if target_id in store .get (owner_uid ,set ())else "○"
    key =(target_id ,chat_id )
    mute_on ="◉"if key in MUTED_USERS .get (owner_uid ,set ())else "○"
    until =MUTED_UNTIL .get (owner_uid ,{}).get (key )
    mute_label =f"☒ سکوت {mute_on }"
    if until and until >time .time ():
        mute_label =f"☒ سکوت {format_duration_full (int (until -time .time ()))}"
    block_on ="◉"if target_id in BLOCKED_USERS .get (owner_uid ,set ())else "○"
    rows =[
    [InlineKeyboardButton (mute_label ,callback_data =f"act_mute_{owner_uid }_{chat_id }_{target_id }"),
    InlineKeyboardButton (f"⊘ بلاک {block_on }",callback_data =f"act_block_{owner_uid }_{chat_id }_{target_id }")],
    [InlineKeyboardButton (f"✘ دشمن {on_list (ENEMY_LIST )}",callback_data =f"act_enemy_{owner_uid }_{chat_id }_{target_id }"),
    InlineKeyboardButton (f"✚ دوست {on_list (FRIEND_LIST )}",callback_data =f"act_friend_{owner_uid }_{chat_id }_{target_id }")],
    [InlineKeyboardButton (f"♡ کراش {on_list (CRASH_LIST )}",callback_data =f"act_crash_{owner_uid }_{chat_id }_{target_id }"),
    InlineKeyboardButton ("✕ بستن",callback_data =f"act_close_{owner_uid }_{chat_id }_{target_id }")]
    ]
    return InlineKeyboardMarkup (rows )

def build_action_panel_markup_json (owner_uid :int ,chat_id :int ,target_id :int ):
    return {"inline_keyboard":[
    [{"text":b .text ,"callback_data":b .callback_data }for b in row ]
    for row in build_action_panel_markup (owner_uid ,chat_id ,target_id ).inline_keyboard 
    ]}

def build_action_panel_text (owner_uid :int ,chat_id :int ,target_id :int ):
    return (
    "╔══════════════════════════════╗\n"
    "        **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 | ACTION**\n"
    "╚══════════════════════════════╝\n\n"
    f"`USER` `{target_id }`\n"
    f"`CHAT` `{chat_id }`\n\n"
    "◉ فعال    ○ خاموش\n"
    "اقدام موردنظر را انتخاب کن."
    )

async def action_panel_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    if not message .reply_to_message or not message .reply_to_message .from_user :
        return await message .edit_text ("**برای باز کردن پنل اکشن، روی پیام کاربر ریپلای کن و بزن:**\n`اکشن`")
    target_id =int (message .reply_to_message .from_user .id )
    chat_id =int (message .chat .id )
    global BOT_USERNAME 
    try :
        if not BOT_USERNAME :
            if not manager_bot .me :await manager_bot .get_me ()
            BOT_USERNAME =manager_bot .me .username 
        results =await asyncio .wait_for (client .get_inline_bot_results (BOT_USERNAME ,f"action_{uid }_{chat_id }_{target_id }"),timeout =5.0 )
        if results and results .results :
            await message .delete ()
            await client .send_inline_bot_result (chat_id ,results .query_id ,results .results [0 ].id )
            asyncio .create_task (schedule_inline_auto_close_by_chat ("action",uid ,client ,chat_id ,message .id ))
        else :
            await message .edit_text ("**پنل اکشن دریافت نشد. Inline Mode را بررسی کنید.**")
    except Exception :
        await message .edit_text ("**پنل اکشن باز نشد.**")

async def timed_tools_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )or ""
    normalized =cmd .replace ("پاک‌شونده","پاک شونده").strip ()

    if normalized .startswith ("پاک شونده"):
        rest =normalized [len ("پاک شونده"):].strip ()
        delay =parse_time_duration (rest )
        if not delay :
            return await message .edit_text ("**فرمت صحیح:**\n`پاک شونده 10 دقیقه`\n`پاک شونده 2 ساعت`")
        SELF_DESTRUCT_DELAY [uid ]=delay 
        SELF_DESTRUCT_STATUS [uid ]=True 
        data_manager .update_user_data (uid ,{"settings":{"self_destruct":True ,"self_destruct_delay":delay }})
        return await message .edit_text (f"**حالت پاک‌شونده روشن شد.**\nزمان حذف: `{format_duration (delay )}`")

    if normalized .startswith ("ارسال"):
        rest =normalized [len ("ارسال"):].strip ()
        delay =parse_time_duration (rest )
        if not delay :
            return await message .edit_text ("**فرمت صحیح:**\n`ارسال 10 دقیقه بعد متن پیام`\nیا روی پیام ریپلای کن: `ارسال 2 ساعت بعد`")

        msg_text =re .sub (r"^\s*\d+\s*(ثانیه|ثانيه|دقیقه|دقيقه|ساعت|روز)\s*(بعد)?\s*","",rest ,flags =re .I ).strip ()
        if not msg_text and message .reply_to_message :
            msg_text =message .reply_to_message .text or message .reply_to_message .caption or ""
        if not msg_text :
            return await message .edit_text ("**متن پیام زمان‌دار خالی است.**")
        await schedule_timed_send (client ,message .chat .id ,msg_text ,delay )

        try :
            await message .delete ()
        except Exception :
            pass 
        return 

async def reply_based_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )
    if not getattr (message ,"reply_to_message",None ):
        await ensure_reply_message (client ,message )

    if message .reply_to_message :
        tid =message .reply_to_message .from_user .id if message .reply_to_message .from_user else None 

        if cmd =="دانلود":
            rm =message .reply_to_message 
            if rm .media :
                size =get_media_file_size (rm )
                if size and size >DIRECT_DOWNLOAD_MAX_MB *1024 *1024 :
                    return await safe_edit_message (message ,f"**حجم فایل بالاست. سقف دانلود مستقیم `{DIRECT_DOWNLOAD_MAX_MB }MB` است.**")
                await safe_edit_message (message ,"**در حال دانلود فایل...**")
                f_path =await rm .download (file_name =ensure_download_temp_dir ()+os .sep )
                await client .send_document ("me",f_path ,caption ="فایل دانلود شد.")
                await message .delete ()
                if os .path .exists (f_path ):os .remove (f_path )
            else :await safe_edit_message (message ,"**پیام انتخاب‌شده فاقد فایل است.**")

        elif cmd =="ذخیره":
            rm =message .reply_to_message 
            sender_name =rm .from_user .first_name if rm .from_user else (rm .sender_chat .title if rm .sender_chat else "ناشناس")

            await safe_edit_message (message ,"**در حال ذخیره‌سازی...**")
            try :
                _rm_has_hint =False
                try :
                    _rm_has_hint =(rm .chat and rm .id and (rm .chat .id ,rm .id )in RAW_TTL_MEDIA_HINTS )
                except Exception :
                    _rm_has_hint =False
                if rm .media or _rm_has_hint :
                    size =get_media_file_size (rm )
                    if size and size >DIRECT_DOWNLOAD_MAX_MB *1024 *1024 :
                        return await safe_edit_message (message ,f"**حجم فایل بالاست. سقف ذخیره مستقیم `{DIRECT_DOWNLOAD_MAX_MB }MB` است.**")
                    file_path =await download_special_media (client ,rm ,ensure_download_temp_dir ()+os .sep )
                    if file_path :
                        cap =f"فرستنده: {sender_name }"
                        _rm_hint =RAW_TTL_MEDIA_HINTS .get ((rm .chat .id ,rm .id ))
                        _rm_kind =_rm_hint .get ("kind")if isinstance (_rm_hint ,dict )else None
                        if getattr (rm ,"photo",None )or _rm_kind =="photo":await client .send_photo ("me",file_path ,caption =cap )
                        elif getattr (rm ,"video",None )or _rm_kind =="video":await client .send_video ("me",file_path ,caption =cap )
                        elif getattr (rm ,"audio",None ):await client .send_audio ("me",file_path ,caption =cap )
                        elif getattr (rm ,"voice",None )or _rm_kind =="voice":await client .send_voice ("me",file_path ,caption =cap )
                        elif getattr (rm ,"document",None ):await client .send_document ("me",file_path ,caption =cap )
                        elif getattr (rm ,"animation",None )or _rm_kind =="animation":await client .send_animation ("me",file_path ,caption =cap )
                        elif getattr (rm ,"sticker",None ):
                            await client .send_message ("me",cap )
                            await client .send_sticker ("me",file_path )
                        else :
                            await client .send_document ("me",file_path ,caption =cap )
                        os .remove (file_path )
                        await safe_edit_message (message ,"**مدیا در پیام‌های ذخیره‌شده ثبت شد.**")
                else :
                    text_to_save =rm .text or ""
                    await client .send_message ("me",f"فرستنده: {sender_name }\n\n{text_to_save }")
                    await safe_edit_message (message ,"**متن در پیام‌های ذخیره‌شده ثبت شد.**")
            except Exception as e :await safe_edit_message (message ,f"**خطا در ذخیره‌سازی:**\n`{e }`")
            await asyncio .sleep (2 )
            try :await message .delete ()
            except Exception :pass 

        elif cmd =="بن":
            if message .chat .type in [ChatType .GROUP ,ChatType .SUPERGROUP ]and tid :
                try :
                    await client .ban_chat_member (message .chat .id ,tid )
                    await safe_edit_message (message ,"**کاربر مورد نظر بن شد.**")
                except Exception as e :
                    err =str (e ).lower ()
                    if "chat_admin_required"in err or "admin"in err :
                        await safe_edit_message (message ,"**برای بن کردن کاربر باید در این چت دسترسی ادمین داشته باشید.**")
                    else :
                        await safe_edit_message (message ,f"**بن کردن کاربر انجام نشد:**\n`{str (e )[:120 ]}`")
            else :
                await safe_edit_message (message ,"**این دستور فقط در گروه و با ریپلای روی کاربر قابل اجرا است.**")

        elif cmd =="پین":
            try :
                await message .reply_to_message .pin ()
                await safe_edit_message (message ,"**پیام مورد نظر پین شد.**")
            except Exception as e :
                err =str (e ).lower ()
                if "chat_admin_required"in err or "admin"in err :
                    await safe_edit_message (message ,"**برای پین کردن پیام باید در این چت دسترسی ادمین داشته باشید.**")
                else :
                    await safe_edit_message (message ,f"**پین کردن پیام انجام نشد:**\n`{str (e )[:120 ]}`")

        elif cmd in ("تکرار خاموش","تکرار خاموش همه","توقف تکرار","حذف تکرار"):
            rep_dict =TABCHI_REPEATER .get (uid ,{})
            if cmd in ("تکرار خاموش همه","توقف تکرار","حذف تکرار")or not rep_dict or len (rep_dict )==1 or message .chat .id in rep_dict :
                if message .chat .id in rep_dict :
                    rep_dict .pop (message .chat .id ,None )
                if cmd in ("تکرار خاموش همه","توقف تکرار","حذف تکرار")or len (rep_dict )==0 :
                    TABCHI_REPEATER [uid ]={}
                    data_manager .update_user_data (uid ,{"settings":{"tabchi_repeater":{}}})
                    await safe_edit_message (message ,"تمام تکرارهای خودکار در کل چت‌ها متوقف شدند.")
                else :
                    data_manager .update_user_data (uid ,{"settings":{"tabchi_repeater":rep_dict }})
                    await safe_edit_message (message ,"تکرار خودکار زمان‌دار در این چت خاموش شد.")
            else :
                await safe_edit_message (message ,"تکرار خودکاری در این چت فعال نیست. برای توقف تکرار در کل چت‌ها، دستور «تکرار خاموش همه» را بفرستید.")
        elif cmd .startswith ("تکرار "):
            parts =cmd .split ()
            val_str =parts [1 ]if len (parts )>1 else ""
            sec =parse_time_duration (" ".join (parts [1 :]))
            if not sec and len (parts )>2 and "ثانیه"in cmd :
                try :sec =int (val_str )
                except Exception :pass 
            if sec or "ثانیه"in cmd or "دقیقه"in cmd or "ساعت"in cmd :
                if not sec :
                    try :sec =int (val_str )
                    except Exception :pass 
                if not sec or sec <5 or sec >TABCHI_REPEATER_MAX :
                    await safe_edit_message (message ,f"تایم تکرار باید بین ۵ تا {TABCHI_REPEATER_MAX } ثانیه باشد.")
                elif not message .reply_to_message :
                    await safe_edit_message (message ,"برای تنظیم تکرار زمان‌دار، روی یک پیام ریپلای کنید.")
                else :
                    rep_dict =TABCHI_REPEATER .setdefault (uid ,{})
                    rep_dict [message .chat .id ]={"msg_id":message .reply_to_message .id ,"timer":sec ,"last_ts":time .time ()}
                    data_manager .update_user_data (uid ,{"settings":{"tabchi_repeater":rep_dict }})
                    await safe_edit_message (message ,f"تکرار خودکار این پیام هر {sec } ثانیه در همین چت فعال شد.\nبرای توقف دستور «تکرار خاموش» را بفرستید.")
            else :
                try :
                    c =int (val_str )
                    await message .delete ()
                    for _ in range (min (c ,20 )):
                        await message .reply_to_message .copy (message .chat .id )
                        await asyncio .sleep (1.0 )
                except Exception :pass 

        elif tid :
            if cmd =="بلاک":
                try :
                    await client .block_user (tid )
                    await safe_edit_message (message ,"**کاربر مورد نظر در لیست بلاک قرار گرفت.**")
                except Exception as e :
                    err =str (e ).lower ()
                    if "peer_id_invalid"in err or "peer id"in err :
                        await safe_edit_message (message ,"**بلاک انجام نشد.**\nاین کاربر هنوز برای این سلف شناخته‌شده نیست؛ اول یک پیام از او در همین چت ببینید یا دوباره امتحان کنید.")
                    else :
                        await safe_edit_message (message ,friendly_telegram_error (e ,"بلاک کردن"))
            elif cmd =="حذف بلاک":
                try :
                    await client .unblock_user (tid )
                    await safe_edit_message (message ,"**کاربر مورد نظر از لیست بلاک خارج شد.**")
                except Exception as e :
                    err =str (e ).lower ()
                    if "peer_id_invalid"in err or "peer id"in err :
                        await safe_edit_message (message ,"**آنبلاک انجام نشد.**\nاین کاربر هنوز برای این سلف شناخته‌شده نیست.")
                    else :
                        await safe_edit_message (message ,friendly_telegram_error (e ,"آنبلاک کردن"))
            elif cmd .startswith ("سکوت "):
                delay =parse_time_duration (cmd )
                if not delay :
                    return await safe_edit_message (message ,"**فرمت صحیح:**\n`سکوت 10 دقیقه`\n`سکوت 2 ساعت`")
                s =MUTED_USERS .setdefault (uid ,set ())
                key =(tid ,message .chat .id )
                s .add (key )
                until =time .time ()+delay 
                MUTED_UNTIL .setdefault (uid ,{})[key ]=until 
                timed =[[k [0 ],k [1 ],v ]for k ,v in MUTED_UNTIL .get (uid ,{}).items ()if v >time .time ()]
                data_manager .update_user_data (uid ,{"muted":[list (x )for x in s ],"timed_muted":timed })
                await schedule_unmute (uid ,tid ,message .chat .id ,delay )
                await safe_edit_message (message ,f"**کاربر مورد نظر به مدت `{format_duration (delay )}` سکوت شد.**")
            elif cmd =="تنظیم سکوت":
                s =MUTED_USERS .setdefault (uid ,set ())
                key =(tid ,message .chat .id )
                if key in s :
                    await safe_edit_message (message ,"**این کاربر از قبل در این چت سکوت شده است.**")
                    return 
                s .add (key )
                data_manager .update_user_data (uid ,{"muted":[list (x )for x in s ]})
                await safe_edit_message (message ,"**کاربر مورد نظر در لیست سکوت قرار گرفت.**")
            elif cmd =="حذف سکوت":
                s =MUTED_USERS .get (uid ,set ())
                key =(tid ,message .chat .id )
                if key not in s :
                    await safe_edit_message (message ,"**این کاربر در این چت سکوت نشده است.**")
                    return 
                s .remove (key )
                MUTED_UNTIL .get (uid ,{}).pop (key ,None )
                timed =[[k [0 ],k [1 ],v ]for k ,v in MUTED_UNTIL .get (uid ,{}).items ()if v >time .time ()]
                data_manager .update_user_data (uid ,{"muted":[list (x )for x in s ],"timed_muted":timed })
                await safe_edit_message (message ,"**کاربر مورد نظر از لیست سکوت خارج شد.**")
            elif cmd .startswith ("ریاکت ")and cmd not in ("لیست ریاکت","ریاکت پاکسازی"):
                parts =cmd .split (maxsplit =1 )
                if len (parts )<2 or not parts [1 ].strip ():
                    await safe_edit_message (message ,"**فرمت صحیح:**\n`ریاکت [ایموجی]`")
                    return 
                reaction_emoji =parts [1 ].strip ()
                try :

                    await client .send_reaction (message .chat .id ,message .reply_to_message .id ,reaction_emoji )
                except Exception :
                    await safe_edit_message (message ,"**هشدار لطفا ریاکت مناسب را انتخاب کنید.**")
                    return 
                t =AUTO_REACTION_TARGETS .setdefault (uid ,{})
                t [str (tid )]=reaction_emoji 
                data_manager .update_user_data (uid ,{"reactions":t })
                await safe_edit_message (message ,"**ری‌اکشن خودکار برای کاربر مورد نظر فعال شد.**")
            elif cmd =="حذف ریاکت":
                t =AUTO_REACTION_TARGETS .get (uid ,{})
                if str (tid )in t :
                    t .pop (str (tid ),None )
                    data_manager .update_user_data (uid ,{"reactions":t })
                    await safe_edit_message (message ,"**ری‌اکشن خودکار برای کاربر مورد نظر غیرفعال شد.**")
                else :
                    await safe_edit_message (message ,"**برای کاربر مورد نظر ری‌اکشن فعالی ثبت نشده است.**")

async def auto_reaction_list_handler (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):
        return 
    targets =AUTO_REACTION_TARGETS .get (uid ,{})
    if not targets :
        await safe_edit_message (message ,"**لیست ری‌اکشن‌های خودکار خالی است.**")
        return 

    rows =["**لیست کاربران دارای ری‌اکشن خودکار:**"]
    for idx ,(tid_str ,emoji )in enumerate (targets .items (),1 ):
        display_name ="کاربر ناشناس"
        try :
            user =await client .get_users (int (tid_str ))
            full_name =f"{user .first_name or ''} {user .last_name or ''}".strip ()
            display_name =full_name or (f"@{user .username }"if user .username else "کاربر ناشناس")
        except Exception :
            pass 
        rows .append (f"{idx }. **{display_name }**  |  {emoji }")
    await safe_edit_message (message ,"\n".join (rows )[:4000 ])

async def auto_reaction_clear_handler (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):
        return 
    AUTO_REACTION_TARGETS [uid ]={}
    data_manager .update_user_data (uid ,{"reactions":{}})
    await safe_edit_message (message ,
    "**لیست ری‌اکشن‌های خودکار پاکسازی شد.**"
    )

def _strip_html (raw :str )->str :
    raw =re .sub (r"<script.*?</script>|<style.*?</style>"," ",raw ,flags =re .S |re .I )
    raw =re .sub (r"<[^>]+>"," ",raw )
    raw =html .unescape (raw )
    raw =re .sub (r"\s+"," ",raw ).strip ()
    return raw 

async def search_web_snippets (query :str ,limit :int =5 ):
    headers ={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language":"fa,en;q=0.8",
    }
    session =await get_http_session ()
    candidates =[]

    def norm (txt :str )->str :
        txt =_strip_html (txt or "").lower ()
        txt =txt .replace ("ي","ی").replace ("ك","ک").replace ("‌"," ")
        txt =re .sub (r"[^0-9a-zA-Zآ-ی\s]"," ",txt )
        return re .sub (r"\s+"," ",txt ).strip ()

    stop_words ={
    "از","به","در","با","برای","و","یا","که","این","آن","را","روی","یک","تا","چی","چیه","چگونه","چطور",
    "the","and","for","with","what","how","is","are","of","to","in"
    }
    query_norm =norm (query )
    keywords =[w for w in query_norm .split ()if len (w )>1 and w not in stop_words ]
    if not keywords :
        keywords =query_norm .split ()

    def score_item (title :str ,snippet :str )->int :
        t =norm (title )
        sn =norm (snippet )
        full =f"{t } {sn }"
        score =0 
        if query_norm and query_norm in full :
            score +=12 
        for kw in keywords :
            if kw in t :
                score +=4 
            if kw in sn :
                score +=2 

        matched =sum (1 for kw in keywords if kw in full )
        if len (keywords )>=3 and matched <2 :
            return 0 
        if len (keywords )==2 and matched <1 :
            return 0 
        return score 

    def add_candidate (title ,snippet ,source =""):
        title =_strip_html (title or "")
        snippet =_strip_html (snippet or "")
        if not snippet and title :
            snippet =title 
        if not title or not snippet :
            return 
        sc =score_item (title ,snippet )
        if sc <=0 :
            return 
        key =(title ,snippet )
        if all ((a ,b )!=key for _ ,a ,b ,_ in candidates ):
            candidates .append ((sc ,title ,snippet ,source ))

    try :
        url =f"https://lite.duckduckgo.com/lite/?q={quote (query )}"
        async with session .get (url ,headers =headers ,timeout =aiohttp .ClientTimeout (total =8 ))as resp :
            page =await resp .text ()
        titles =re .findall (r"class=['\"]result-link['\"][^>]*>(.*?)</a>",page ,flags =re .S |re .I )
        snippets =re .findall (r"class=['\"]result-snippet['\"][^>]*>(.*?)</td>",page ,flags =re .S |re .I )
        for i ,title in enumerate (titles [:10 ]):
            add_candidate (title ,snippets [i ]if i <len (snippets )else "","duck")
    except Exception :
        pass 

    try :
        url =f"https://duckduckgo.com/html/?q={quote (query )}"
        async with session .get (url ,headers =headers ,timeout =aiohttp .ClientTimeout (total =8 ))as resp :
            page =await resp .text ()
        titles =re .findall (r"class=['\"]result__a['\"][^>]*>(.*?)</a>",page ,flags =re .S |re .I )
        snippets =re .findall (r"class=['\"]result__snippet['\"][^>]*>(.*?)</(?:a|div)>",page ,flags =re .S |re .I )
        for i ,title in enumerate (titles [:10 ]):
            add_candidate (title ,snippets [i ]if i <len (snippets )else "","duck_html")
    except Exception :
        pass 

    try :
        url =f"https://www.bing.com/search?q={quote (query )}&setlang=fa"
        async with session .get (url ,headers =headers ,timeout =aiohttp .ClientTimeout (total =8 ))as resp :
            page =await resp .text ()
        blocks =re .findall (r'<li class="b_algo".*?</li>',page ,flags =re .S |re .I )
        for block in blocks [:10 ]:
            title_m =re .search (r'<h2[^>]*>.*?<a[^>]*>(.*?)</a>.*?</h2>',block ,flags =re .S |re .I )
            snip_m =re .search (r'<p[^>]*>(.*?)</p>',block ,flags =re .S |re .I )
            add_candidate (title_m .group (1 )if title_m else "",snip_m .group (1 )if snip_m else "","bing")
    except Exception :
        pass 

    try :
        url =f"https://api.wikimedia.org/core/v1/wikipedia/fa/search/page?q={quote (query )}&limit=10"
        async with session .get (url ,headers =headers ,timeout =aiohttp .ClientTimeout (total =6 ))as resp :
            data =await resp .json (content_type =None )
        for item in data .get ("pages",[]):
            add_candidate (item .get ("title",""),item .get ("excerpt","")or item .get ("description",""),"wiki")
    except Exception :
        pass 

    if not candidates :
        return []

    candidates .sort (key =lambda x :x [0 ],reverse =True )
    return [(title ,snippet )for _ ,title ,snippet ,_ in candidates [:limit ]]

def is_clickbait_or_weak (text :str )->bool :
    t =(text or "").lower ()
    bad_words =(
    "قاتل","سه سوته","قطعی","واقعی","معجزه","تضمینی","فوری و خانگی",
    "بهترین روش","باورنکردنی","حتی شدیدترین","معرفی","کلیک","همین حالا"
    )
    return any (w in t for w in bad_words )

def clean_search_sentence (text :str )->str :
    text =_strip_html (text or "")
    text =re .sub (r"\s+"," ",text ).strip ()

    parts =re .split (r"(?<=[.!؟])\s+",text )
    good =[]
    for part in parts :
        if not is_clickbait_or_weak (part ):
            good .append (part .strip ())
    text =" ".join (good ).strip ()if good else text 
    return text [:450 ].strip ()

def make_basic_search_answer (query ):
    q =str (query ).strip ()[:120 ]
    return f"🔎 نتیجه‌ی قابل اتکایی برای «{q }» پیدا نشد.\n\nسوالت رو دقیق‌تر یا با کلمات دیگه بنویس و دوباره امتحان کن."

def build_dental_answer (query :str )->str :
    return (
    f"╔══════════════════════════════╗\n"
    f"        **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 | SEARCH**\n"
    f"╚══════════════════════════════╝\n\n"
    f"**موضوع:** `{query }`\n\n"
    f"**متن دقیق برای مطالعه:**\n"
    f"دندان‌درد معمولاً به‌خاطر تحریک عصب دندان، پوسیدگی، التهاب لثه، گیر کردن غذا بین دندان‌ها، ترک یا شکستگی دندان، یا عفونت ایجاد می‌شود. تسکین خانگی فقط موقتی است و علت اصلی باید توسط دندان‌پزشک بررسی شود.\n\n"
    f"**برای کاهش موقت درد:**\n"
    f"1. دهان را با آب ولرم تمیز کنید و اگر غذا بین دندان‌ها گیر کرده، آرام نخ‌دندان بکشید.\n"
    f"2. اگر ورم یا درد ضربان‌دار دارید، کمپرس سرد را 10 تا 15 دقیقه روی گونه بگذارید.\n"
    f"3. از غذا و نوشیدنی خیلی سرد، خیلی گرم، شیرین یا سفت دوری کنید.\n"
    f"4. در صورت نیاز، مسکن معمول را فقط طبق دستور دارو یا توصیه پزشک/داروساز مصرف کنید.\n\n"
    f"**کارهایی که انجام ندهید:**\n"
    f"آسپرین، الکل، مواد اسیدی یا هر دارو را مستقیم روی لثه و دندان نگذارید؛ ممکن است باعث سوختگی و بدتر شدن التهاب شود.\n\n"
    f"**مراجعه فوری لازم است اگر:**\n"
    f"درد شدید یا بیش از 24 تا 48 ساعت ادامه داشت، صورت یا لثه ورم کرد، تب داشتید، چرک یا بوی بد حس کردید، یا درد بعد از ضربه و شکستگی دندان شروع شد.\n\n"
    f"**توجه:** این متن جایگزین معاینه دندان‌پزشک نیست."
    )

async def search_topic_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )
    m =re .match (r"^سرچ\s+(.+)$",cmd ,flags =re .S |re .I )
    if not m :
        return 
    query =m .group (1 ).strip ()
    if len (query )<2 :
        return await safe_edit_message (message ,"**موضوع جستجو را وارد کنید.**\n`سرچ [موضوع]`")

    wait_msg =await safe_edit_message (message ,"**در حال جستجو و آماده‌سازی متن...**")
    try :
        q_norm =query .replace ("ي","ی").replace ("ك","ک").lower ()

        if "دندان"in q_norm or "tooth"in q_norm or "toothache"in q_norm :
            return await wait_msg .edit_text (build_dental_answer (query )[:4000 ])

        results =await search_web_snippets (query ,limit =8 )
        if not results :
            fallback =make_basic_search_answer (query )
            return await wait_msg .edit_text (fallback [:4000 ])

        points =[]
        for title ,snippet in results :
            cleaned =clean_search_sentence (snippet )
            if not cleaned or is_clickbait_or_weak (cleaned ):
                continue 

            q_words =[w for w in re .sub (r"[^0-9a-zA-Zآ-ی\s]"," ",q_norm ).split ()if len (w )>1 ]
            if q_words and not any (w in cleaned .lower ().replace ("ي","ی").replace ("ك","ک")for w in q_words [:5 ]):
                continue 
            if cleaned not in points :
                points .append (cleaned )
            if len (points )>=5 :
                break 

        if not points :
            fallback =make_basic_search_answer (query )
            return await wait_msg .edit_text (fallback [:4000 ])

        summary ="\n\n".join ([f"{i +1 }. {txt }"for i ,txt in enumerate (points [:5 ])])
        medical_words =("درد","دارو","بیماری","درمان","پزشک","علائم","عفونت")
        caution =""
        if any (w in q_norm for w in medical_words ):
            caution ="\n\n**توجه:** این متن جایگزین نظر پزشک نیست؛ اگر علائم شدید یا طولانی دارید مراجعه حضوری لازم است."

        text =(
        f"╔══════════════════════════════╗\n"
        f"        **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 | SEARCH**\n"
        f"╚══════════════════════════════╝\n\n"
        f"**موضوع:** `{query }`\n\n"
        f"**متن پیشنهادی برای مطالعه:**\n{summary }"
        f"{caution }"
        )
        await wait_msg .edit_text (text [:4000 ])
    except Exception as e :
        await wait_msg .edit_text (f"**جستجو انجام نشد:**\n`{str (e )[:120 ]}`")

async def image_search_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )
    m =re .match (r"^عکس\s+(.+)$",cmd )
    if not m :
        return 
    query =m .group (1 ).strip ()
    if not query :
        return 

    uptt =await safe_edit_message (message ,f"🔎 جستجوی `{query }`...")

    headers ={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    try :
        session =await get_http_session ()
        image_urls =[]

        for src_url in [
        f"https://www.bing.com/images/search?q={quote (query )}&form=HDRSC2&adlt=strict",
        f"https://www.google.com/search?q={quote (query )}&safe=active&tbm=isch&hl=en&gbv=1",
        ]:
            try :
                async with session .get (src_url ,headers =headers ,timeout =aiohttp .ClientTimeout (total =8 ))as resp :
                    html =await resp .text ()
                html =html .replace ("&quot;",'"').replace ("&amp;","&").replace ("&#39;","'").replace ("&lt;","<").replace ("&gt;",">")

                extracted =[]
                if "bing.com"in src_url :
                    for pat in [
                    r'mediaurl"\s*:\s*"(https?://[^"]+)"',
                    r'murl"\s*:\s*"(https?://[^"]+)"',
                    r'"mediaurl"\s*:\s*"(https?://[^"]+)"',
                    r'"murl"\s*:\s*"(https?://[^"]+)"',
                    ]:
                        extracted =re .findall (pat ,html ,re .I )
                        if extracted :
                            break 
                    if not extracted :
                        extracted =re .findall (r'<img[^>]+src="(https?://[^"\s]+)"',html ,re .I )
                else :
                    extracted =re .findall (r'"(https?://[^"\s]+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^"]*)??)"',html ,re .I )

                extracted =[u for u in extracted if "bing.com"not in u and "gstatic.com"not in u and "google"not in u and "th.bing.com"not in u and u .startswith ("http")]
                if extracted :
                    image_urls =extracted 
                    break 
            except Exception :
                continue 

        if not image_urls :
            return await uptt .edit_text ("**نتیجه‌ای پیدا نشد.**")

        random .shuffle (image_urls )
        temp_path =f"_img_{uuid .uuid4 ().hex }.jpg"
        img_ext =".jpg"
        downloaded =False 

        max_attempts =min (10 ,len (image_urls ))
        for url_candidate in image_urls [:max_attempts ]:
            try :
                async with session .get (url_candidate ,headers =headers ,timeout =aiohttp .ClientTimeout (total =20 ))as img_resp :
                    if img_resp .status !=200 :
                        continue 

                    content_length =img_resp .headers .get ("Content-Length")
                    if content_length and int (content_length )>20 *1024 *1024 :
                        continue 
                    written =0 
                    too_big =False 
                    with open (temp_path ,"wb")as f :
                        async for chunk in img_resp .content .iter_chunked (64 *1024 ):
                            f .write (chunk )
                            written +=len (chunk )
                            if written >20 *1024 *1024 :
                                too_big =True 
                                break 
                    if too_big or written ==0 :
                        try :os .remove (temp_path )
                        except Exception :pass 
                        continue 
                    img_ext =os .path .splitext (url_candidate .split ("?")[0 ])[1 ]or ".jpg"
                    if len (img_ext )>5 :
                        img_ext =".jpg"
                    downloaded =True 
                    break 
            except Exception :
                continue 

        if not downloaded or not os .path .exists (temp_path ):
            try :
                if os .path .exists (temp_path ):os .remove (temp_path )
            except Exception :pass 
            return await uptt .edit_text ("**دانلود تصویر انجام نشد.**")

        if img_ext !=".jpg":
            new_path =temp_path .rsplit (".",1 )[0 ]+img_ext 
            try :
                os .rename (temp_path ,new_path )
                temp_path =new_path 
            except Exception :
                pass 

        try :
            await client .send_photo (
            message .chat .id ,
            temp_path ,
            caption =f"🔍 `{query }`",
            )
        except Exception :
            try :
                await client .send_document (
                message .chat .id ,
                document =temp_path ,
                caption =f"🔍 `{query }`",
                )
            except Exception :
                pass 
        finally :
            if os .path .exists (temp_path ):
                try :os .remove (temp_path )
                except Exception :pass 

        try :await uptt .delete ()
        except Exception :pass 
    except Exception as e :
        try :
            await uptt .edit_text (f"**خطا:** `{str (e )[:120 ]}`")
        except Exception :
            pass 

async def tools_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )

    if cmd in ["تگ","tagall"]:
        if message .chat .type in [ChatType .GROUP ,ChatType .SUPERGROUP ]:
            try :
                await message .delete ()
            except Exception :
                pass 
            try :
                mems =[]
                async for m in client .get_chat_members (message .chat .id ,limit =100 ):
                    if m .user and not m .user .is_bot and m .user .username :
                        mems .append (f'@{m .user .username }')
                for i in range (0 ,len (mems ),6 ):
                    try :
                        await client .send_message (message .chat .id ,'\n'.join (mems [i :i +6 ]))
                    except FloodWait as fw :
                        await asyncio .sleep (min (int (getattr (fw ,"value",1 )or 1 ),15 ))
                    except (ChatWriteForbidden ,ChannelPrivate ,ChannelInvalid ,PeerIdInvalid ):
                        break 
                    except Exception as e :
                        if type (e ).__name__ in ("ChatWriteForbidden","UserBannedInChannel","ChatAdminRequired","ChannelPrivate"):
                            break 
                    await asyncio .sleep (1 )
            except Exception as e :
                logger .warning ("tagall failed: %s",type (e ).__name__ )

    elif cmd in ["تگ ادمین ها"]:
        if message .chat .type in [ChatType .GROUP ,ChatType .SUPERGROUP ]:
            try :
                await message .delete ()
            except Exception :
                pass 
            try :
                ads =[]
                async for m in client .get_chat_members (message .chat .id ,filter =ChatMembersFilter .ADMINISTRATORS ):
                    if m .user and not m .user .is_bot and m .user .username :
                        ads .append (f'@{m .user .username }')
                for i in range (0 ,len (ads ),6 ):
                    try :
                        await client .send_message (message .chat .id ,'ادمین‌ها:\n'+'\n'.join (ads [i :i +6 ]))
                    except FloodWait as fw :
                        await asyncio .sleep (min (int (getattr (fw ,"value",1 )or 1 ),15 ))
                    except (ChatWriteForbidden ,ChannelPrivate ,ChannelInvalid ,PeerIdInvalid ):
                        break 
                    except Exception as e :
                        if type (e ).__name__ in ("ChatWriteForbidden","UserBannedInChannel","ChatAdminRequired","ChannelPrivate"):
                            break 
                    await asyncio .sleep (1 )
            except Exception as e :
                logger .warning ("tag admins failed: %s",type (e ).__name__ )

    elif cmd =="آن پین":
        await client .unpin_chat_message (message .chat .id )
        await safe_edit_message (message ,"**پین پیام برداشته شد.**")

    elif cmd .startswith ("اسپم "):
        try :
            parts =cmd .split (maxsplit =2 )
            txt ,c =parts [1 ],int (parts [2 ])
            await message .delete ()
            for _ in range (min (c ,20 )):
                await client .send_message (message .chat .id ,txt )
                await asyncio .sleep (0.8 )
        except Exception :await safe_edit_message (message ,"**فرمت صحیح:** `اسپم [متن] [تعداد]`")

    elif cmd .startswith ("فلود "):
        try :
            parts =cmd .split (maxsplit =2 )
            txt ,c =parts [1 ],int (parts [2 ])
            await message .delete ()
            await client .send_message (message .chat .id ,(txt +"\n")*min (c ,30 ))
        except Exception :await safe_edit_message (message ,"**فرمت صحیح:** `فلود [متن] [تعداد]`")

    elif cmd .startswith ("حذف"):
        if re .match (r"^حذف (گروه|کانال)\s",cmd )or cmd in PROFILE_DELETE_CMDS :
            return 
        try :
            if cmd =="حذف همه":count =200 
            else :
                parts =cmd .split ()
                count =int (parts [1 ])if len (parts )>1 else 5 
                if count <1 :count =1 
                if count >200 :count =200 

            chat_id =message .chat .id 
            message_ids_to_delete =[message .id ]
            user_messages_found =0 

            fetch_limit =min (max (count *3 ,60 ),500 )

            async for msg in client .get_chat_history (chat_id ,limit =fetch_limit ):
                if msg .id ==message .id :continue 
                if msg .from_user and msg .from_user .id ==uid :
                    message_ids_to_delete .append (msg .id )
                    user_messages_found +=1 
                    if user_messages_found >=count :break 

            if message_ids_to_delete :
                for i in range (0 ,len (message_ids_to_delete ),100 ):
                    batch =message_ids_to_delete [i :i +100 ]
                    try :
                        await client .delete_messages (chat_id ,batch )
                        await asyncio .sleep (0.3 )
                    except FloodWait as e :await asyncio .sleep (e .value +1 )
                    except Exception :pass 
        except Exception :pass 

async def copy_profile_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    command =get_cmd (uid ,message .text )

    if command not in ["کپی روشن","کپی خاموش"]:
        return 

    requires_reply =command =="کپی روشن"

    async def _send_ephemeral_status (text :str ):
        try :
            m =await client .send_message (message .chat .id ,text )
            try :await m .delete ()
            except Exception :pass 
        except Exception :pass 

    try :await message .delete ()
    except Exception :pass 

    if requires_reply and (not message .reply_to_message or not message .reply_to_message .from_user ):return 

    try :
        if command =="کپی خاموش":
            if not COPY_MODE_STATUS .get (uid ,False ):return 
            original =ORIGINAL_PROFILE_DATA .get (uid )
            if not original :
                COPY_MODE_STATUS [uid ]=False 
                data_manager .update_user_data (uid ,{"settings":{"copy_mode":False }})
                await _send_ephemeral_status ("خاموش شد")
                return 

            try :
                await client .update_profile (first_name =original .get ('first_name',''),last_name =original .get ('last_name',''),bio =original .get ('bio',''))
            except Exception :pass 
            try :
                photos_to_delete =[p .file_id async for p in client .get_chat_photos ("me")]
                if photos_to_delete :await client .delete_profile_photos (photos_to_delete )
            except Exception :pass 

            original_photo_paths =original .get ('photo_paths')or []
            if original_photo_paths :
                for path in original_photo_paths :
                    if not path :continue 
                    try :
                        if os .path .exists (path ):await client .set_profile_photo (photo =path )
                    except Exception :pass 
                    finally :
                        try :
                            if os .path .exists (path ):os .remove (path )
                        except Exception :pass 
            else :
                if original .get ('photo'):
                    try :await client .set_profile_photo (photo =original .get ('photo'))
                    except Exception :pass 
            try :ORIGINAL_PROFILE_DATA .pop (uid ,None )
            except Exception :pass 

            COPY_MODE_STATUS [uid ]=False 
            data_manager .update_user_data (uid ,{"settings":{"copy_mode":False }})
            await _send_ephemeral_status ("خاموش شد")

        elif command =="کپی روشن":
            target_user =message .reply_to_message .from_user 
            target_id =target_user .id 
            me =await client .get_me ()
            me_photo_bytes ,me_bio =None ,""
            try :
                peer =await safe_resolve_peer (client ,"me")
                if peer :
                    me_full =await client .invoke (functions .users .GetFullUser (id =peer ))
                    me_bio =me_full .full_user .about or ''
            except Exception :pass 
            if me .photo :
                try :me_photo_bytes =await client .download_media (me .photo .big_file_id ,in_memory =True )
                except Exception :pass 

            original_photo_paths =[]
            try :
                async for photo in client .get_chat_photos ("me"):
                    try :
                        path =await client .download_media (photo .file_id ,file_name =f"original_{uid }_{photo .file_id }.jpg")
                        if path :
                            original_photo_paths .append (path )
                    except Exception :pass 
            except Exception :pass 

            ORIGINAL_PROFILE_DATA [uid ]={
            'first_name':me .first_name or '','last_name':me .last_name or '',
            'bio':me_bio ,'photo':me_photo_bytes ,'photo_paths':original_photo_paths 
            }

            target_bio =""
            try :
                 peer =await safe_resolve_peer (client ,target_id )
                 if peer :
                     target_full =await client .invoke (functions .users .GetFullUser (id =peer ))
                     target_bio =target_full .full_user .about or ''
            except Exception :pass 

            await client .update_profile (first_name =target_user .first_name or '',last_name =target_user .last_name or '',bio =target_bio )
            try :
                photos_to_delete =[p .file_id async for p in client .get_chat_photos ("me")]
                if photos_to_delete :await client .delete_profile_photos (photos_to_delete )
            except Exception :pass 

            target_photo_paths =[]
            try :
                async for photo in client .get_chat_photos (target_id ):
                    try :
                        path =await client .download_media (photo .file_id ,file_name =f"target_{uid }_{target_id }_{photo .file_id }.jpg")
                        if path :
                            target_photo_paths .append (path )
                    except Exception :pass 
            except Exception :pass 

            if target_photo_paths :
                for path in reversed (target_photo_paths ):
                    if not path :continue 
                    try :
                        if os .path .exists (path ):await client .set_profile_photo (photo =path )
                    except Exception :pass 
                    finally :
                        try :
                            if os .path .exists (path ):os .remove (path )
                        except Exception :pass 
            COPY_MODE_STATUS [uid ]=True 
            data_manager .update_user_data (uid ,{"settings":{"copy_mode":True }})
            await _send_ephemeral_status ("فعال شد")
    except Exception :pass 

PERSIAN_WEEKDAYS =["دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه","شنبه","یکشنبه"]
PERSIAN_MONTHS =["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"]
GREGORIAN_MONTHS_FA =["ژانویه","فوریه","مارس","آوریل","مه","ژوئن","ژوئیه","اوت","سپتامبر","اکتبر","نوامبر","دسامبر"]
HIJRI_MONTHS_FA =["محرم","صفر","ربیع‌الاول","ربیع‌الثانی","جمادی‌الاول","جمادی‌الثانی","رجب","شعبان","رمضان","شوال","ذی‌القعده","ذی‌الحجه"]

def fa_digits (value )->str :
    return str (value ).translate (str .maketrans ("0123456789","۰۱۲۳۴۵۶۷۸۹"))

def gregorian_to_jalali_numbers (gy :int ,gm :int ,gd :int ):
    g_d_m =[0 ,31 ,59 ,90 ,120 ,151 ,181 ,212 ,243 ,273 ,304 ,334 ]
    if gy >1600 :
        jy =979 
        gy -=1600 
    else :
        jy =0 
        gy -=621 
    gy2 =gy +1 if gm >2 else gy 
    days =(365 *gy )+((gy2 +3 )//4 )-((gy2 +99 )//100 )+((gy2 +399 )//400 )-80 +gd +g_d_m [gm -1 ]
    jy +=33 *(days //12053 )
    days %=12053 
    jy +=4 *(days //1461 )
    days %=1461 
    if days >365 :
        jy +=(days -1 )//365 
        days =(days -1 )%365 
    if days <186 :
        jm =1 +(days //31 )
        jd =1 +(days %31 )
    else :
        jm =7 +((days -186 )//30 )
        jd =1 +((days -186 )%30 )
    return jy ,jm ,jd 

def gregorian_to_jdn (year :int ,month :int ,day :int )->int :
    a =(14 -month )//12 
    y =year +4800 -a 
    m =month +12 *a -3 
    return day +((153 *m +2 )//5 )+365 *y +(y //4 )-(y //100 )+(y //400 )-32045 

def islamic_to_jdn (year :int ,month :int ,day :int )->int :

    return day +math .ceil (29.5 *(month -1 ))+(year -1 )*354 +((3 +11 *year )//30 )+1948439 -1 

def gregorian_to_hijri_numbers (gy :int ,gm :int ,gd :int ):
    jd =gregorian_to_jdn (gy ,gm ,gd )
    year =(30 *(jd -1948439 )+10646 )//10631 
    month =min (12 ,math .ceil ((jd -(29 +islamic_to_jdn (year ,1 ,1 )))/29.5 )+1 )
    day =jd -islamic_to_jdn (year ,month ,1 )+1 
    if day <=0 :
        month -=1 
        if month <=0 :
            month =12 
            year -=1 
        day =jd -islamic_to_jdn (year ,month ,1 )+1 
    return int (year ),int (month ),int (day )

def build_datetime_answer (now :datetime ,mode :str ="تاریخ")->str :
    weekday =PERSIAN_WEEKDAYS [now .weekday ()]
    g_y ,g_m ,g_d =now .year ,now .month ,now .day 

    if jdatetime :
        j_now =jdatetime .datetime .fromgregorian (datetime =now )
        j_y ,j_m ,j_d =j_now .year ,j_now .month ,j_now .day 
    else :
        j_y ,j_m ,j_d =gregorian_to_jalali_numbers (g_y ,g_m ,g_d )

    h_y ,h_m ,h_d =gregorian_to_hijri_numbers (g_y ,g_m ,g_d )

    time_24 =fa_digits (now .strftime ("%H:%M:%S"))
    time_12_raw =now .strftime ("%I:%M:%S %p")
    time_12_raw =time_12_raw .replace ("AM","قبل‌ازظهر").replace ("PM","بعدازظهر")
    time_12 =fa_digits (time_12_raw )

    g_num =fa_digits (f"{g_y :04d}/{g_m :02d}/{g_d :02d}")
    j_num =fa_digits (f"{j_y :04d}/{j_m :02d}/{j_d :02d}")
    h_num =fa_digits (f"{h_y :04d}/{h_m :02d}/{h_d :02d}")

    title ="TIME"if str (mode ).lower ()in ("ساعت","time")else "DATE & TIME"

    return (
    f"╔══════════════════════════════╗\n"
    f"        **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 | {title }**\n"
    f"╚══════════════════════════════╝\n\n"
    f"🕰 **ساعت تهران:** `{time_24 }`\n"
    f"⌚️ **فرمت ۱۲ ساعته:** `{time_12 }`\n"
    f"🌐 **منطقه زمانی:** `Asia/Tehran`\n"
    f"📌 **روز هفته:** **{weekday }**\n\n"
    f"╭─────── **تقویم‌ها** ───────╮\n"
    f"│ 📅 **شمسی:** `{j_num }`\n"
    f"│     {fa_digits (j_d )} {PERSIAN_MONTHS [j_m -1 ]} {fa_digits (j_y )}\n"
    f"│ 🌍 **میلادی:** `{g_num }`\n"
    f"│     {fa_digits (g_d )} {GREGORIAN_MONTHS_FA [g_m -1 ]} {fa_digits (g_y )}\n"
    f"│ 🌙 **قمری:** `{h_num }`\n"
    f"│     {fa_digits (h_d )} {HIJRI_MONTHS_FA [h_m -1 ]} {fa_digits (h_y )}\n"
    f"╰────────────────────────╯"
    )

async def datetime_info_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )
    if not cmd :
        return 
    cmd_l =cmd .strip ().lower ()
    if cmd_l not in ("ساعت","تاریخ","time","date"):
        return 

    try :
        now =datetime .now (TEHRAN_TIMEZONE )
        await safe_edit_message (message ,build_datetime_answer (now ,cmd_l ))
    except Exception as e :
        try :
            await safe_edit_message (message ,f"**خطا در دریافت ساعت و تاریخ:**\n`{str (e )[:120 ]}`")
        except Exception :
            pass 

BACKUP_MESSAGE_LIMIT =2000 
BACKUP_ALL_CHAT_LIMIT =10 

def safe_backup_filename (name :str )->str :
    name =re .sub (r"[\\/:*?\"<>|\n\r\t]+","_",str (name or "chat")).strip (" ._")
    name =re .sub (r"\s+"," ",name )
    return (name or "chat")[:70 ]

def backup_chat_title (chat )->str :
    if not chat :
        return "Chat"
    title =getattr (chat ,"title",None )
    if title :
        return title 
    first =getattr (chat ,"first_name","")or ""
    last =getattr (chat ,"last_name","")or ""
    name =f"{first } {last }".strip ()
    if name :
        return name 
    username =getattr (chat ,"username",None )
    if username :
        return f"@{username }"
    return str (getattr (chat ,"id","Chat"))

def message_sender_name (msg ,self_id :int )->str :
    try :
        if getattr (msg ,"from_user",None ):
            u =msg .from_user 
            if u .id ==self_id :
                return "من"
            full =f"{u .first_name or ''} {u .last_name or ''}".strip ()
            return full or (f"@{u .username }"if u .username else str (u .id ))
        if getattr (msg ,"sender_chat",None ):
            return msg .sender_chat .title or str (msg .sender_chat .id )
    except Exception :
        pass 
    return "ناشناس"

def message_media_label (msg )->str :
    labels =[]
    if getattr (msg ,"photo",None ):labels .append ("🖼 عکس")
    if getattr (msg ,"video",None ):labels .append ("🎬 ویدیو")
    if getattr (msg ,"animation",None ):labels .append ("🎞 گیف")
    if getattr (msg ,"voice",None ):labels .append ("🎙 ویس")
    if getattr (msg ,"audio",None ):labels .append ("🎵 آهنگ")
    if getattr (msg ,"document",None ):
        fn =getattr (msg .document ,"file_name","")or "فایل"
        labels .append (f"📎 فایل: {fn }")
    if getattr (msg ,"sticker",None ):
        emoji =getattr (msg .sticker ,"emoji","")or ""
        labels .append (f"🏷 استیکر {emoji }".strip ())
    if getattr (msg ,"location",None ):labels .append ("📍 لوکیشن")
    if getattr (msg ,"contact",None ):labels .append ("👤 مخاطب")
    if getattr (msg ,"poll",None ):labels .append ("📊 نظرسنجی")
    if getattr (msg ,"venue",None ):labels .append ("📌 مکان")
    return " | ".join (labels )

def build_backup_html (chat_title :str ,messages :list ,self_id :int ,exported_at :datetime )->str :
    esc_title =html .escape (chat_title )
    exported_text =html .escape (exported_at .strftime ("%Y/%m/%d - %H:%M:%S"))
    count_text =fa_digits (len (messages ))if 'fa_digits'in globals ()else str (len (messages ))
    parts =[f'''<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc_title }.html</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;font-family:Tahoma,Arial,sans-serif;background:linear-gradient(135deg,#101827,#1d2b4f 45%,#16213e);color:#eaf0ff}}
.header{{position:sticky;top:0;z-index:2;background:rgba(17,24,39,.92);backdrop-filter:blur(10px);padding:18px 20px;border-bottom:1px solid rgba(255,255,255,.09)}}
.brand{{font-weight:900;letter-spacing:2px;color:#7dd3fc;font-size:13px}}.title{{font-size:22px;font-weight:800;margin-top:6px}}.meta{{margin-top:8px;color:#b7c5df;font-size:12px;line-height:1.9}}
.chat{{max-width:920px;margin:0 auto;padding:22px 12px 40px;background:radial-gradient(circle at top left,rgba(125,211,252,.10),transparent 28%)}}
.day{{display:table;margin:14px auto 22px;padding:7px 14px;border-radius:999px;background:rgba(15,23,42,.72);color:#dbeafe;font-size:12px;border:1px solid rgba(255,255,255,.08)}}
.row{{display:flex;margin:8px 0;align-items:flex-end}}.row.out{{justify-content:flex-start}}.row.in{{justify-content:flex-end}}
.bubble{{max-width:min(76%,680px);padding:9px 12px 7px;border-radius:18px;box-shadow:0 8px 22px rgba(0,0,0,.16);line-height:1.9;white-space:pre-wrap;word-wrap:break-word;position:relative}}
.in .bubble{{background:#253044;border-bottom-right-radius:6px;color:#eef4ff}}.out .bubble{{background:linear-gradient(135deg,#1f9d67,#15803d);border-bottom-left-radius:6px;color:white}}
.sender{{font-size:12px;font-weight:800;margin-bottom:3px;color:#93c5fd}}.out .sender{{color:#d1fae5}}
.media{{margin:5px 0 7px;padding:10px 12px;border-radius:14px;background:rgba(0,0,0,.18);border:1px solid rgba(255,255,255,.10);font-weight:700}}
.time{{display:block;text-align:left;font-size:11px;opacity:.72;margin-top:3px;direction:ltr}}.empty{{opacity:.75;font-style:italic}}
.footer{{text-align:center;color:#9fb0cc;font-size:12px;margin-top:30px}}
</style>
</head>
<body>
<div class="header"><div class="brand">DARKSELF BACKUP</div><div class="title">{esc_title }</div><div class="meta">تعداد پیام‌ها: {count_text }<br>زمان بکاپ: {exported_text } Asia/Tehran</div></div>
<div class="chat">''']
    last_day =None 
    for msg in messages :
        try :
            dt =msg .date 
            if dt and dt .tzinfo is None :
                dt =dt .replace (tzinfo =ZoneInfo ("UTC")).astimezone (TEHRAN_TIMEZONE )
            elif dt :
                dt =dt .astimezone (TEHRAN_TIMEZONE )
        except Exception :
            dt =None 
        day_key =dt .strftime ("%Y-%m-%d")if dt else "unknown"
        if day_key !=last_day :
            last_day =day_key 
            day_text =dt .strftime ("%Y/%m/%d")if dt else "بدون تاریخ"
            day_text =fa_digits (day_text )if 'fa_digits'in globals ()else day_text 
            parts .append (f'<div class="day">{html .escape (day_text )}</div>')
        is_out =bool (getattr (msg ,"outgoing",False )or (getattr (msg ,"from_user",None )and msg .from_user .id ==self_id ))
        cls ="out"if is_out else "in"
        sender =html .escape (message_sender_name (msg ,self_id ))
        text =getattr (msg ,"text",None )or getattr (msg ,"caption",None )or ""
        text =html .escape (text )
        media =html .escape (message_media_label (msg ))
        time_s =dt .strftime ("%H:%M")if dt else "--:--"
        time_s =fa_digits (time_s )if 'fa_digits'in globals ()else time_s 
        parts .append (f'<div class="row {cls }"><div class="bubble"><div class="sender">{sender }</div>')
        if media :
            parts .append (f'<div class="media">{media }</div>')
        if text :
            parts .append (text )
        elif not media :
            parts .append ('<span class="empty">پیام بدون متن</span>')
        parts .append (f'<span class="time">{html .escape (time_s )}</span></div></div>')
    parts .append ('<div class="footer">Backup generated by DARKSELF</div></div></body></html>')
    return "".join (parts )

async def create_chat_backup_file (client ,chat_id ,limit :int =BACKUP_MESSAGE_LIMIT ):
    chat =await client .get_chat (chat_id )
    title =backup_chat_title (chat )
    msgs =[]
    async for msg in client .get_chat_history (chat_id ,limit =limit ):
        msgs .append (msg )
        if len (msgs )%250 ==0 :
            await asyncio .sleep (0.05 )
    msgs .reverse ()
    now =datetime .now (TEHRAN_TIMEZONE )
    html_text =build_backup_html (title ,msgs ,client .me .id ,now )
    fname =f"{safe_backup_filename (title )}_{now .strftime ('%Y%m%d_%H%M%S')}.html"
    fpath =os .path .join ("/tmp",fname )
    def _write ():
        with open (fpath ,"w",encoding ="utf-8")as f :
            f .write (html_text )
    await asyncio .get_event_loop ().run_in_executor (cpu_executor ,_write )
    return fpath ,title ,len (msgs )

async def backup_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )
    if not cmd :
        return 
    cmd_l =cmd .strip ().lower ()

    if cmd_l in ("بکاپ","backup"):
        status =None 
        try :
            status =await safe_edit_message (message ,"**در حال گرفتن بکاپ سبک از این چت...**")
            fpath ,title ,count =await create_chat_backup_file (client ,message .chat .id ,BACKUP_MESSAGE_LIMIT )
            await client .send_document ("me",fpath ,caption =f"بکاپ چت: {title }\nتعداد پیام: {count }\nفایل HTML آماده است.")
            try :os .remove (fpath )
            except Exception :pass 
            await status .edit_text ("**بکاپ این چت ساخته شد و به پیام‌های ذخیره‌شده ارسال شد.**")
        except Exception as e :
            try :
                target =status or message 
                await target .edit_text (f"**بکاپ انجام نشد:**\n`{str (e )[:120 ]}`")
            except Exception :
                pass 
        return 

    if cmd_l in ("بکاپ کل","backup all"):
        status =None 
        try :
            status =await safe_edit_message (message ,f"**شروع بکاپ کل از {BACKUP_ALL_CHAT_LIMIT } چت آخر...**")
            chats =[]
            async for d in client .get_dialogs (limit =80 ):
                c =d .chat 
                if not c or getattr (c ,"id",None )==uid :
                    continue 
                if getattr (c ,"type",None )==ChatType .PRIVATE :
                    if getattr (c ,"is_bot",False ):
                        continue 
                    chats .append (c )
                if len (chats )>=BACKUP_ALL_CHAT_LIMIT :
                    break 

            if not chats :
                return await status .edit_text ("**چت خصوصی برای بکاپ پیدا نشد.**")

            done =0 
            for c in chats :
                try :
                    await status .edit_text (f"**در حال بکاپ:** `{backup_chat_title (c )}`\n{done }/{len (chats )}")
                    fpath ,title ,count =await create_chat_backup_file (client ,c .id ,BACKUP_MESSAGE_LIMIT )
                    await client .send_document ("me",fpath ,caption =f"بکاپ چت: {title }\nتعداد پیام: {count }\nفایل HTML آماده است.")
                    try :os .remove (fpath )
                    except Exception :pass 
                    done +=1 
                    await asyncio .sleep (1.0 )
                except FloodWait as fw :
                    await asyncio .sleep (fw .value +2 )
                except Exception :
                    continue 
            await status .edit_text (f"**بکاپ کل تمام شد.**\nتعداد فایل‌های ارسال‌شده: `{done }`")
        except Exception as e :
            try :
                target =status or message 
                await target .edit_text (f"**بکاپ کل انجام نشد:**\n`{str (e )[:120 ]}`")
            except Exception :
                pass 
        return 

async def ping_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    try :
        t0 =time .perf_counter ()
        try :
            await client .invoke (functions .Ping (ping_id =random .getrandbits (63 )))
        except Exception :
            await asyncio .sleep (0 )
        ping_ms =round ((time .perf_counter ()-t0 )*1000 )
        txt =(
        "╔═══════ ✦ 𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 ✦ ═══════╗\n"
        "              PING\n"
        "╚══════════════════════════════╝\n\n"
        f"◉  `{ping_ms }ms`"
        )
        await safe_edit_message (message ,txt )
    except Exception :pass 

async def translate_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    rm =await ensure_reply_message (client ,message )
    if not rm :
        await safe_edit_message (message ,"**روی پیام مورد نظر برای ترجمه ریپلای کنید.**")
        return 
    text_to_translate =rm .text or rm .caption 
    if not text_to_translate :return await safe_edit_message (message ,"**پیام انتخاب‌شده فاقد متن است.**")

    m =await safe_edit_message (message ,"**در حال ترجمه...**")
    translated =await translate_text (text_to_translate ,'fa')
    if translated and translated !=text_to_translate :
        await m .edit_text (f"**ترجمه:**\n`{translated }`")
    else :
        await m .edit_text ("**ترجمه انجام نشد.**")

async def gif_converter_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    rm =await ensure_reply_message (client ,message )
    if not rm or not getattr (rm ,"video",None ):
        return await safe_edit_message (message ,"**روی یک ویدیو ریپلای کنید.**")

    vid =rm .video 
    if vid .duration and vid .duration >20 :
        return await safe_edit_message (message ,"**مدت ویدیو باید کمتر از ۲۰ ثانیه باشد.**")

    size =get_media_file_size (rm ,"video")
    if size and size >DIRECT_DOWNLOAD_MAX_MB *1024 *1024 :
        return await safe_edit_message (message ,f"**حجم ویدیو بالاست. سقف تبدیل `{DIRECT_DOWNLOAD_MAX_MB }MB` است.**")
    m =await safe_edit_message (message ,"**در حال تبدیل ویدیو به گیف...**")
    try :
        file_path =await rm .download (file_name =ensure_download_temp_dir ()+os .sep )
        if file_path :
            await client .send_animation (message .chat .id ,animation =file_path ,reply_to_message_id =rm .id )
            await m .delete ()
            os .remove (file_path )
        else :
            await m .edit_text ("**دانلود فایل انجام نشد.**")
    except Exception :
        await m .edit_text ("**تبدیل ویدیو به گیف انجام نشد.**")

def _sticker_sender_name (msg ):
    sender =getattr (msg ,"from_user",None )
    if sender is not None :
        name =" ".join (part .strip ()for part in (
        getattr (sender ,"first_name",None ),getattr (sender ,"last_name",None ))if part and part .strip ())
        return name or getattr (sender ,"username",None )or "کاربر"
    chat =getattr (msg ,"sender_chat",None )
    return getattr (chat ,"title",None )or "کاربر"

def _render_sticker_quote (text ,sender_name ,time_str ,avatar_path ):
    import unicodedata
    from PIL import features
    has_raqm =bool (features .check ("raqm"))
    raw_text =unicodedata .normalize ("NFC",str (text )).replace ("\r\n","\n").replace ("\r","\n")
    raw_name =unicodedata .normalize ("NFC",str (sender_name ))
    if not has_raqm and any (unicodedata .bidirectional (c )in ("R","AL")for c in raw_text +raw_name )and (arabic_reshaper is None or get_display is None ):
        raise RuntimeError ("Persian stickers require Pillow RAQM or arabic-reshaper and python-bidi")
    engine =getattr (getattr (ImageFont ,"Layout",None ),"RAQM"if has_raqm else "BASIC",1 if has_raqm else 0 )
    font_paths =[
    os .path .join (os .path .dirname (os .path .abspath (__file__ )),"fonts","Vazirmatn-Regular.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    os .path .join (os .environ .get ("WINDIR","C:/Windows"),"Fonts","arial.ttf"),
    "DejaVuSans.ttf","arial.ttf"
    ]
    font_path =None
    for candidate in font_paths :
        try :
            ImageFont .truetype (candidate ,24 ,layout_engine =engine )
            font_path =candidate
            break
        except (OSError ,ValueError ):continue
    if font_path is None :
        raise RuntimeError ("No Persian-capable sticker font found; install DejaVu Sans or supply fonts/Vazirmatn-Regular.ttf")

    probe =Image .new ("RGBA",(1 ,1 ))
    measure =ImageDraw .Draw (probe )
    max_width =350

    def direction (value ):
        for c in value :
            bidi =unicodedata .bidirectional (c )
            if bidi in ("R","AL"):return "rtl"
            if bidi =="L":return "ltr"
        return "rtl"

    def shaped (value ,base ):
        if has_raqm :
            return value ,{"direction":base ,"language":"fa"if base =="rtl"else "en"}
        if arabic_reshaper is not None and get_display is not None :
            return get_display (arabic_reshaper .reshape (value ),base_dir ="R"if base =="rtl"else "L"),{}
        return value ,{}

    def bounds (value ,font ,base ):
        visual ,options =shaped (value ,base )
        box =measure .textbbox ((0 ,0 ),visual ,font =font ,**options )
        return visual ,options ,box

    def width (value ,font ,base ):
        box =bounds (value ,font ,base )[2 ]
        return box [2 ]-box [0 ]

    def clusters (value ):
        result =[]
        for c in value :
            if result and (unicodedata .category (c )in ("Mn","Mc","Me")or c in ("\u200c","\u200d")or result [-1 ].endswith ("\u200d")):
                result [-1 ]+=c
            else :result .append (c )
        return result

    def wrap (value ,font ):
        rows =[]
        for paragraph in value .split ("\n"):
            base =direction (paragraph )
            line =""
            for word in paragraph .split ():
                candidate =(line +" "+word )if line else word
                if width (candidate ,font ,base )<=max_width :
                    line =candidate
                    continue
                if line :rows .append ((line ,base ))
                line =""
                for cluster in clusters (word ):
                    if line and width (line +cluster ,font ,base )>max_width :
                        rows .append ((line ,base ))
                        line =""
                    line +=cluster
                    if width (line ,font ,base )>max_width :
                        raise ValueError ("A sticker glyph exceeds the available width")
            rows .append ((line ,base ))
        return rows

    def layout_rows (rows ,font ,colour ):
        ascent ,descent =font .getmetrics ()
        result =[]
        for value ,base in rows :
            visual ,options ,box =bounds (value ,font ,base )
            height =max (ascent +descent ,box [3 ]-box [1 ])
            result .append ((visual ,options ,box ,height ,base ,font ,colour ))
        return result

    chosen =None
    try :
        for size in range (28 ,13 ,-1 ):
            body_font =ImageFont .truetype (font_path ,size ,layout_engine =engine )
            name_font =ImageFont .truetype (font_path ,max (14 ,size -4 ),layout_engine =engine )
            name_rows =layout_rows (wrap (raw_name ,name_font ),name_font ,"#69d6c8")
            text_rows =layout_rows (wrap (raw_text ,body_font ),body_font ,"#ffffff")
            bubble_h =18 +sum (r [3 ]+4 for r in name_rows )+9 +sum (r [3 ]+4 for r in text_rows )+30
            if bubble_h <=480 :
                chosen =(name_rows ,text_rows ,bubble_h )
                break
    finally :
        probe .close ()
    if chosen is None :
        raise ValueError ("Quote is too long for one readable 512px sticker; use a shorter message")
    name_rows ,text_rows ,bubble_h =chosen
    height =max (128 ,bubble_h +32 )
    img =Image .new ("RGBA",(512 ,height ),(0 ,0 ,0 ,0 ))
    try :
        draw =ImageDraw .Draw (img )
        bx ,by ,right =98 ,16 ,494
        draw .rounded_rectangle ((bx ,by ,right ,by +bubble_h ),radius =22 ,fill ="#292234")
        draw .polygon ([(bx +5 ,by +bubble_h -23 ),(bx -14 ,by +bubble_h ),(bx +24 ,by +bubble_h )],fill ="#292234")
        avatar_y =max (16 ,by +bubble_h -70 )
        draw .ellipse ((14 ,avatar_y ,84 ,avatar_y +70 ),fill ="#4dc5b7")
        if avatar_path and os .path .isfile (avatar_path ):
            try :
                from PIL import ImageOps
                with Image .open (avatar_path )as original :
                    with original .convert ("RGBA")as rgba :
                        with ImageOps .fit (rgba ,(70 ,70 ))as avatar :
                            with Image .new ("L",(70 ,70 ),0 )as mask :
                                ImageDraw .Draw (mask ).ellipse ((0 ,0 ,69 ,69 ),fill =255 )
                                img .paste (avatar ,(14 ,avatar_y ),mask )
            except (OSError ,ValueError ):pass
        y =by +18
        for index ,rows in enumerate ((name_rows ,text_rows )):
            if index :y +=9
            for visual ,options ,box ,line_h ,base ,font ,colour in rows :
                x =(right -23 -box [2 ])if base =="rtl"else (bx +23 -box [0 ])
                draw .text ((x ,y -box [1 ]),visual ,font =font ,fill =colour ,**options )
                y +=line_h +4
        clock_font =ImageFont .truetype (font_path ,13 ,layout_engine =engine )
        clock_options ={"direction":"ltr"}if has_raqm else {}
        box =draw .textbbox ((0 ,0 ),str (time_str ),font =clock_font ,**clock_options )
        draw .text ((right -23 -box [2 ],by +bubble_h -22 -box [1 ]),str (time_str ),font =clock_font ,fill ="#a99daf",**clock_options )
        return img
    except Exception :
        img .close ()
        raise

def _sticker_lanczos ():
    return getattr (getattr (Image ,"Resampling",Image ),"LANCZOS",getattr (Image ,"LANCZOS",1 ))

def _fit_telegram_sticker (img ):
    if img .mode =="P":
        img =img .convert ("RGBA")
    elif img .mode =="LA":
        img =img .convert ("RGBA")
    elif img .mode !="RGBA":
        img =img .convert ("RGBA")
    try :
        img .load ()
    except Exception :
        pass 
    w ,h =img .size 
    if w <1 or h <1 :
        raise ValueError ("empty image")
    if w >=h :
        nw ,nh =512 ,max (1 ,min (512 ,int (round (h *512.0 /w ))))
    else :
        nh ,nw =512 ,max (1 ,min (512 ,int (round (w *512.0 /h ))))
    if (w ,h )!=(nw ,nh ):
        img =img .resize ((nw ,nh ),_sticker_lanczos ())
    return img 

def _simple_sticker_quote (text ,sender_name ,time_str ):
    img =Image .new ("RGBA",(512 ,512 ),(0 ,0 ,0 ,0 ))
    draw =ImageDraw .Draw (img )
    try :
        draw .rounded_rectangle ((36 ,96 ,476 ,430 ),radius =26 ,fill =(41 ,34 ,52 ,255 ))
    except Exception :
        draw .rectangle ((36 ,96 ,476 ,430 ),fill =(41 ,34 ,52 ,255 ))
    font =ImageFont .load_default ()
    for candidate in (
    os .path .join (os .path .dirname (os .path .abspath (__file__ )),"fonts","Vazirmatn-Regular.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "DejaVuSans.ttf",
    ):
        try :
            if candidate and (os .path .isfile (candidate )or candidate .endswith (".ttf")):
                font =ImageFont .truetype (candidate ,26 )
                break 
        except Exception :
            continue 
    body =(str (sender_name or "کاربر")+"\n"+str (text or "")).strip ()
    if arabic_reshaper is not None and get_display is not None :
        try :
            body =get_display (arabic_reshaper .reshape (body ))
        except Exception :
            pass 
    y =114 
    line =""
    for word in body .replace ("\n"," \n ").split (" "):
        if word =="\n":
            if line :
                draw .text ((56 ,y ),line ,font =font ,fill =(255 ,255 ,255 ,255 ))
                y +=34 
                line =""
            continue 
        trial =(line +" "+word ).strip ()
        try :
            box =draw .textbbox ((0 ,0 ),trial ,font =font )
            too_wide =(box [2 ]-box [0 ])>380 
        except Exception :
            too_wide =len (trial )>22 
        if too_wide and line :
            draw .text ((56 ,y ),line ,font =font ,fill =(255 ,255 ,255 ,255 ))
            y +=34 
            line =word 
            if y >390 :
                break 
        else :
            line =trial 
    if line and y <=390 :
        draw .text ((56 ,y ),line ,font =font ,fill =(255 ,255 ,255 ,255 ))
    try :
        draw .text ((56 ,400 ),str (time_str or ""),font =font ,fill =(169 ,157 ,175 ,255 ))
    except Exception :
        pass 
    return img 

def sync_create_sticker_image (download_path ,text ,sender_name ,time_str ,avatar_path ):
    if Image is None or ImageDraw is None or ImageFont is None :
        return None 
    file_path =os .path .join (tempfile .gettempdir (),f"sticker_{uuid .uuid4 ().hex }.webp")
    try :
        if download_path and os .path .isfile (download_path ):
            img =Image .open (download_path )
            try :
                try :
                    img .seek (0 )
                except Exception :
                    pass 
                img =_fit_telegram_sticker (img )
                img .save (file_path ,"WEBP",quality =90 ,method =4 )
            finally :
                try :
                    img .close ()
                except Exception :
                    pass 
        elif text :
            made =None 
            try :
                made =_render_sticker_quote (text ,sender_name ,time_str ,avatar_path )
                made .save (file_path ,"WEBP",lossless =True )
            except Exception as exc :
                logger .warning ("Quote sticker render fallback: %s: %s",type (exc ).__name__ ,str (exc )[:240 ])
                if made is not None :
                    try :made .close ()
                    except Exception :pass 
                made =_simple_sticker_quote (text ,sender_name ,time_str )
                made .save (file_path ,"WEBP",quality =90 )
            finally :
                if made is not None :
                    try :made .close ()
                    except Exception :pass 
        else :
            return None 
        if os .path .isfile (file_path )and os .path .getsize (file_path )>32 :
            return file_path 
        return None 
    except Exception as exc :
        logger .warning ("Sticker image rendering failed: %s: %s",type (exc ).__name__ ,str (exc )[:300 ])
        try :
            if os .path .isfile (file_path ):
                os .remove (file_path )
        except OSError :
            pass 
        return None 

def _sticker_video_frame (src ):
    out =src +".jpg"
    ffmpeg =shutil .which ("ffmpeg")
    if not ffmpeg :
        try :
            import imageio_ffmpeg 
            ffmpeg =imageio_ffmpeg .get_ffmpeg_exe ()
        except Exception :
            ffmpeg =None 
    if not ffmpeg :
        return None 
    try :
        r =subprocess .run ([ffmpeg ,"-y","-i",src ,"-vframes","1","-q:v","2",out ],
        stdout =subprocess .DEVNULL ,stderr =subprocess .DEVNULL ,timeout =40 )
        if r .returncode ==0 and os .path .isfile (out )and os .path .getsize (out )>32 :
            return out 
    except Exception :
        return None 
    return None 

def _sticker_chat_id (message ,msg ):
    for obj in (message ,msg ):
        chat =getattr (obj ,"chat",None )
        cid =getattr (chat ,"id",None )if chat is not None else None 
        if cid :
            return cid 
        cid =getattr (obj ,"chat_id",None )
        if cid :
            return cid 
    return "me"

async def _sticker_say (message ,status ,text ):
    if status is not None :
        try :
            return await status .edit_text (text )
        except Exception :
            pass 
    try :
        return await message .edit_text (text )
    except Exception :
        pass 
    try :
        return await message .reply_text (text )
    except Exception :
        return status 

async def _sticker_send (client ,chat_id ,path ,reply_to ):
    try :
        return await client .send_sticker (chat_id ,sticker =path ,reply_to_message_id =reply_to )
    except TypeError :
        return await client .send_sticker (chat_id ,path )
    except Exception as exc :
        logger .warning ("send_sticker failed: %s: %s",type (exc ).__name__ ,exc )
        return await client .send_document (chat_id ,document =path ,file_name ="sticker.webp",reply_to_message_id =reply_to )

async def sticker_creator_controller (client ,message ):
    uid =getattr (getattr (client ,"me",None ),"id",None )
    if uid and not await check_global_fjoin_for_user (uid ,message ):
        return 
    msg =await ensure_reply_message (client ,message )
    if not msg :
        return await safe_edit_message (message ,"**روی پیام، عکس یا ویدیو ریپلای کن و بزن استیکر.**")

    status =await safe_edit_message (message ,"**در حال ساخت استیکر...**")
    file_path =None 
    avatar_path =None 
    download_path =None 
    frame_path =None 

    try :
        text_content =(getattr (msg ,"text",None )or getattr (msg ,"caption",None )or "")or None 
        sender_name =_sticker_sender_name (msg )
        date =getattr (msg ,"date",None )
        try :
            time_str =date .strftime ("%H:%M")if date is not None and hasattr (date ,"strftime")else datetime .now ().strftime ("%H:%M")
        except Exception :
            time_str =datetime .now ().strftime ("%H:%M")

        media_kind =None 
        for attr in ("photo","sticker","animation","video","video_note","document"):
            if getattr (msg ,attr ,None ):
                media_kind =attr 
                break 

        chat_id =_sticker_chat_id (message ,msg )
        reply_to =getattr (msg ,"id",None )

        if media_kind =="sticker":
            stk =msg .sticker 
            animated =bool (getattr (stk ,"is_animated",False )or getattr (stk ,"is_video",False ))
            file_id =getattr (stk ,"file_id",None )
            if file_id and not animated :
                try :
                    await client .send_sticker (chat_id ,sticker =file_id ,reply_to_message_id =reply_to )
                    if status is not None :
                        try :await status .delete ()
                        except Exception :pass 
                    else :
                        try :await message .delete ()
                        except Exception :pass 
                    return 
                except Exception as exc :
                    logger .warning ("resend sticker file_id failed: %s",exc )

        if media_kind :
            size =get_media_file_size (msg ,media_kind if media_kind in ("photo","document","video","animation")else None )
            if size and size >STICKER_SOURCE_MAX_MB *1024 *1024 :
                return await _sticker_say (message ,status ,f"**حجم فایل برای استیکر بالاست. سقف `{STICKER_SOURCE_MAX_MB }MB` است.**")
            try :
                download_path =await client .download_media (msg ,file_name =ensure_download_temp_dir ()+os .sep )
            except Exception as exc :
                logger .warning ("sticker download failed: %s: %s",type (exc ).__name__ ,exc )
                download_path =None 
            low =(download_path or "").lower ()
            if download_path and low .endswith ((".tgs",".webm")):
                await _sticker_send (client ,chat_id ,download_path ,reply_to )
                if status is not None :
                    try :await status .delete ()
                    except Exception :pass 
                return 
            if media_kind in ("video","animation","video_note")and download_path :
                frame_path =await asyncio .get_event_loop ().run_in_executor (cpu_executor ,_sticker_video_frame ,download_path )
                if frame_path :
                    download_path =frame_path 
        elif text_content :
            photo =getattr (getattr (msg ,"from_user",None ),"photo",None )
            file_id =getattr (photo ,"small_file_id",None )or getattr (photo ,"big_file_id",None )
            if file_id :
                try :
                    avatar_path =await client .download_media (file_id )
                except Exception :
                    pass 

        if not download_path and not text_content :
            return await _sticker_say (message ,status ,"**این پیام قابل تبدیل به استیکر نیست.**")

        if Image is None or ImageDraw is None or ImageFont is None :
            if download_path and download_path .lower ().endswith (".webp"):
                await _sticker_send (client ,chat_id ,download_path ,reply_to )
                if status is not None :
                    try :await status .delete ()
                    except Exception :pass 
                return 
            return await _sticker_say (message ,status ,"**ساخت استیکر موقتاً در دسترس نیست.**")

        loop =asyncio .get_event_loop ()
        file_path =await loop .run_in_executor (
        cpu_executor ,
        sync_create_sticker_image ,
        download_path ,text_content if not download_path else None ,sender_name ,time_str ,avatar_path 
        )

        if file_path and os .path .exists (file_path ):
            await _sticker_send (client ,chat_id ,file_path ,reply_to )
            if status is not None :
                try :await status .delete ()
                except Exception :pass 
            else :
                try :await message .delete ()
                except Exception :pass 
            try :os .remove (file_path )
            except OSError :pass 
            file_path =None 
        else :
            await _sticker_say (message ,status ,"**ساخت استیکر انجام نشد.**")
    except Exception as e :
        logger .warning ("Sticker creation failed: %s: %s",type (e ).__name__ ,e )
        await _sticker_say (message ,status ,"**ساخت استیکر انجام نشد.**")
    finally :
        for path in (download_path ,avatar_path ,frame_path ,file_path ):
            if path and os .path .exists (path ):
                try :os .remove (path )
                except Exception :pass 

async def _collect_profile_photo_ids (client ):
    me_id =client .me .id 
    ids =[]
    async for p in client .get_chat_photos (me_id ):
        pid =getattr (p ,"file_id",None )
        if pid :ids .append (pid )
    return ids 

async def _delete_last_profile_photo (client ):
    me_id =client .me .id 
    photos =[p async for p in client .get_chat_photos (me_id ,limit =1 )]
    if not photos :return False ,"**عکسی در پروفایل موجود نیست.**"
    last_photo_id =getattr (photos [0 ],"file_id",None )
    if not last_photo_id :return False ,"**شناسه عکس پروفایل دریافت نشد.**"
    await client .delete_profile_photos ([last_photo_id ])
    return True ,"**آخرین عکس پروفایل حذف شد.**"

async def _delete_all_profile_photos (client ):
    deleted =0 
    while True :
        ids =await _collect_profile_photo_ids (client )
        if not ids :break 
        for i in range (0 ,len (ids ),50 ):
            batch =ids [i :i +50 ]
            await client .delete_profile_photos (batch )
            deleted +=len (batch )
    if not deleted :return False ,"**عکسی در پروفایل موجود نیست.**"
    return True ,f"**{deleted } عکس پروفایل حذف شد.**"

async def _find_chat_by_target (client ,kind ,target ):
    normalized_target =target .casefold ().strip ()

    if target .startswith ("@")or target .lstrip ("-").isdigit ():
        try :
            peer =target if not target .lstrip ("-").isdigit ()else int (target )
            got =await client .get_chat (peer )
            ctype =getattr (got ,"type",None )
            if kind =="کانال"and ctype ==ChatType .CHANNEL :return got 
            if kind =="گروه"and ctype in (ChatType .GROUP ,ChatType .SUPERGROUP ):return got 
        except Exception :
            pass 

    fallback_match =None 
    async for d in client .get_dialogs (limit =200 ):
        c =d .chat 
        if not c :continue 
        ctype =getattr (c ,"type",None )
        is_kind_ok =((kind =="کانال"and ctype ==ChatType .CHANNEL )or (kind =="گروه"and ctype in (ChatType .GROUP ,ChatType .SUPERGROUP )))
        if not is_kind_ok :continue 

        title =(getattr (c ,"title","")or "").strip ()
        uname =(getattr (c ,"username","")or "").strip ()
        normalized_title =title .casefold ()
        normalized_uname =uname .casefold ()

        if normalized_title ==normalized_target or normalized_uname ==normalized_target .lstrip ("@"):return c 
        if fallback_match is None and (normalized_target in normalized_title or normalized_target .lstrip ("@")in normalized_uname ):fallback_match =c 

    return fallback_match 

async def _delete_owned_chat (client ,chat_obj ):
    cid =chat_obj .id 
    ctype =getattr (chat_obj ,"type",None )
    if ctype ==ChatType .CHANNEL :
        await client .delete_channel (cid )
        return 
    if ctype in (ChatType .SUPERGROUP ,ChatType .GROUP ):
        try :
            await client .delete_supergroup (cid )
            return 
        except Exception :
            try :
                await client .delete_channel (cid )
                return 
            except Exception :
                if ctype ==ChatType .GROUP :
                    try :
                        await client .invoke (functions .messages .DeleteChat (chat_id =abs (cid )))
                        return 
                    except Exception :
                        await client .leave_chat (cid )
                        return 
                raise 
    raise ValueError ("نوع چت پشتیبانی نمی‌شود.")

async def manage_account_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )

    m =re .match (r"^تنظیم نام اکانت(?:\s+)(.+)$",cmd ,re .DOTALL )
    if m :
        name =m .group (1 ).strip ()[:64 ]
        try :
            await client .update_profile (first_name =name )
            await safe_edit_message (message ,f"**نام اکانت تنظیم شد.**:\n`{name }`")
        except Exception as e :
            await safe_edit_message (message ,f"⚠️ خطا: {e }")
        return 

    m =re .match (r"^تنظیم نام خانوادگی(?: اکانت)?(?:\s+)(.+)$",cmd ,re .DOTALL )
    if m :
        last =m .group (1 ).strip ()[:64 ]
        try :
            await client .update_profile (last_name =last )
            await safe_edit_message (message ,"**نام خانوادگی اکانت تنظیم شد.**")
        except Exception as e :
            await safe_edit_message (message ,f"⚠️ خطا: {e }")
        return 

    if cmd =="تنظیم عکس":
        if not message .reply_to_message or not (message .reply_to_message .photo or message .reply_to_message .document ):
            return await safe_edit_message (message ,"**روی یک عکس ریپلای کنید.**")
        await safe_edit_message (message ,"**در حال تنظیم عکس پروفایل...**")
        try :
            f_path =await message .reply_to_message .download ()
            if f_path :
                await client .set_profile_photo (photo =f_path )
                try :os .remove (f_path )
                except Exception :pass 
                await safe_edit_message (message ,"**عکس پروفایل تنظیم شد.**")
            else :
                await safe_edit_message (message ,"**دانلود عکس انجام نشد.**")
        except Exception as e :
            await safe_edit_message (message ,f"⚠️ خطا: {e }")
        return 

    if cmd in ("حذف عکس پروفایل","حذف عکس پروفایل آخر","حذف اخرین عکس پروفایل"):
        await safe_edit_message (message ,"**در حال حذف آخرین عکس پروفایل...**")
        try :
            ok ,txt =await _delete_last_profile_photo (client )
            await safe_edit_message (message ,txt )
        except Exception as e :
            await safe_edit_message (message ,f"⚠️ خطا: {e }")
        return 

    if cmd =="حذف تمام عکس پروفایل":
        await safe_edit_message (message ,"**در حال حذف تمام عکس‌های پروفایل...**")
        try :
            ok ,txt =await _delete_all_profile_photos (client )
            await safe_edit_message (message ,txt )
        except Exception as e :
            await safe_edit_message (message ,f"⚠️ خطا: {e }")
        return 

def friendly_telegram_error (e ,action ="عملیات"):
    raw =str (e or "")
    low =raw .lower ()
    if "user_restricted"in low or "limited/restricted"in low or "you are limited"in low :
        return f"**{action } انجام نشد.**\nاکانت شما از طرف تلگرام محدود شده و فعلاً اجازه انجام این کار را ندارد."
    if "user_deactivated"in low or "session_revoked"in low or "auth_key"in low :
        return "**سشن این اکانت معتبر نیست یا از تلگرام خارج شده است.**\nلطفاً دوباره وارد شوید."
    if "chat_admin_required"in low or "admin"in low :
        return f"**{action } انجام نشد.**\nبرای این کار دسترسی ادمین لازم است."
    if "flood"in low :
        return f"**{action } فعلاً محدود شد.**\nچند دقیقه بعد دوباره امتحان کنید."
    if "peer_id_invalid"in low or "channel_private"in low or "channelinvalid"in low :
        return f"**{action } انجام نشد.**\nچت یا کانال موردنظر در دسترس نیست."
    if "chat_send_photos_forbidden"in low :
        return f"**{action } انجام نشد.**\nارسال عکس در این چت توسط ادمین گروه محدود شده است."
    if "chat_send_gifs_forbidden"in low :
        return f"**{action } انجام نشد.**\nارسال گیف در این چت توسط ادمین گروه محدود شده است."
    if "chat_send_media_forbidden"in low or "chat_send_stickers_forbidden"in low :
        return f"**{action } انجام نشد.**\nارسال این نوع رسانه در این چت محدود شده است."
    if "chat_write_forbidden"in low :
        return f"**{action } انجام نشد.**\nاجازه ارسال پیام در این چت وجود ندارد."
    return f"**{action } انجام نشد.**\nلطفاً شرایط اکانت و دسترسی‌ها را بررسی کنید."

async def create_delete_controller (client ,message ):

    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )
    if cmd and cmd .startswith (("ساخت","حذف گروه","حذف کانال")):
        logger .warning ("CHAT-CREATE CMD uid=%s text=%r stack=%s",uid ,getattr (message ,"text",None ),"".join (traceback .format_stack ()[-6 :-1 ]))

    m =re .match (r"^ساخت گروه(?:\s+)(.+)$",cmd ,re .DOTALL )
    if m :
        title =m .group (1 ).strip ()[:128 ]
        await safe_edit_message (message ,"**در حال ساخت گروه...**")
        try :
            chat =await client .create_supergroup (title )
            link =None 
            try :link =await client .export_chat_invite_link (chat .id )
            except Exception :pass 
            txt =f"**گروه ساخته شد.**\n`{chat .id }`"
            if link :txt +=f"\n{link }"
            await safe_edit_message (message ,txt )
        except Exception as e :
            await safe_edit_message (message ,friendly_telegram_error (e ,"ساخت گروه"))
        return 

    m =re .match (r"^ساخت کانال(?:\s+)(.+)$",cmd ,re .DOTALL )
    if m :
        title =m .group (1 ).strip ()[:128 ]
        await safe_edit_message (message ,"**در حال ساخت کانال...**")
        try :
            chat =await client .create_channel (title )
            link =None 
            try :link =await client .export_chat_invite_link (chat .id )
            except Exception :pass 
            txt =f"**کانال ساخته شد.**\n`{chat .id }`"
            if link :txt +=f"\n{link }"
            await safe_edit_message (message ,txt )
        except Exception as e :
            await safe_edit_message (message ,friendly_telegram_error (e ,"ساخت کانال"))
        return 

    m =re .match (r"^حذف (گروه|کانال)(?:\s+)(.+)$",cmd ,re .DOTALL )
    if m :
        kind ,target =m .group (1 ),m .group (2 ).strip ()
        if not target :
            return await safe_edit_message (message ,f"**فرمت صحیح:**\n`حذف {kind } [اسم/یوزرنیم/آیدی]`")
        await safe_edit_message (message ,f"**در حال بررسی و حذف {kind }...**")
        try :chat_obj =await _find_chat_by_target (client ,kind ,target )
        except Exception :chat_obj =None 
        if chat_obj is None :
            return await safe_edit_message (message ,f"**{kind } مورد نظر پیدا نشد.**")
        try :
            await _delete_owned_chat (client ,chat_obj )
            await safe_edit_message (message ,"**چت مورد نظر حذف شد.**")
        except Exception as e :
            await safe_edit_message (message ,friendly_telegram_error (e ,f"حذف {kind }")+"\n`برای حذف باید مالک باشید.`")
        return 

async def tag_alert_handler (client ,message ):
    uid =client .me .id 
    if not SELF_ACTIVE_STATUS .get (uid ,True ):return 
    if not TAG_ALERT_STATUS .get (uid ,False ):return 
    if not message .from_user or message .from_user .id ==uid :return 
    try :
        if message .reply_to_message and not message .entities and not message .caption_entities :return 

        tagged =False 
        full_text =(message .text or message .caption or "")
        entities =list (message .entities or [])+list (message .caption_entities or [])
        my_username =(client .me .username or "").lower ()

        for ent in entities :
            ent_type =str (getattr (ent ,"type","")).lower ()
            if getattr (ent ,"user",None )and ent .user .id ==uid :tagged =True ;break 
            if ent_type .endswith ("mention")and my_username :
                try :
                    mention_text =full_text [ent .offset :ent .offset +ent .length ].lower ()
                    if mention_text ==f"@{my_username }":tagged =True ;break 
                except Exception :pass 

        if tagged :
            who =(("@"+message .from_user .username )if getattr (message .from_user ,"username",None )else (message .from_user .first_name or "کاربر"))
            my_username_text =("@"+client .me .username )if getattr (client .me ,"username",None )else str (uid )
            chat_title =message .chat .title if message .chat and message .chat .title else "پیوی"
            link =""
            try :
                if message .chat and getattr (message .chat ,"username",None ):
                    link =f"\n🔗 [https://t.me/](https://t.me/){message .chat .username }/{message .id }"
            except Exception :pass 
            msg_text =(message .text or message .caption or "(بدون متن)")
            await client .send_message (
            "me",
            f"🔔 **هشدار تگ شدن**\n"
            f"👤 {who } شما ({my_username_text }) را منشن کرد.\n"
            f"💬 چت: {chat_title }{link }\n\n"
            f"📝 متن پیام:\n{msg_text }"
            )
    except Exception :
        pass 

async def forced_join_cmds_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 

    cmd =get_cmd (uid ,message .text )

    if cmd .startswith ("تنظیم عضویت اجباری"):
        match =re .match (r"^تنظیم عضویت اجباری\s+(@\w+|\d+|-100\d+)$",cmd )
        if not match :return await safe_edit_message (message ,"**فرمت صحیح:**\n`تنظیم عضویت اجباری @username`")
        chat_target =match .group (1 )

        await safe_edit_message (message ,"**در حال بررسی دسترسی ربات مدیریت...**")
        try :
            chat_info =await manager_bot .get_chat (chat_target )
            member =await manager_bot .get_chat_member (chat_info .id ,"me")

            if member .status in [ChatMemberStatus .ADMINISTRATOR ,ChatMemberStatus .OWNER ]:
                chats =FORCED_JOIN_CHATS .setdefault (uid ,[])
                stored_target =chat_info .username if chat_info .username else chat_info .id 
                stored_target_str =f"@{stored_target }"if chat_info .username else str (stored_target )

                if stored_target_str not in chats :
                    chats .append (stored_target_str )
                    data_manager .update_user_data (uid ,{"forced_join_chats":chats })
                await safe_edit_message (message ,"**کانال یا گروه مورد نظر ثبت شد.**")
            else :
                await safe_edit_message (message ,"**ربات مدیریت در این چت ادمین نیست.**")
        except Exception :
            await safe_edit_message (message ,
            "❌ ربات مدیریت در این کانال/گروه عضو نیست یا ادمین نمی‌باشد!\n\n"
            "💡 **راهنمایی:**\n"
            "۱. ابتدا ربات مدیریت خود را در کانال/گروه عضو کنید.\n"
            "۲. به آن دسترسی **ادمین (Administrator)** با اختیارات لازم بدهید.\n"
            "۳. سپس مجدداً این دستور را ارسال کنید."
            )

    elif cmd .startswith ("حذف عضویت اجباری"):
        match =re .match (r"^حذف عضویت اجباری\s+(@\w+|\d+|-100\d+)$",cmd )
        if not match :return await safe_edit_message (message ,"**فرمت صحیح:**\n`حذف عضویت اجباری @username`")
        chat_target =match .group (1 )

        chats =FORCED_JOIN_CHATS .get (uid ,[])
        if chat_target in chats :
            chats .remove (chat_target )
            data_manager .update_user_data (uid ,{"forced_join_chats":chats })
            await safe_edit_message (message ,"**کانال یا گروه مورد نظر از لیست حذف شد.**")
        else :
            await safe_edit_message (message ,"**این چت در لیست عضویت اجباری شما ثبت نشده است.**")

    elif cmd =="لیست عضویت اجباری":
        chats =FORCED_JOIN_CHATS .get (uid ,[])
        if not chats :return await safe_edit_message (message ,"**لیست عضویت اجباری شما خالی است.**")
        text ="**لیست عضویت اجباری شخصی:**\n\n"
        for idx ,c in enumerate (chats ,1 ):
            text +=f"{idx }. `{c }`\n"
        await safe_edit_message (message ,text )

async def nsfw_controller (client ,message ):
    cmd =message .text .strip ().lower ()
    uid =client .me .id 
    use_dot =DOT_COMMANDS_STATUS .get (uid ,False )
    if use_dot and cmd .startswith ("."):cmd =cmd [1 :].lstrip ()

    try :
        session =await get_http_session ()
        file_path =None 

        if cmd =="boob":
            uptt =await message .reply ("🔎 `Wait...`")
            async with session .get ("http://api.oboobs.ru/boobs/0/1/random")as resp :
                data =await resp .json ()
                nsfw_id =data [0 ]["preview"]
                pic_url =f"http://media.oboobs.ru/{nsfw_id }"

            async with session .get (pic_url )as resp :
                file_path =f"/tmp/boobs_{uuid .uuid4 ().hex }.jpg"
                img_bytes =await resp .read ()
                await asyncio .get_event_loop ().run_in_executor (cpu_executor ,lambda :open (file_path ,"wb").write (img_bytes ))

            await message .reply_photo (file_path ,caption ="**Boobs! 🔞**",reply_to_message_id =message .id )
            await uptt .delete ()

        elif cmd =="butt":
            uptt =await message .reply ("🔎 `Wait...`")
            async with session .get ("http://api.obutts.ru/butts/0/1/random")as resp :
                data =await resp .json ()
                nsfw_id =data [0 ]["preview"]
                pic_url =f"http://media.obutts.ru/{nsfw_id }"

            async with session .get (pic_url )as resp :
                file_path =f"/tmp/butt_{uuid .uuid4 ().hex }.jpg"
                img_bytes =await resp .read ()
                await asyncio .get_event_loop ().run_in_executor (cpu_executor ,lambda :open (file_path ,"wb").write (img_bytes ))

            await message .reply_photo (file_path ,caption ="**Butts! 🔞**",reply_to_message_id =message .id )
            await uptt .delete ()

        elif cmd =="lewd":
            uptt =await message .reply ("🔎 `Loading Lewd...`")
            async with session .get ("https://api.purrbot.site/v2/img/nsfw/neko/gif")as resp :
                data =await resp .json ()
                pic_url =data ["link"]

            async with session .get (pic_url )as resp :
                ext =pic_url .split (".")[-1 ]
                file_path =f"/tmp/lewd_{uuid .uuid4 ().hex }.{ext }"
                with open (file_path ,"wb")as f :f .write (await resp .read ())

            await message .reply_animation (file_path ,caption ="**Here is your Lewd GIF! 🔞**",reply_to_message_id =message .id )
            await uptt .delete ()

        elif cmd =="hentai":
            uptt =await message .reply ("🔎 `Loading Hentai...`")
            async with session .get ("https://api.purrbot.site/v2/img/nsfw/neko/img")as resp :
                data =await resp .json ()
                pic_url =data ["link"]

            async with session .get (pic_url )as resp :
                ext =pic_url .split (".")[-1 ]
                file_path =f"/tmp/hentai_{uuid .uuid4 ().hex }.{ext }"
                with open (file_path ,"wb")as f :f .write (await resp .read ())

            await message .reply_photo (file_path ,caption ="**Hentai Neko 🔞**",reply_to_message_id =message .id )
            await uptt .delete ()

    except Exception as e :
        err =str (e ).lower ()

        if "forbidden"in err :
            try :
                await message .reply_text (friendly_telegram_error (e ,"ارسال محتوا"))
            except Exception :
                pass 
            logger .debug (f"nsfw_controller media send forbidden: {e }")
        else :
            logger .error (f"Error in nsfw_controller: {e }")
    finally :
        if 'file_path'in locals ()and file_path and os .path .exists (file_path ):
            try :os .remove (file_path )
            except Exception :pass 

async def sync_sessions_from_database (reason :str ="database-sync"):
    try :
        sessions =list (data_manager .get_all_sessions ())
        started =0 
        for phone ,s_data in sessions :
            try :
                uid =int (s_data .get ("user_id"))
                is_adm =uid in data_manager .get_admins ()or uid ==ROOT_ADMIN 
                if data_manager .is_banned (uid )or data_manager .is_invalid_session_uid (uid ):
                    continue 

                if not _shard_assigns_to_me (uid ):
                    continue 
                session_string =s_data .get ("string")or s_data .get ("session_string")
                activation_id =data_manager .data .get ("users",{}).get (str (uid ),{}).get ("activation_id")
                active =ACTIVE_BOTS .get (uid )
                if active and activation_id and getattr (active [0 ],"_darkself_activation_id",None )!=activation_id :
                    await stop_user_bot (uid )
                    load_all_states ()
                if not session_string or uid in ACTIVE_BOTS or uid in STARTING_BOTS :
                    continue 
                STARTING_BOTS .add (uid )

                async def boot_one (_uid =uid ,_phone =phone ,_session =session_string ):
                    try :
                        await start_bot_instance (_session ,_phone ,_uid ,'stylized')
                    finally :
                        STARTING_BOTS .discard (_uid )

                asyncio .create_task (boot_one ())
                started +=1 
                await asyncio .sleep (0.15 )
            except Exception as e :
                logger .warning (f"Session sync skip {phone }: {e }")
        if started :
            logger .warning (f"Started {started } newly imported sessions from database backup. reason={reason }")
            try :
                asyncio .create_task (notify_admins (f"{started } سشن جدید از بکاپ دیتابیس شناسایی و وصل شد."))
            except Exception :
                pass 
        return started 
    except Exception as e :
        logger .error (f"Database session sync failed: {e }")
        return 0 

def ensure_tabchi_loops_running (uid ):
    try :
        pair =ACTIVE_BOTS .get (int (uid ))
        if pair :
            c ,tasks =pair 
            has_ctrl =any ("tabchi_controller_loop"in str (getattr (t ,"get_coro",lambda :"")())for t in tasks if not t .done ())
            has_rep =any ("tabchi_repeater_loop"in str (getattr (t ,"get_coro",lambda :"")())for t in tasks if not t .done ())
            if not has_ctrl :
                new_t =asyncio .create_task (tabchi_controller_loop (c ,int (uid )))
                tasks .append (new_t )
                logger .info (f"Dynamically started tabchi_controller_loop for {uid }")
            if not has_rep :
                new_r =asyncio .create_task (tabchi_repeater_loop (c ,int (uid )))
                tasks .append (new_r )
                logger .info (f"Dynamically started tabchi_repeater_loop for {uid }")
    except Exception as e :
        logger .warning (f"ensure_tabchi_loops_running error: {e }")

def _message_timestamp (msg )->float :
    try :
        dt =getattr (msg ,"date",None )
        if not dt :
            return 0.0 
        if getattr (dt ,"tzinfo",None )is None :
            return dt .replace (tzinfo =ZoneInfo ("UTC")).timestamp ()
        return dt .timestamp ()
    except Exception :
        return 0.0 

def _today_start_ts ()->float :
    now =datetime .now (TEHRAN_TIMEZONE )
    return now .replace (hour =0 ,minute =0 ,second =0 ,microsecond =0 ).timestamp ()

def _week_start_ts ()->float :
    return time .time ()-(7 *86400 )

CLEAN_EXIT_MESSAGE_LIMIT =2000 

async def _delete_message_batch_safe (client ,chat_id ,ids ):
    if not ids :
        return 0 
    try :
        await client .delete_messages (chat_id ,list (ids ),revoke =True )
        return len (ids )
    except FloodWait as fw :
        await asyncio .sleep (min (int (fw .value )+2 ,20 ))
        try :
            await client .delete_messages (chat_id ,list (ids ),revoke =True )
            return len (ids )
        except Exception :
            return 0 
    except Exception :
        ok =0 
        for mid in list (ids ):
            try :
                await client .delete_messages (chat_id ,mid ,revoke =True )
                ok +=1 
            except FloodWait as fw :
                await asyncio .sleep (min (int (fw .value )+2 ,20 ))
            except Exception :
                pass 
        return ok 

async def _iter_my_messages (client ,chat_id ,uid :int ,limit :int ):
    got =False 
    try :
        async for msg in client .search_messages (chat_id ,from_user ="me",limit =limit ):
            got =True 
            yield msg 
    except FloodWait as fw :
        await asyncio .sleep (min (int (fw .value )+2 ,20 ))
    except Exception :
        pass 
    if got :
        return 
    try :
        scanned =0 
        async for msg in client .get_chat_history (chat_id ,limit =max (limit *3 ,limit )):
            scanned +=1 
            is_mine =bool (getattr (msg ,"outgoing",False ))
            if not is_mine :
                u =getattr (msg ,"from_user",None )
                if u and getattr (u ,"id",None )==uid :
                    is_mine =True 
            if is_mine :
                yield msg 
            if scanned >=max (limit *3 ,limit ):
                break 
    except FloodWait as fw :
        await asyncio .sleep (min (int (fw .value )+2 ,20 ))
    except Exception :
        pass 

async def _delete_my_messages_in_chat (client ,chat_id ,uid :int ,since_ts :float =None ,max_scan :int =CLEAN_EXIT_MESSAGE_LIMIT ):
    limit =max (1 ,min (int (max_scan or CLEAN_EXIT_MESSAGE_LIMIT ),CLEAN_EXIT_MESSAGE_LIMIT ))
    deleted =0 
    scanned =0 
    batch =[]
    try :
        async for msg in _iter_my_messages (client ,chat_id ,uid ,limit ):
            scanned +=1 
            ts =_message_timestamp (msg )
            if since_ts and ts and ts <since_ts :
                continue 
            batch .append (msg .id )
            if len (batch )>=100 :
                deleted +=await _delete_message_batch_safe (client ,chat_id ,batch )
                batch =[]
            if scanned >=limit :
                break 
        if batch :
            deleted +=await _delete_message_batch_safe (client ,chat_id ,batch )
    except FloodWait as fw :
        await asyncio .sleep (min (int (fw .value )+2 ,20 ))
    except Exception as e :
        logger .warning (f"clean exit delete messages failed {uid }/{chat_id }: {e }")
    return deleted ,scanned 

async def _delete_private_history_both_sides (client ,chat_id ):
    try :
        if hasattr (client ,"delete_chat_history"):
            await client .delete_chat_history (chat_id ,revoke =True )
            return True 
    except FloodWait as fw :
        await asyncio .sleep (fw .value +2 )
        return False 
    except Exception :
        pass 
    try :
        peer =await safe_resolve_peer (client ,chat_id )
        if not peer :
            return False 
        await client .invoke (functions .messages .DeleteHistory (peer =peer ,max_id =0 ,revoke =True ))
        return True 
    except FloodWait as fw :
        await asyncio .sleep (fw .value +2 )
        return False 
    except Exception as e :
        logger .warning (f"private history revoke failed {chat_id }: {e }")
        return False 

async def _send_clean_temp_notice (client ,chat_id ,text ):
    try :
        m =await client .send_message (chat_id ,text )
        await asyncio .sleep (4 )
        try :
            await m .delete (revoke =True )
        except TypeError :
            await m .delete ()
        except Exception :
            pass 
    except Exception :
        pass 

async def _leave_chat_safe (client ,chat_id ):
    for attempt in (1 ,2 ):
        try :
            try :
                await client .leave_chat (chat_id ,delete =True )
            except TypeError :
                await client .leave_chat (chat_id )
            return True 
        except FloodWait as fw :
            await asyncio .sleep (min (int (fw .value )+2 ,20 ))
        except Exception as e :
            if attempt ==2 :
                logger .warning (f"leave_chat failed {chat_id }: {e }")
                return False 
            await asyncio .sleep (1 )
    return False 

async def _run_clean_exit_group (client ,chat_id ,uid ):
    try :
        await _delete_my_messages_in_chat (client ,chat_id ,uid ,since_ts =None ,max_scan =CLEAN_EXIT_MESSAGE_LIMIT )
    except Exception as e :
        logger .warning (f"clean exit cleanup failed {uid }/{chat_id }: {e }")
    await _leave_chat_safe (client ,chat_id )

async def _run_clean_range (client ,chat_id ,uid ,since_ts ,title ):
    try :
        deleted ,_ =await _delete_my_messages_in_chat (client ,chat_id ,uid ,since_ts =since_ts ,max_scan =CLEAN_EXIT_MESSAGE_LIMIT )
    except Exception as e :
        logger .warning (f"clean range failed {uid }/{chat_id }: {e }")
        return 
    await _send_clean_temp_notice (client ,chat_id ,f"{title } انجام شد. تعداد حذف‌شده: {deleted }")

class _MaintenancePaused (Exception ):
    pass 

def _maintenance_restrict (uid ,exc ):
    now =time .monotonic ()
    if isinstance (exc ,FloodWait ):
        if ACCOUNT_MAINTENANCE_LIMIT_KIND .get (uid )!="restricted"or ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 )<=now :
            ACCOUNT_MAINTENANCE_LIMIT_KIND [uid ]="flood"
            ACCOUNT_MAINTENANCE_AFTER [uid ]=max (ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 ),now +max (5 ,exc .value +2 ))
    elif type (exc ).__name__ in ("PeerFlood","UserRestricted","UserDeactivatedBan"):
        ACCOUNT_MAINTENANCE_LIMIT_KIND [uid ]="restricted"
        ACCOUNT_MAINTENANCE_AFTER [uid ]=max (ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 ),now +86400 )
    else :
        return False 
    logger .warning ("Account maintenance paused for %s: %s",uid ,type (exc ).__name__ )
    return True 

async def _maintenance_rpc (client ,uid ,query ):
    delay =ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 )-time .monotonic ()
    if delay >0 and ACCOUNT_MAINTENANCE_LIMIT_KIND .get (uid )=="restricted":
        raise _MaintenancePaused ("account-restricted")
    if delay >6 :raise _MaintenancePaused ("cooldown")
    if delay >0 :await asyncio .sleep (delay )
    if ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 )<=time .monotonic ():
        ACCOUNT_MAINTENANCE_LIMIT_KIND .pop (uid ,None )
    try :
        return await client .invoke (query ,sleep_threshold =0 )
    except FloodWait as exc :
        _maintenance_restrict (uid ,exc )
        raise 
    except Exception as exc :
        if _maintenance_restrict (uid ,exc ):raise _MaintenancePaused ("account-restricted")from None 
        raise 
    finally :
        ACCOUNT_MAINTENANCE_AFTER [uid ]=max (ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 ),time .monotonic ()+5 )

async def _maintenance_note (client ,text ):
    try :
        await client .send_message ("me",text ,parse_mode =ParseMode .HTML ,disable_notification =True )
    except Exception as exc :
        logger .warning ("Maintenance private summary failed: %s",type (exc ).__name__ )

async def _bulk_wait_for_limit (client ,uid ):
    if ACCOUNT_MAINTENANCE_LIMIT_KIND .get (uid )=="restricted":
        raise _MaintenancePaused ("account-restricted")
    delay =max (0 ,ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 )-time .monotonic ())
    progress =getattr (client ,"_darkself_maintenance_progress",{})
    progress ["state"]="waiting"
    progress ["waits"]=progress .get ("waits",0 )+1 
    progress ["wait_until"]=time .time ()+delay 
    now =time .monotonic ()
    if now -getattr (client ,"_darkself_bulk_pause_notice_at",-1000000 )>=60 :
        client ._darkself_bulk_pause_notice_at =now 
        await _maintenance_note (client ,f"<b>پاکسازی در حال مکث است، نه لغو.</b>\nتلگرام درخواست صبر داده است؛ حدود {math .ceil (delay )} ثانیه.\nبعد از پایان این زمان، عملیات خودکار ادامه پیدا می‌کند.\nبرای لغو: «توقف پاکسازی»")
    while True :
        if not SELF_ACTIVE_STATUS .get (uid ,True ):raise _MaintenancePaused ("inactive")
        delay =ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 )-time .monotonic ()
        if delay <=0 :break 
        await asyncio .sleep (min (delay ,30 ))
        if ACCOUNT_MAINTENANCE_LIMIT_KIND .get (uid )=="restricted":raise _MaintenancePaused ("account-restricted")
    ACCOUNT_MAINTENANCE_LIMIT_KIND .pop (uid ,None )
    progress ["state"]="running"
    progress ["wait_until"]=0 

async def _bulk_retry_call (client ,uid ,operation ,*args ,**kwargs ):
    transient_retries =0 
    while True :
        if not SELF_ACTIVE_STATUS .get (uid ,True ):raise _MaintenancePaused ("inactive")
        remaining =ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 )-time .monotonic ()
        limit_kind =ACCOUNT_MAINTENANCE_LIMIT_KIND .get (uid )
        if remaining >0 and limit_kind =="restricted":raise _MaintenancePaused ("account-restricted")
        if remaining >0 and limit_kind =="flood":await _bulk_wait_for_limit (client ,uid )
        try :
            return await operation (*args ,**kwargs )
        except FloodWait as exc :
            _maintenance_restrict (uid ,exc )
            await _bulk_wait_for_limit (client ,uid )
        except (TimeoutError ,OSError ):
            if transient_retries >=2 :raise 
            transient_retries +=1 
            await asyncio .sleep (3 *transient_retries )
        except Exception as exc :
            if _maintenance_restrict (uid ,exc ):raise _MaintenancePaused ("account-restricted")from None 
            raise 

async def _bulk_dialog_snapshot (client ,uid ):
    async def collect ():
        return [chat async for chat in _maintenance_dialog_chats (client )]
    return await _bulk_retry_call (client ,uid ,collect )

def _bulk_chat_matches (chat ,kind ):
    if not chat :return False 
    if kind =="groups":return chat .type in (ChatType .GROUP ,ChatType .SUPERGROUP )
    if kind =="channels":return chat .type ==ChatType .CHANNEL 
    if kind =="bots":
        manager_id =int (BOT_TOKEN .split (":",1 )[0 ])
        return chat .type ==ChatType .BOT and chat .id !=manager_id 
    return False 

async def _maintenance_dialog_chats (client ):
    
    seen =set ()
    for folder in (0 ,1 ):
        offset_id ,offset_date ,offset_peer =0 ,0 ,types .InputPeerEmpty ()
        cursors =set ()
        while True :
            result =await client .invoke (functions .messages .GetDialogs (offset_date =offset_date ,offset_id =offset_id ,offset_peer =offset_peer ,limit =100 ,hash =0 ,folder_id =folder ,exclude_pinned =bool (offset_id )),sleep_threshold =0 )
            dialogs =[d for d in getattr (result ,"dialogs",[])if isinstance (d ,types .Dialog )]
            if not dialogs :break 
            users ={item .id :item for item in getattr (result ,"users",[])}
            chats ={item .id :item for item in getattr (result ,"chats",[])}
            for dialog in dialogs :
                peer =dialog .peer 
                cid =pyrogram .utils .get_peer_id (peer )
                if cid in seen :continue 
                seen .add (cid )
                if isinstance (peer ,types .PeerUser ):
                    entity =users .get (peer .user_id )
                    kind =ChatType .BOT if getattr (entity ,"bot",False )else ChatType .PRIVATE 
                elif isinstance (peer ,types .PeerChat ):
                    entity =chats .get (peer .chat_id )
                    kind =ChatType .GROUP 
                else :
                    entity =chats .get (peer .channel_id )
                    kind =ChatType .SUPERGROUP if getattr (entity ,"megagroup",False )else ChatType .CHANNEL 
                if getattr (entity ,"left",False ):continue 
                yield SimpleNamespace (id =cid ,type =kind )
            last =dialogs [-1 ]
            cid =pyrogram .utils .get_peer_id (last .peer )
            top =next ((m for m in getattr (result ,"messages",[])if not isinstance (m ,types .MessageEmpty )and m .id ==last .top_message and pyrogram .utils .get_peer_id (m .peer_id )==cid ),None )
            cursor =(cid ,last .top_message )
            if cursor in cursors :raise RuntimeError ("Dialog pagination did not advance")
            cursors .add (cursor )
            if len (getattr (result ,"dialogs",[]))<100 :break 
            offset_id =last .top_message 
            offset_date =int (getattr (top ,"date",0 )or 0 )
            offset_peer =await client .resolve_peer (cid )
            await asyncio .sleep (0.4 )

async def _run_bulk_cleanup (client ,uid ,kind ,max_items =None ):
    
    stats ={"selected":0 ,"attempted":0 ,"completed":0 ,"blocked":0 ,"skipped":0 ,"failed":0 ,"stopped":False ,"waits":0 ,"state":"running","stop_reason":""}
    client ._darkself_maintenance_progress =stats 
    pending_departures =set ()
    try :
        targets ={chat .id :chat for chat in await _bulk_dialog_snapshot (client ,uid )if _bulk_chat_matches (chat ,kind )}
        stats ["selected"]=len (targets )
        selected =list (targets .values ())
        if max_items is not None :selected =selected [:max (0 ,int (max_items ))]
        for chat in selected :
            if not SELF_ACTIVE_STATUS .get (uid ,True ):raise _MaintenancePaused ("inactive")
            stats ["attempted"]+=1 
            departure_sent =False 
            try :
                if kind =="bots":
                    peer =await _bulk_retry_call (client ,uid ,client .resolve_peer ,chat .id )
                    if not isinstance (peer ,types .InputPeerUser ):
                        stats ["skipped"]+=1 
                        continue 
                    await _bulk_retry_call (client ,uid ,_maintenance_rpc ,client ,uid ,functions .contacts .Block (id =peer ))
                    full =await _bulk_retry_call (client ,uid ,client .invoke ,functions .users .GetFullUser (id =types .InputUser (user_id =peer .user_id ,access_hash =peer .access_hash )),sleep_threshold =0 )
                    if not getattr (full .full_user ,"blocked",False ):raise _MaintenancePaused ("unconfirmed-block")
                    stats ["blocked"]+=1 
                    for _ in range (100 ):
                        result =await _bulk_retry_call (client ,uid ,_maintenance_rpc ,client ,uid ,functions .messages .DeleteHistory (peer =peer ,max_id =0 ,just_clear =False ,revoke =False ))
                        if not getattr (result ,"offset",0 ):break 
                    else :raise _MaintenancePaused ("history-incomplete")
                    history =await _bulk_retry_call (client ,uid ,client .invoke ,functions .messages .GetHistory (peer =peer ,offset_id =0 ,offset_date =0 ,add_offset =0 ,limit =1 ,max_id =0 ,min_id =0 ,hash =0 ),sleep_threshold =0 )
                    if any (not isinstance (item ,types .MessageEmpty )for item in history .messages ):raise _MaintenancePaused ("unconfirmed-history")
                else :
                    try :
                        member =await _bulk_retry_call (client ,uid ,client .get_chat_member ,chat .id ,uid )
                    except Exception as exc :
                        if type (exc ).__name__ !="UserNotParticipant":raise 
                        member =SimpleNamespace (status =ChatMemberStatus .LEFT )
                    if member .status ==ChatMemberStatus .OWNER :
                        stats ["skipped"]+=1 
                        continue 
                    if member .status not in (ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ):
                        peer =await _bulk_retry_call (client ,uid ,client .resolve_peer ,chat .id )
                        if isinstance (peer ,types .InputPeerChannel ):
                            query =functions .channels .LeaveChannel (channel =types .InputChannel (channel_id =peer .channel_id ,access_hash =peer .access_hash ))
                        elif isinstance (peer ,types .InputPeerChat ):
                            query =functions .messages .DeleteChatUser (**{
                                "chat_id":peer .chat_id ,
                                "user_id":types .InputUserSelf (),
                                "revoke_history":False 
                            })
                        else :
                            stats ["skipped"]+=1 
                            continue 
                        await _bulk_retry_call (client ,uid ,_maintenance_rpc ,client ,uid ,query )
                        departure_sent =True 
                    try :
                        member =await _bulk_retry_call (client ,uid ,client .get_chat_member ,chat .id ,uid )
                        if member .status not in (ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ):
                            raise _MaintenancePaused ("unconfirmed-leave")
                    except Exception as exc :
                        if type (exc ).__name__ !="UserNotParticipant":raise 
                stats ["completed"]+=1 
            except _MaintenancePaused as exc :
                if str (exc ).startswith ("unconfirmed-")or str (exc )=="history-incomplete":
                    stats ["failed"]+=1 
                    logger .warning ("Bulk item unconfirmed; continuing for %s/%s: %s",uid ,chat .id ,str (exc ))
                    continue 
                raise 
            except Exception as exc :
                if departure_sent and isinstance (exc ,ChannelPrivate ):
                    pending_departures .add (chat .id )
                    continue 
                if _maintenance_restrict (uid ,exc ):raise _MaintenancePaused ("account-restricted")from None 
                stats ["failed"]+=1 
                logger .warning ("Bulk maintenance item failed for %s/%s: %s",uid ,chat .id ,type (exc ).__name__ )
    except _MaintenancePaused as exc :
        stats ["stopped"]=True 
        stats ["stop_reason"]=str (exc )
        logger .warning ("Bulk maintenance stopped for %s: %s",uid ,str (exc ))
    except asyncio .CancelledError :
        stats ["stopped"]=True 
        stats ["state"]="cancelled"
        stats ["stop_reason"]="cancelled"
        raise 
    except Exception as exc :
        _maintenance_restrict (uid ,exc )
        stats ["stopped"]=True 
        stats ["stop_reason"]="scan-failed"
        logger .warning ("Bulk maintenance scan failed for %s: %s",uid ,type (exc ).__name__ )
    if pending_departures :
        try :
            still_present ={chat .id for chat in await _bulk_dialog_snapshot (client ,uid )}
            stats ["completed"]+=len (pending_departures -still_present )
            stats ["failed"]+=len (pending_departures &still_present )
        except Exception as exc :
            _maintenance_restrict (uid ,exc )
            stats ["failed"]+=len (pending_departures )
            stats ["stopped"]=True 
            stats ["stop_reason"]=str (exc )if isinstance (exc ,_MaintenancePaused )else "verification-failed"
            logger .warning ("Departure verification deferred for %s: %s",uid ,type (exc ).__name__ )
    stats ["remaining"]=max (0 ,stats ["selected"]-stats ["completed"]-stats ["skipped"])
    stats ["state"]="stopped"if stats ["stopped"]else "finished"
    return stats 

def _membership_target (value ):
    value =str (value or "").strip ().rstrip (".,؛،!؟)")
    if value .startswith ("@"):value ="https://t.me/"+value [1 :]
    if re .match (r"^(?:t\.me|telegram\.me)/",value ,re .I ):value ="https://"+value 
    try :
        url =urlsplit (value )
        if url .scheme =="tg":
            args =parse_qs (url .query )
            if url .netloc =="join"and set (args )=={"invite"}:
                token =args ["invite"][0 ]
                return ("invite",token )if re .fullmatch (r"[A-Za-z0-9_-]{5,256}",token )else None 
            if url .netloc =="resolve"and set (args )=={"domain"}:
                value ="https://t.me/"+args ["domain"][0 ]
                url =urlsplit (value )
            else :return None 
        if url .scheme not in ("https","http")or url .hostname not in ("t.me","www.t.me","telegram.me","www.telegram.me"):
            return None 
        if url .username or url .password or url .port or url .query or url .fragment :return None 
        path =unquote (url .path ).strip ("/")
        token =path [1 :]if path .startswith ("+")else path [9 :]if path .startswith ("joinchat/")else None 
        if token is not None :
            return ("invite",token )if re .fullmatch (r"[A-Za-z0-9_-]{5,256}",token )else None 
        if re .fullmatch (r"[A-Za-z][A-Za-z0-9_]{3,31}",path )and path .lower ()not in ("share","proxy","socks","login","addstickers","addemoji","boost","invoice","giftcode"):
            return ("public",path .lower ())
    except (ValueError ,TypeError ):pass 
    return None 

def _membership_targets (message ):
    
    values =[]
    keyboard =getattr (getattr (message ,"reply_markup",None ),"inline_keyboard",None )or []
    for row in keyboard :
        for button in row :
            if getattr (button ,"url",None ):values .append (button .url )
    result =[]
    for value in values :
        target =_membership_target (value )
        if target and target not in result :result .append (target )
    return result 

def _is_membership_prompt (message ):
    body =(getattr (message ,"text",None )or getattr (message ,"caption",None )or "")
    rows =getattr (getattr (message ,"reply_markup",None ),"inline_keyboard",None )or []
    body +=" "+" ".join (str (getattr (button ,"text","")or "")for row in rows for button in row )
    return bool (re .search (r"عضو|عضویت|\bjoin\b|subscrib|subscription|подпис",body ,re .I ))

async def _run_membership_join (client ,uid ,prompt ):
    
    stats ={"joined":0 ,"already":0 ,"requested":0 ,"skipped":0 ,"failed":0 ,"stopped":False ,"verification_sent":False }
    client ._darkself_maintenance_progress =stats 
    sender =getattr (prompt ,"from_user",None )
    if not sender or not getattr (sender ,"is_bot",False )or prompt .chat .id !=sender .id or not _is_membership_prompt (prompt ):return stats 
    for kind ,value in _membership_targets (prompt ):
        try :
            if not SELF_ACTIVE_STATUS .get (uid ,True ):raise _MaintenancePaused ("inactive")
            if kind =="invite":
                invite =await client .invoke (functions .messages .CheckChatInvite (hash =value ),sleep_threshold =0 )
                if isinstance (invite ,types .ChatInviteAlready ):
                    stats ["already"]+=1 
                    continue 
                if getattr (invite ,"subscription_pricing",None )or getattr (invite ,"subscription_form_id",None ):
                    stats ["skipped"]+=1 
                    continue 
                query =functions .messages .ImportChatInvite (hash =value )
            else :
                chat =await client .get_chat (value )
                if chat .type not in (ChatType .CHANNEL ,ChatType .SUPERGROUP ):
                    stats ["skipped"]+=1 
                    continue 
                try :
                    member =await client .get_chat_member (chat .id ,uid )
                    if member .status not in (ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ):
                        stats ["already"]+=1 
                        continue 
                    if member .status ==ChatMemberStatus .BANNED :
                        stats ["skipped"]+=1 
                        continue 
                except Exception as exc :
                    if type (exc ).__name__ not in ("UserNotParticipant","ChannelPrivate"):raise 
                peer =await client .resolve_peer (chat .id )
                query =functions .channels .JoinChannel (channel =types .InputChannel (channel_id =peer .channel_id ,access_hash =peer .access_hash ))
            await _maintenance_rpc (client ,uid ,query )
            
            if kind =="invite":
                check =await client .invoke (functions .messages .CheckChatInvite (hash =value ),sleep_threshold =0 )
                if not isinstance (check ,types .ChatInviteAlready ):raise _MaintenancePaused ("unconfirmed-join")
            else :
                member =await client .get_chat_member (chat .id ,uid )
                if member .status in (ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ):raise _MaintenancePaused ("unconfirmed-join")
            stats ["joined"]+=1 
        except _MaintenancePaused :
            stats ["stopped"]=True 
            break 
        except Exception as exc :
            name =type (exc ).__name__ 
            if name =="InviteRequestSent":stats ["requested"]+=1 
            elif name =="UserAlreadyParticipant":stats ["already"]+=1 
            elif _maintenance_restrict (uid ,exc ):
                stats ["stopped"]=True 
                break 
            else :
                stats ["failed"]+=1 
                logger .warning ("Requested membership failed for %s: %s",uid ,name )
    if stats ["joined"]+stats ["already"]and not any (stats [key ]for key in ("requested","skipped","failed","stopped")):
        rows =getattr (getattr (prompt ,"reply_markup",None ),"inline_keyboard",None )or []
        button =next ((button for row in rows for button in row if re .sub (r"[\W_]+","",str (getattr (button ,"text","")or "").casefold ())in ("عضوشدم","عضوشدمفعالسازی","تاییدعضویت","تأییدعضویت","بررسیعضویت","checkmembership","ijoined")and getattr (button ,"callback_data",None )is not None ),None )
        if button :
            try :
                data =button .callback_data .encode ()if isinstance (button .callback_data ,str )else button .callback_data 
                peer =await client .resolve_peer (prompt .chat .id )
                await _maintenance_rpc (client ,uid ,functions .messages .GetBotCallbackAnswer (peer =peer ,msg_id =prompt .id ,data =data ))
                stats ["verification_sent"]=True 
            except Exception as exc :
                if isinstance (exc ,_MaintenancePaused )or _maintenance_restrict (uid ,exc ):stats ["stopped"]=True 
                logger .warning ("Membership confirmation failed for %s: %s",uid ,type (exc ).__name__ )
    return stats 

async def _launch_account_maintenance (client ,uid ,factory ,title ,resume_on_flood =False ):
    running =getattr (client ,"_darkself_maintenance_task",None )
    if running and not running .done ():
        return await _maintenance_note (client ,"یک عملیات در حال اجراست. برای توقف، «توقف پاکسازی» را ارسال کن.")
    wait_left =ACCOUNT_MAINTENANCE_AFTER .get (uid ,0 )-time .monotonic ()
    limit_kind =ACCOUNT_MAINTENANCE_LIMIT_KIND .get (uid )
    if (wait_left >0 and limit_kind =="restricted")or (wait_left >6 and not (resume_on_flood and limit_kind =="flood")):
        return await _maintenance_note (client ,"عملیات به‌دلیل محدودیت حساب فعلاً متوقف است؛ بعداً دوباره امتحان کن.")
    async def runner ():
        try :
            await _maintenance_note (client ,f"<b>{title }</b>\nعملیات شروع شد. نتیجه همین‌جا ارسال می‌شود؛ برای توقف، «توقف پاکسازی» را بفرست.")
            stats =await factory ()
            if "completed"in stats :
                body =f"انجام و تأییدشده: {stats ['completed']}\nربات مسدودشده: {stats ['blocked']}\nمستثنا (مالک): {stats ['skipped']}\nناموفق: {stats ['failed']}\nباقیمانده از فهرست اولیه: {stats ['remaining']}"
            else :
                body =f"عضویت تأییدشده: {stats ['joined']}\nاز قبل عضو: {stats ['already']}\nدرخواست ارسال‌شده: {stats ['requested']}\nردشده یا نیازمند اقدام دستی: {stats ['skipped']}\nناموفق: {stats ['failed']}"
            if "completed"in stats :
                body +=f"\nمکث موقت و ادامهٔ خودکار: {stats .get ('waits',0 )} بار"
                if not stats ["stopped"]and stats ["failed"]:
                    body +="\nهمهٔ موارد بررسی شدند؛ موارد ناموفق یا تأییدنشدنی حذف‌شده حساب نشده‌اند."
            if stats ["stopped"]:
                reasons ={"account-restricted":"محدودیت جدی حساب؛ برای محافظت از حساب ادامه داده نشد.","inactive":"سلف غیرفعال شد.","scan-failed":"خواندن فهرست چت‌ها کامل نشد.","verification-failed":"بررسی نتیجه کامل نشد.","cooldown":"محدودیت حساب هنوز برقرار است."}
                body +="\nعلت توقف: "+reasons .get (stats .get ("stop_reason"),"نیاز به بررسی یا اقدام دستی دارد.")
            await _maintenance_note (client ,f"<b>{title }</b>\n\n{body }")
        except asyncio .CancelledError :raise 
        except Exception as exc :logger .warning ("Maintenance worker failed for %s: %s",uid ,type (exc ).__name__ )
    task =asyncio .create_task (runner ())
    client ._darkself_maintenance_task =task 
    pair =ACTIVE_BOTS .get (uid )
    if pair :
        pair [1 ].append (task )
        def finished (done ):
            try :pair [1 ].remove (done )
            except ValueError :pass 
        task .add_done_callback (finished )

async def bulk_cleanup_controller (client ,message ):
    uid =client .me .id 
    if not getattr (message ,"from_user",None )or message .from_user .id !=uid :return 
    if getattr (message ,"forward_date",None )or getattr (message ,"via_bot",None ):return 
    cmd =re .sub (r"\s+"," ",(get_cmd (uid ,message .text )or "").replace ("‌"," ")).strip ()
    if cmd =="توقف پاکسازی":
        task =getattr (client ,"_darkself_maintenance_task",None )
        if task and not task .done ():
            task .cancel ()
            try :await task 
            except asyncio .CancelledError :pass 
            await _maintenance_note (client ,"عملیات متوقف شد. اقدام‌های قبلی بازگردانده نمی‌شوند.")
        return 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    match =re .fullmatch (r"حذف (?:تمام|همه) (گروه|کانال|ربات)\s*ها",cmd )
    if not match :return 
    kind ,title ={"گروه":("groups","خروج از گروه‌ها"),"کانال":("channels","خروج از کانال‌ها"),"ربات":("bots","مسدودسازی و حذف ربات‌ها")}[match .group (1 )]
    await _launch_account_maintenance (client ,uid ,lambda :_run_bulk_cleanup (client ,uid ,kind ),title ,resume_on_flood =True )

async def membership_join_controller (client ,message ):
    uid =client .me .id 
    if not getattr (message ,"from_user",None )or message .from_user .id !=uid :return 
    if getattr (message ,"forward_date",None )or getattr (message ,"via_bot",None ):return 
    if message .chat .type !=ChatType .BOT :return 
    if not SELF_ACTIVE_STATUS .get (uid ,True )or data_manager .is_banned (uid ):return 
    if not re .fullmatch (r"عضو",(message .text or "").strip ()):return 
    try :
        
        prompt =getattr (message ,"reply_to_message",None )
        if prompt is None :return 
        sender =getattr (prompt ,"from_user",None )
        if not prompt or not sender or not sender .is_bot or prompt .chat .id !=message .chat .id or sender .id !=message .chat .id :return 
        if not _is_membership_prompt (prompt )or not _membership_targets (prompt ):return 
        await _launch_account_maintenance (client ,uid ,lambda :_run_membership_join (client ,uid ,prompt ),"نتیجهٔ عضویت درخواستی")
    except Exception as exc :
        _maintenance_restrict (uid ,exc )
        logger .warning ("Membership trigger failed for %s: %s",uid ,type (exc ).__name__ )

async def clean_exit_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None 
    if not cmd :return 
    cmd =re .sub (r"\s+"," ",cmd .strip ())
    chat =getattr (message ,"chat",None )
    if not chat :
        return 

    is_private =chat .type ==ChatType .PRIVATE 
    is_group =chat .type in (ChatType .GROUP ,ChatType .SUPERGROUP )

    if re .match (r"^ترک(?: گروه)?$",cmd ,re .I ):
        if is_private :
            try :
                await _delete_private_history_both_sides (client ,chat .id )
            finally :
                raise StopPropagation 
        if not is_group :
            return await safe_edit_message (message ,"این دستور فقط داخل گروه یا پیوی اجرا می‌شود.")
        try :
            await message .delete ()
        except Exception :
            pass 
        asyncio .create_task (_run_clean_exit_group (client ,chat .id ,uid ))
        raise StopPropagation 

    if re .match (r"^ترک پیوی$",cmd ,re .I ):
        if not is_private :
            return await safe_edit_message (message ,"این دستور فقط داخل پیوی اجرا می‌شود.")
        await _delete_private_history_both_sides (client ,chat .id )
        raise StopPropagation 

    if re .match (r"^حذف پیام های امروز$",cmd ,re .I ):
        try :
            await message .delete ()
        except Exception :
            pass 
        asyncio .create_task (_run_clean_range (client ,chat .id ,uid ,_today_start_ts (),"پاکسازی امروز"))
        raise StopPropagation 

    if re .match (r"^حذف پیام های هفته$",cmd ,re .I ):
        try :
            await message .delete ()
        except Exception :
            pass 
        asyncio .create_task (_run_clean_range (client ,chat .id ,uid ,_week_start_ts (),"پاکسازی هفته"))
        raise StopPropagation 

def _short_button_text (text :str ,limit :int =34 )->str :
    text =re .sub (r"\s+"," ",str (text or "")).strip ()
    return text if len (text )<=limit else text [:limit -1 ]+"…"

def _chat_has_protected_content (chat )->bool :
    for attr in ("has_protected_content","protect_content","noforwards"):
        try :
            if bool (getattr (chat ,attr ,False )):
                return True 
        except Exception :
            pass 
    return False 

async def _is_private_protected_channel (client ,chat )->bool :
    try :
        if not chat or chat .type !=ChatType .CHANNEL :
            return False 
        if getattr (chat ,"username",None ):
            return False 
        if _chat_has_protected_content (chat ):
            return True 
        try :
            full =await client .get_chat (chat .id )
            if _chat_has_protected_content (full ):
                return True 
        except Exception :
            pass 
        try :
            async for msg in client .get_chat_history (chat .id ,limit =1 ):
                if bool (getattr (msg ,"has_protected_content",False )):
                    return True 
                break 
        except Exception :
            pass 
    except Exception :
        pass 
    return False 

async def _scan_private_channel_dialogs_from_client (self_client ,limit :int =30 ):
    channels =[]
    seen =set ()
    try :
        async for d in self_client .get_dialogs (limit =80 ):
            ch =getattr (d ,"chat",None )
            if not ch or getattr (ch ,"id",None )in seen :
                continue 
            if await _is_private_protected_channel (self_client ,ch ):
                seen .add (ch .id )
                title =getattr (ch ,"title",None )or f"Channel {ch .id }"
                channels .append ((int (ch .id ),title ))
                if len (channels )>=limit :
                    break 
    except Exception as e :
        logger .warning (f"private protected channel scan failed: {type (e ).__name__ }: {e }")
    return channels 

async def _get_private_channel_dialogs (uid :int ,limit :int =30 ):
    uid =int (uid )
    try :
        udata =data_manager .get_user_data (uid )
        cache =udata .get ("private_channel_cache")or []
        ts =float (udata .get ("private_channel_cache_ts",0 )or 0 )
        if cache and time .time ()-ts <600 :
            out =[]
            for item in cache [:limit ]:
                try :
                    out .append ((int (item .get ("id")),str (item .get ("title")or item .get ("id"))))
                except Exception :
                    pass 
            if out :
                return out 
    except Exception :
        pass 
    pair =ACTIVE_BOTS .get (uid )
    if not pair :
        return []
    return await _scan_private_channel_dialogs_from_client (pair [0 ],limit =limit )

def _private_channel_home_text (uid :int ,count :int =0 )->str :
    return (
    "╔══════ ✦ 𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 ✦ ══════╗\n"
    "        سیو کانال خصوصی\n"
    "╚══════════════════════════╝\n\n"
    f"USER `{uid }`\n"
    f"کانال‌های خصوصی ضد فوروارد پیدا شده: `{count }`\n\n"
    "روی اسم کانال بزن، بعد تعداد پست‌های آخر را انتخاب کن.\n"
    "فقط کانال‌هایی نمایش داده می‌شوند که فوروارد/کپی از آن‌ها بسته است."
    )

def _private_channel_home_markup_json (uid :int ,channels ):
    rows =[]
    if channels :
        for chat_id ,title in channels :
            rows .append ([{"text":_short_button_text (title ),"callback_data":f"privch_{int (uid )}_{int (chat_id )}"}])
    else :
        rows .append ([{"text":"کانال خصوصی ضد فوروارد پیدا نشد","callback_data":"help_none"}])
    rows .append ([{"text":"بستن","callback_data":f"privclose_{int (uid )}"}])
    return {"inline_keyboard":rows }

def _private_channel_count_text (uid :int ,chat_id :int ,title :str )->str :
    return (
    "╔══════ ✦ 𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 ✦ ══════╗\n"
    "        انتخاب تعداد ذخیره\n"
    "╚══════════════════════════╝\n\n"
    f"کانال: {title }\n\n"
    "چند پست آخر دانلود و در Saved Messages ذخیره شود؟\n"
    "از ۱ تا ۲۰ انتخاب کن."
    )

def _private_channel_count_markup_json (uid :int ,chat_id :int ):
    rows =[]
    nums =list (range (1 ,21 ))
    for i in range (0 ,20 ,5 ):
        rows .append ([
        {"text":str (n ),"callback_data":f"privcnt_{int (uid )}_{int (chat_id )}_{n }"}
        for n in nums [i :i +5 ]
        ])
    rows .append ([
    {"text":"بازگشت","callback_data":f"privback_{int (uid )}"},
    {"text":"بستن","callback_data":f"privclose_{int (uid )}"}
    ])
    return {"inline_keyboard":rows }

async def _edit_private_inline_page (callback ,text :str ,markup_json =None ):
    try :
        payload ={"text":text }
        if callback .inline_message_id :
            payload ["inline_message_id"]=callback .inline_message_id 
            if markup_json is not None :
                payload ["reply_markup"]=markup_json 
            res =await bot_api_request ("editMessageText",payload ,timeout =3.0 )
            if res .get ("ok"):
                return True 
        if callback .message :
            await callback .message .edit_text (text ,reply_markup =InlineKeyboardMarkup ([
            [InlineKeyboardButton (btn ["text"],callback_data =btn ["callback_data"])for btn in row ]
            for row in (markup_json or {}).get ("inline_keyboard",[])
            ])if markup_json else None )
            return True 
    except Exception :
        pass 
    return False 

async def _save_protected_message_to_saved (client ,msg )->bool :
    caption =(getattr (msg ,"caption",None )or "").strip ()
    text_body =(getattr (msg ,"text",None )or "").strip ()
    file_path =None 
    try :

        if text_body and not any (getattr (msg ,x ,None )for x in ("photo","video","document","animation","voice","audio","video_note","sticker")):
            await client .send_message ("me",text_body )
            return True 

        media_kind =None 
        if getattr (msg ,"photo",None ):media_kind ="photo"
        elif getattr (msg ,"video",None ):media_kind ="video"
        elif getattr (msg ,"document",None ):media_kind ="document"
        elif getattr (msg ,"animation",None ):media_kind ="animation"
        elif getattr (msg ,"voice",None ):media_kind ="voice"
        elif getattr (msg ,"audio",None ):media_kind ="audio"
        elif getattr (msg ,"video_note",None ):media_kind ="video_note"
        elif getattr (msg ,"sticker",None ):media_kind ="sticker"

        if not media_kind :
            if text_body or caption :
                await client .send_message ("me",text_body or caption )
                return True 
            return False 

        try :
            size =get_media_file_size (msg )
            if size and size >DIRECT_DOWNLOAD_MAX_MB *1024 *1024 :
                if caption :
                    await client .send_message ("me",f"پست رسانه‌ای حجمش بیشتر از سقف {DIRECT_DOWNLOAD_MAX_MB }MB بود و ذخیره نشد.\n\n{caption }")
                return False 
        except Exception :
            pass 

        file_path =await msg .download (file_name =ensure_download_temp_dir ()+os .sep )
        if not file_path :
            return False 

        if media_kind =="photo":await client .send_photo ("me",file_path ,caption =caption or None )
        elif media_kind =="video":await client .send_video ("me",file_path ,caption =caption or None )
        elif media_kind =="document":await client .send_document ("me",file_path ,caption =caption or None )
        elif media_kind =="animation":await client .send_animation ("me",file_path ,caption =caption or None )
        elif media_kind =="voice":await client .send_voice ("me",file_path ,caption =caption or None )
        elif media_kind =="audio":await client .send_audio ("me",file_path ,caption =caption or None )
        elif media_kind =="video_note":
            await client .send_video_note ("me",file_path )
            if caption :await client .send_message ("me",caption )
        elif media_kind =="sticker":
            await client .send_sticker ("me",file_path )
            if caption :await client .send_message ("me",caption )
        return True 
    except FloodWait as fw :
        await asyncio .sleep (fw .value +2 )
        return False 
    except Exception as e :
        logger .warning (f"save protected private channel message failed: {e }")

        try :
            await client .copy_message ("me",msg .chat .id ,msg .id )
            return True 
        except Exception :
            return False 
    finally :
        try :
            if file_path and os .path .exists (file_path ):
                os .remove (file_path )
        except Exception :
            pass 

async def _copy_private_channel_posts_to_saved (uid :int ,chat_id :int ,count :int ):
    uid =int (uid )
    pair =ACTIVE_BOTS .get (uid )
    if not pair :
        return 0 ,0 
    self_client =pair [0 ]
    msgs =[]
    ok =0 
    failed =0 
    try :
        ch =await self_client .get_chat (chat_id )
        if not await _is_private_protected_channel (self_client ,ch ):
            return 0 ,max (1 ,min (20 ,int (count )))
    except Exception :
        pass 
    try :
        async for msg in self_client .get_chat_history (chat_id ,limit =max (1 ,min (20 ,int (count )))):
            if getattr (msg ,"empty",False ):
                continue 
            msgs .append (msg )
    except Exception as e :
        logger .warning (f"private channel history fetch failed {uid }/{chat_id }: {e }")
        return 0 ,int (count )

    for msg in reversed (msgs ):
        if await _save_protected_message_to_saved (self_client ,msg ):
            ok +=1 
        else :
            failed +=1 
        await asyncio .sleep (0.35 )
    return ok ,failed 

def _queue_private_channel_save_job (uid :int ,chat_id :int ,count :int )->str :
    uid =int (uid );chat_id =int (chat_id );count =max (1 ,min (20 ,int (count )))
    job_id =uuid .uuid4 ().hex [:10 ]
    try :
        udata =data_manager .get_user_data (uid )
        jobs =udata .get ("private_channel_save_jobs")or []

        jobs =[j for j in jobs if isinstance (j ,dict )and j .get ("status","queued")in ("queued","running")][-10 :]
        jobs .append ({"id":job_id ,"chat_id":chat_id ,"count":count ,"status":"queued","ts":int (time .time ())})
        data_manager .update_user_data (uid ,{"private_channel_save_jobs":jobs })
        _commit_and_broadcast_shards ("private-channel-save-job")
    except Exception as e :
        logger .warning (f"queue private channel save failed for {uid }: {e }")
    return job_id 

async def private_channel_save_jobs_loop (client :Client ,uid :int ):
    await asyncio .sleep (6 )
    while uid in ACTIVE_BOTS :
        try :
            await asyncio .sleep (5 )
            udata =data_manager .get_user_data (uid )
            jobs =udata .get ("private_channel_save_jobs")or []
            if not jobs :
                continue 
            job =None 
            rest =[]
            for j in jobs :
                if isinstance (j ,dict )and j .get ("status","queued")=="queued"and job is None :
                    job =dict (j )
                    job ["status"]="running"
                    rest .append (job )
                else :
                    rest .append (j )
            if not job :
                continue 
            data_manager .update_user_data (uid ,{"private_channel_save_jobs":rest })
            try :
                await client .send_message ("me",f"سیو کانال خصوصی شروع شد.\nتعداد: {int (job .get ('count',1 ))}")
            except Exception :
                pass 
            ok ,failed =await _copy_private_channel_posts_to_saved (uid ,int (job .get ("chat_id")),int (job .get ("count",1 )))

            latest =data_manager .get_user_data (uid ).get ("private_channel_save_jobs")or []
            latest =[j for j in latest if not (isinstance (j ,dict )and j .get ("id")==job .get ("id"))]
            data_manager .update_user_data (uid ,{"private_channel_save_jobs":latest })
            data_manager .force_save_sync ()
            try :
                await client .send_message ("me",f"سیو کانال خصوصی تمام شد.\nموفق: {ok }\nناموفق: {failed }")
            except Exception :
                pass 
        except asyncio .CancelledError :
            break 
        except Exception as e :
            logger .warning ("private channel save jobs loop error for %s: %s",uid ,type (e ).__name__ )
            await asyncio .sleep (10 )

async def private_channel_save_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None 
    if not cmd or not re .match (r"^سیو\s+کانال\s+خصوصی$",cmd .strip (),re .I ):
        return 
    global BOT_USERNAME 
    try :
        wait_msg =None 
        try :
            wait_msg =await safe_edit_message (message ,"در حال ساخت صفحه سیو کانال خصوصی...")
        except Exception :
            pass 

        channels =await _scan_private_channel_dialogs_from_client (client ,limit =30 )
        try :
            data_manager .update_user_data (uid ,{
            "private_channel_cache":[{"id":int (cid ),"title":title }for cid ,title in channels ],
            "private_channel_cache_ts":int (time .time ())
            })
            _commit_and_broadcast_shards ("private-channel-cache")
        except Exception :
            pass 

        if not BOT_USERNAME :
            if not manager_bot .me :
                await manager_bot .get_me ()
            BOT_USERNAME =manager_bot .me .username 
        if not BOT_USERNAME :
            return await safe_edit_message (message ,"ربات مدیریت هنوز آماده نیست. چند ثانیه دیگر دوباره تلاش کن.")
        results =await asyncio .wait_for (client .get_inline_bot_results (BOT_USERNAME ,f"privsave_{uid }"),timeout =10.0 )
        if results and results .results :
            try :
                if wait_msg :
                    await wait_msg .delete ()
                else :
                    await message .delete ()
            except Exception :
                pass 
            return await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id )
        return await safe_edit_message (message ,"صفحه سیو کانال خصوصی ساخته نشد. Inline Mode ربات را بررسی کن.")
    except ChatSendInlineForbidden :
        return await safe_edit_message (message ,"ارسال پیام شیشه‌ای در این چت بسته است.")
    except Exception as e :
        detail =str (e ).strip ()or type (e ).__name__ 
        logger .warning (f"private channel save page error for {uid }: {type (e ).__name__ }: {e }")
        return await safe_edit_message (message ,f"خطا در ساخت صفحه سیو کانال خصوصی:\n`{detail [:180 ]}`")

async def source_controller (client ,message ):
    uid =client .me .id
    if uid !=ROOT_ADMIN :
        return
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None
    if not cmd or not re .match (r"^(?:سورس|source)$",cmd .strip (),re .I ):
        return
    path =os .path .abspath (__file__ )
    try :
        raw =open (path ,encoding ="utf-8").read ()
    except Exception as exc :
        logger .warning ("source read failed: %s",type (exc ).__name__ )
        return await safe_edit_message (message ,"**خواندن سورس ناموفق بود.**")
    lines =raw .count ("\n")+1
    size =len (raw .encode ("utf-8"))
    stamp =datetime .now (TEHRAN_TIMEZONE ).strftime ("%Y-%m-%d_%H-%M")
    out =os .path .join (tempfile .gettempdir (),f"darkself_{stamp }.py")
    try :
        with open (out ,"w",encoding ="utf-8")as fh :
            fh .write (raw )
        cap =("✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  SOURCE\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"◈ خط      `{lines :,}`\n"
        f"◈ حجم     `{size //1024 :,}` کیلوبایت\n"
        f"◈ تاریخ   `{stamp .replace ('_',' ')}`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✧ آخرین نسخه، مستقیم از سرور")
        await client .send_document ("me",out ,caption =cap ,file_name =f"darkself_{stamp }.py")
        try :
            await message .delete ()
        except Exception :
            pass
    except Exception as exc :
        logger .warning ("source send failed: %s: %s",type (exc ).__name__ ,str (exc )[:120 ])
        await safe_edit_message (message ,"**ارسال سورس ناموفق بود.**")
    finally :
        try :
            os .remove (out )
        except Exception :
            pass

AI_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
AI_ENDPOINT = "https://text.pollinations.ai/"
AI_KEY = ""
AI_KEY_URL = "https://api.groq.com/openai/v1/chat/completions"
AI_KEY_MODEL = "llama-3.3-70b-versatile"
AI_PERSONA = ("تو دستیار هوشمند فارسی‌زبان هستی. کوتاه، دقیق و خودمونی جواب بده. "
              "اگر سوال فارسی بود فارسی جواب بده و اگر انگلیسی بود انگلیسی.")
AI_G4F_CHAIN = [("HuggingSpace", ""), ("", "gpt-4"), ("CohereForAI_C4AI_Command", ""), ("", "command-r-plus")]
AI_JUNK = ("برو بخر", "خریداری", "اشتراک تهیه", "subscribe", "upgrade your plan", "api key",
           "api_key", "payment required", "model is unavailable", "try again later",
           "no cake credits", "rate limit", "insufficient")
AI_G4F = None
AI_INLINE_BOTS = ["chatgpt_query_bot"]
AI_PM_BOTS = ["FreeGPT4Bot", "AiChatGPT4bot", "chatgptai_bot"]
AI_INLINE_WAIT = 8.0
AI_GAP = 2.0
AI_MAX_HIST = 4
AI_HIST = {}
AI_LAST = [0.0]
AI_LOCK = None

def _ai_key (uid ,chat_id ):
    return (int (uid ),int (chat_id ))

def _ai_prompt (uid ,chat_id ,question ):
    hist =AI_HIST .get (_ai_key (uid ,chat_id ))or []
    parts =[AI_PERSONA ,"---"]
    for q ,a in hist [-AI_MAX_HIST :]:
        parts .append ("کاربر: "+q )
        parts .append ("دستیار: "+a )
    parts .append ("کاربر: "+question )
    parts .append ("دستیار:")
    out ="\n".join (parts )
    if len (out )>1800 :
        out =AI_PERSONA +"\n---\nکاربر: "+question +"\nدستیار:"
    return out

def _ai_remember (uid ,chat_id ,q ,a ):
    k =_ai_key (uid ,chat_id )
    lst =AI_HIST .get (k )or []
    lst .append ((q [:300 ],a [:600 ]))
    AI_HIST [k ]=lst [-AI_MAX_HIST :]

async def _ai_free (prompt ):
    session =await get_http_session ()
    url =AI_ENDPOINT +urllib .parse .quote (prompt ,safe ="")
    async with session .get (url ,headers ={"User-Agent":AI_UA },
    timeout =aiohttp .ClientTimeout (total =45 ))as r :
        body =await r .text ()
        if r .status !=200 :
            raise RuntimeError ("http %d"%r .status )
        return body .strip ()

async def _ai_keyed (prompt ):
    session =await get_http_session ()
    payload ={"model":AI_KEY_MODEL ,"messages":[
    {"role":"system","content":AI_PERSONA },{"role":"user","content":prompt }],"temperature":0.7 }
    async with session .post (AI_KEY_URL ,json =payload ,
    headers ={"Authorization":"Bearer "+AI_KEY ,"Content-Type":"application/json"},
    timeout =aiohttp .ClientTimeout (total =45 ))as r :
        data =json .loads (await r .text ())
    return (((data .get ("choices")or [{}])[0 ].get ("message")or {}).get ("content")or "").strip ()

def _ai_is_junk (txt ):
    low =(txt or "").strip ().lower ()
    if len (low )<8 :
        return True
    return any (bad in low for bad in AI_JUNK )

def _ai_g4f_sync (messages ,provider ,model ):
    global AI_G4F
    if AI_G4F is None :
        AI_G4F ={}
    key =provider or "_default"
    cl =AI_G4F .get (key )
    if cl is None :
        import g4f as _g4f
        from g4f.client import Client as _G4FClient
        cl =_G4FClient (provider =getattr (_g4f .Provider ,provider ))if provider else _G4FClient ()
        AI_G4F [key ]=cl
    r =cl .chat .completions .create (model =model or "",messages =messages ,timeout =35 )
    return ((r .choices [0 ].message .content )or "").strip ()

async def _ai_g4f (uid ,chat_id ,question ):
    msgs =[{"role":"system","content":AI_PERSONA }]
    for q ,a in (AI_HIST .get (_ai_key (uid ,chat_id ))or [])[-AI_MAX_HIST :]:
        msgs .append ({"role":"user","content":q })
        msgs .append ({"role":"assistant","content":a })
    msgs .append ({"role":"user","content":question })
    for provider ,model in AI_G4F_CHAIN :
        tag =provider or model
        try :
            txt =await asyncio .wait_for (asyncio .to_thread (_ai_g4f_sync ,msgs ,provider ,model ),timeout =45 )
        except Exception as exc :
            logger .info ("ai: g4f %s failed (%s: %s)",tag ,type (exc ).__name__ ,str (exc )[:50 ])
            continue
        if _ai_is_junk (txt ):
            logger .info ("ai: g4f %s returned junk (%s)",tag ,(txt or "")[:40 ])
            continue
        logger .info ("ai: answered by g4f/%s",tag )
        return txt
    return ""

def _ai_result_text (r ):
    msg =getattr (r ,"send_message",None )
    for attr in ("message","text"):
        v =getattr (msg ,attr ,None )if msg is not None else None
        if v :
            return str (v )
    for attr in ("description","title"):
        v =getattr (r ,attr ,None )
        if v and len (str (v ))>12 :
            return str (v )
    return ""

async def _ai_inline (client ,question ):
    for bot in AI_INLINE_BOTS :
        try :
            res =await asyncio .wait_for (client .get_inline_bot_results (bot ,question [:250 ]),timeout =AI_INLINE_WAIT )
        except Exception as exc :
            logger .info ("ai: inline %s failed (%s)",bot ,type (exc ).__name__ )
            continue
        for r in (getattr (res ,"results",None )or [])[:3 ]:
            txt =_ai_result_text (r ).strip ()
            if len (txt )>12 :
                logger .info ("ai: answered by inline @%s",bot )
                return txt
        logger .info ("ai: inline %s gave nothing",bot )
    return ""

async def _ai_pm (client ,question ):
    for bot in AI_PM_BOTS :
        try :
            sent =await client .send_message (bot ,question [:1500 ])
        except Exception as exc :
            logger .info ("ai: pm %s send failed (%s)",bot ,type (exc ).__name__ )
            continue
        answer =""
        for _ in range (30 ):
            await asyncio .sleep (0.8 )
            try :
                async for m in client .get_chat_history (bot ,limit =4 ):
                    if m .id <=sent .id or getattr (m ,"outgoing",False ):
                        continue
                    t =(getattr (m ,"text",None )or "").strip ()
                    if len (t )>12 and "..."not in t [:12 ]and not _ai_is_junk (t ):
                        answer =t
                        try :
                            await client .delete_messages (bot ,[sent .id ,m .id ])
                        except Exception :
                            pass
                        break
            except Exception :
                break
            if answer :
                break
        if answer :
            logger .info ("ai: answered by pm @%s",bot )
            return answer
        try :
            await client .delete_messages (bot ,[sent .id ])
        except Exception :
            pass
    return ""

async def _ai_ask (prompt ):
    global AI_LOCK
    if AI_LOCK is None :
        AI_LOCK =asyncio .Lock ()
    async with AI_LOCK :
        gap =AI_GAP -(time .time ()-AI_LAST [0 ])
        if gap >0 :
            await asyncio .sleep (gap )
        AI_LAST [0 ]=time .time ()
    last =""
    for attempt in range (3 ):
        try :
            if AI_KEY :
                txt =await _ai_keyed (prompt )
            else :
                txt =await _ai_free (prompt )
            if txt :
                return txt
            last ="empty"
        except Exception as exc :
            last ="%s: %s"%(type (exc ).__name__ ,str (exc )[:60 ])
            logger .info ("ai: attempt %d failed (%s)",attempt +1 ,last )
        await asyncio .sleep (2.0 *(attempt +1 ))
    raise RuntimeError (last or "failed")

async def ai_controller (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None
    if not cmd :
        return
    m =re .match (r"^(?:هوش|ai|گپت)(?:\s+(.*))?$",cmd .strip (),re .I |re .S )
    if not m :
        return
    arg =" ".join ((m .group (1 )or "").split ())
    chat_id =message .chat .id
    if arg in ("پاک","ریست","clear","reset"):
        AI_HIST .pop (_ai_key (uid ,chat_id ),None )
        return await safe_edit_message (message ,"**◈ حافظه گفتگو پاک شد.**")
    rm =getattr (message ,"reply_to_message",None )
    quoted =""
    if rm :
        quoted =(getattr (rm ,"text",None )or getattr (rm ,"caption",None )or "").strip ()[:600 ]
    if not arg and not quoted :
        return await safe_edit_message (message ,"**سوالت رو بنویس.**\nمثال: `هوش پایتخت ژاپن کجاست`")
    question =arg
    if quoted :
        question =(arg +"\n\nمتن مرتبط:\n"+quoted ).strip ()if arg else quoted
    status =await safe_edit_message (message ,"**◈ در حال فکر کردن...**")
    target =status or message
    answer =""
    try :
        answer =await _ai_g4f (uid ,chat_id ,question )
    except Exception as exc :
        logger .info ("ai: g4f layer error (%s)",type (exc ).__name__ )
    if not answer and AI_KEY :
        try :
            answer =await _ai_ask (_ai_prompt (uid ,chat_id ,question ))
        except Exception as exc :
            logger .info ("ai: key layer failed (%s)",str (exc )[:70 ])
    if not answer :
        try :
            answer =await _ai_pm (client ,question )
        except Exception as exc :
            logger .info ("ai: pm layer error (%s)",type (exc ).__name__ )
    if not answer :
        try :
            answer =await _ai_inline (client ,question )
        except Exception as exc :
            logger .info ("ai: inline layer error (%s)",type (exc ).__name__ )
    if not answer :
        return await safe_edit_message (target ,"**هوش مصنوعی جواب نداد، دوباره بزن.**")
    _ai_remember (uid ,chat_id ,question ,answer )
    answer =answer .strip ()
    head ="✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  AI\n━━━━━━━━━━━━━━━━━━\n"
    body =answer if len (answer )<3500 else answer [:3500 ]+" ..."
    await safe_edit_message (target ,head +body )

FX_TTL = 45
FX_CACHE = {"t": 0.0, "tg": {}, "wx": {}}
FX_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

FX_ITEMS = [
 ("دلار", ["دلار", "دلار آمریکا", "usd", "dollar"], "price_dollar_rl", "rial", "دلار آمریکا", "USD"),
 ("یورو", ["یورو", "eur", "euro"], "price_eur", "rial", "یورو", "EUR"),
 ("پوند", ["پوند", "gbp", "pound"], "price_gbp", "rial", "پوند انگلیس", "GBP"),
 ("درهم", ["درهم", "aed", "dirham"], "price_aed", "rial", "درهم امارات", "AED"),
 ("لیر", ["لیر", "try", "lira"], "price_try", "rial", "لیر ترکیه", "TRY"),
 ("طلا", ["طلا", "طلا 18", "طلای 18", "گرم طلا", "gold", "g18"], "geram18", "rial", "طلای 18 عیار", "1g"),
 ("طلا24", ["طلا 24", "طلای 24", "g24"], "geram24", "rial", "طلای 24 عیار", "1g"),
 ("مثقال", ["مثقال", "mesghal"], "mesghal", "rial", "مثقال طلا", "1m"),
 ("سکه", ["سکه", "سکه امامی", "sekee", "coin"], "sekee", "rial", "سکه امامی", "1x"),
 ("سکه قدیم", ["سکه قدیم", "سکه بهار", "sekeb"], "sekeb", "rial", "سکه بهار آزادی", "1x"),
 ("نیم سکه", ["نیم سکه", "نیم", "nim"], "nim", "rial", "نیم سکه", "1x"),
 ("ربع سکه", ["ربع سکه", "ربع", "rob"], "rob", "rial", "ربع سکه", "1x"),
 ("سکه گرمی", ["سکه گرمی", "گرمی", "gerami"], "gerami", "rial", "سکه گرمی", "1x"),
 ("تتر", ["تتر", "usdt", "tether"], "crypto-tether-irr", "rial", "تتر", "USDT"),
 ("انس", ["انس", "انس طلا", "ons", "xau"], "ons", "usd", "انس جهانی طلا", "oz"),
 ("نقره", ["نقره", "silver", "xag"], "silver", "usd", "انس نقره", "oz"),
 ("بیتکوین", ["بیتکوین", "بیت کوین", "btc", "bitcoin"], "crypto-bitcoin", "usd", "بیت‌کوین", "BTC"),
 ("اتریوم", ["اتریوم", "eth", "ethereum"], "crypto-ethereum", "usd", "اتریوم", "ETH"),
 ("ترون", ["ترون", "تون", "ترون کوین", "trx", "tron"], "crypto-tron", "usd", "ترون", "TRX"),
]
FX_WALLEX = {"بیتکوین": "BTCTMN", "اتریوم": "ETHTMN", "ترون": "TRXTMN", "تتر": "USDTTMN"}
FX_ALIAS = {}
for _it in FX_ITEMS:
    for _a in _it[1]:
        FX_ALIAS[_a] = _it
FX_WORDS = sorted(FX_ALIAS.keys(), key=len, reverse=True)
FX_CMD_RE = re.compile(r"^(?:قیمت\s+)?(" + "|".join(re.escape(w) for w in FX_WORDS) +
                       r")(?:\s+([0-9۰-۹٠-٩]+(?:[.,٫][0-9۰-۹٠-٩]+)?))?$", re.I)

async def _fx_json (url ):
    session =await get_http_session ()
    async with session .get (url ,headers ={"User-Agent":FX_UA ,"Accept":"application/json"},
    timeout =aiohttp .ClientTimeout (total =12 ))as r :
        return json .loads (await r .text ())

async def _fx_load (force =False ):
    now =time .time ()
    if not force and FX_CACHE ["tg"]and now -FX_CACHE ["t"]<FX_TTL :
        return FX_CACHE
    try :
        d =await _fx_json ("https://call1.tgju.org/ajax.json")
        FX_CACHE ["tg"]=d .get ("current")or {}
        FX_CACHE ["t"]=now
    except Exception as exc :
        logger .info ("rate: tgju failed (%s)",type (exc ).__name__ )
        try :
            d =await _fx_json ("https://call3.tgju.org/ajax.json")
            FX_CACHE ["tg"]=d .get ("current")or {}
            FX_CACHE ["t"]=now
        except Exception :
            pass
    try :
        w =await _fx_json ("https://api.wallex.ir/v1/markets")
        FX_CACHE ["wx"]=((w .get ("result")or {}).get ("symbols")or {})
    except Exception :
        pass
    return FX_CACHE

def _fx_num (s ):
    s =_pemoji_norm_digit (str (s or "")).replace (",","").replace ("٫",".").strip ()
    try :
        return float (s )
    except Exception :
        return 0.0

def _fx_money (v ):
    v =float (v or 0 )
    if v >=1000 :
        return "{:,}".format (int (round (v )))
    if v >=1 :
        return "{:,.2f}".format (v ).rstrip ("0").rstrip (".")
    return "{:.4f}".format (v ).rstrip ("0").rstrip (".")

def _fx_qty (v ):
    if abs (v -int (v ))<1e-9 :
        return str (int (v ))
    return ("%.4f"%v ).rstrip ("0").rstrip (".")

def _fx_pick (data ,item ):
    key =item [2 ]
    row =(data ["tg"]or {}).get (key )or {}
    price =_fx_num (row .get ("p"))
    dp =_fx_num (row .get ("dp"))
    dt =str (row .get ("dt")or "")
    tm =str (row .get ("t")or "")
    toman =0.0
    usd =0.0
    if item [3 ]=="rial":
        toman =price /10.0
    else :
        usd =price
        sym =FX_WALLEX .get (item [0 ])
        wx =(data ["wx"]or {}).get (sym )or {}
        last =_fx_num (((wx .get ("stats")or {}).get ("lastPrice")))
        if last >0 :
            toman =last
            ch =_fx_num ((wx .get ("stats")or {}).get ("24h_ch"))
            if ch :
                dp =abs (ch )
                dt ="high"if ch >0 else "low"
        else :
            usd_row =(data ["tg"]or {}).get ("price_dollar_rl")or {}
            rate =_fx_num (usd_row .get ("p"))/10.0
            toman =usd *rate if rate else 0.0
    return {"toman":toman ,"usd":usd ,"dp":dp ,"dt":dt ,"t":tm }

def _fx_card (item ,info ,qty ):
    arrow ="▲"if info ["dt"]=="high"else ("▼"if info ["dt"]=="low"else "•")
    head ="✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  LIVE RATE\n──────────────\n"
    body ="◈ **{}**  ·  {}\n".format (item [4 ],item [5 ])
    if info ["toman"]>0 :
        body +="✦ `{}` تومان\n".format (_fx_money (info ["toman"]))
    if info ["usd"]>0 :
        body +="✧ `{}` دلار\n".format (_fx_money (info ["usd"]))
    if qty and abs (qty -1.0 )>1e-9 and info ["toman"]>0 :
        body +="\n⟡ **{}** × واحد  ⟵  **{} تومان**\n".format (_fx_qty (qty ),_fx_money (info ["toman"]*qty ))
    tail ="\n{} {}٪  ·  {}".format (arrow ,_fx_money (info ["dp"]),info ["t"]or "live")
    return head +body +tail

def _fx_board (data ):
    rows =[("دلار","price_dollar_rl","دلار"),("یورو","price_eur","یورو"),
    ("طلا","geram18","طلای 18"),("سکه","sekee","سکه امامی"),("تتر","crypto-tether-irr","تتر")]
    out ="✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  LIVE BOARD\n──────────────\n"
    stamp =""
    for name ,key ,label in rows :
        row =(data ["tg"]or {}).get (key )or {}
        p =_fx_num (row .get ("p"))/10.0
        dp =_fx_num (row .get ("dp"))
        dt =str (row .get ("dt")or "")
        arrow ="▲"if dt =="high"else ("▼"if dt =="low"else "•")
        stamp =str (row .get ("t")or "")or stamp
        out +="◈ {}  `{}`  {} {}٪\n".format (label ,_fx_money (p ),arrow ,_fx_money (dp ))
    out +="\n✦ تومان  ·  {}".format (stamp or "live")
    return out

async def rate_controller (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None
    if not cmd :
        return
    text =" ".join (cmd .strip ().split ())
    if re .match (r"^(?:نرخ|ارز|rates?)$",text ,re .I ):
        data =await _fx_load ()
        if not data ["tg"]:
            return await safe_edit_message (message ,"**نرخ در دسترس نیست.**")
        return await safe_edit_message (message ,_fx_board (data ))
    m =FX_CMD_RE .match (text )
    if not m :
        return
    item =FX_ALIAS .get (m .group (1 ).lower ())or FX_ALIAS .get (m .group (1 ))
    if not item :
        return
    qty =_fx_num (m .group (2 ))if m .group (2 )else 1.0
    data =await _fx_load ()
    if not data ["tg"]:
        return await safe_edit_message (message ,"**نرخ در دسترس نیست.**")
    info =_fx_pick (data ,item )
    if info ["toman"]<=0 and info ["usd"]<=0 :
        return await safe_edit_message (message ,"**نرخ در دسترس نیست.**")
    await safe_edit_message (message ,_fx_card (item ,info ,qty ))

MUSIC_BOTS = ["melobot", "vkmusic_bot", "ahangify_bot", "moozikestan_bot",
              "BaRitmBot", "songdl_bot", "DeezerMusicBot"]
MUSIC_WAIT = 13.0

def _mu_norm (t ):
    t =str (t or "").lower ()
    for a ,b in (("ي","ی"),("ك","ک"),("أ","ا"),("إ","ا"),("آ","ا"),("ۀ","ه"),("ة","ه"),("ؤ","و")):
        t =t .replace (a ,b )
    t =re .sub (r"[\u200c\u200f\u200e\u064b-\u0652]+","",t )
    t =re .sub (r"[^0-9a-z\u0600-\u06ff]+"," ",t )
    return re .sub (r"\s+"," ",t ).strip ()

def _mu_text (r ):
    bits =[getattr (r ,"title","")or "",getattr (r ,"description","")or ""]
    doc =getattr (r ,"document",None )
    for at in (getattr (doc ,"attributes",None )or []):
        for k in ("title","performer","file_name"):
            v =getattr (at ,k ,None )
            if v :
                bits .append (str (v ))
    return _mu_norm (" ".join (bits ))

def _mu_label (r ):
    return (str (getattr (r ,"title","")or "")+" - "+str (getattr (r ,"description","")or "")).strip (" -")

_MU_F2E ={"ا":"a","آ":"a","ب":"b","پ":"p","ت":"t","ث":"s","ج":"j","چ":"c","ح":"h","خ":"x",
"د":"d","ذ":"z","ر":"r","ز":"z","ژ":"j","س":"s","ش":"c","ص":"s","ض":"z","ط":"t","ظ":"z",
"ع":"a","غ":"q","ف":"f","ق":"q","ک":"k","گ":"g","ل":"l","م":"m","ن":"n","و":"v","ه":"h","ی":"y"}

def _mu_skel (w ):
    out =""
    for ch in str (w or ""):
        out +=_MU_F2E .get (ch ,ch )
    out =out .replace ("kh","x").replace ("gh","q").replace ("sh","c").replace ("ch","c").replace ("zh","j")
    out =re .sub (r"[aeiouy]+","",out )
    return re .sub (r"(.)\1+",r"\1",out )

def _mu_sub (a ,b ):
    it =iter (b )
    return all (ch in it for ch in a )

def _mu_word_hit (w ,parts ):
    if any (w in p for p in parts ):
        return True
    sw =_mu_skel (w )
    if len (sw )<3 :
        return False
    for p in parts :
        sp =_mu_skel (p )
        if len (sp )<3 :
            continue
        if sw ==sp :
            return True
        if abs (len (sw )-len (sp ))<=1 and (_mu_sub (sw ,sp )or _mu_sub (sp ,sw )):
            return True
    return False

def _mu_score (r ,words ,query_norm =""):
    txt =_mu_text (r )
    if not txt :
        return 0
    parts =[p for p in txt .split (" ")if p ]
    sc =float (sum (1 for w in words if w and _mu_word_hit (w ,parts )))
    if _mu_noise_hit (txt ,query_norm ):
        sc -=0.6
    return sc

MUSIC_MIN_SEC = 45

def _mu_dur (r ):
    doc =getattr (r ,"document",None )
    for at in (getattr (doc ,"attributes",None )or []):
        d =getattr (at ,"duration",None )
        if d :
            return int (d )
    return 0

def _mu_is_voice (r ):
    if str (getattr (r ,"type","")or "").lower ()=="voice":
        return True
    doc =getattr (r ,"document",None )
    for at in (getattr (doc ,"attributes",None )or []):
        if getattr (at ,"voice",False ):
            return True
    return False

def _mu_audio_results (res ):
    out =[]
    short =0
    for r in (getattr (res ,"results",None )or []):
        t =str (getattr (r ,"type","")or "").lower ()
        if t not in ("audio","document"):
            continue
        if _mu_is_voice (r ):
            short +=1
            continue
        d =_mu_dur (r )
        if 0 <d <MUSIC_MIN_SEC :
            short +=1
            continue
        out .append (r )
    if short :
        logger .info ("music: dropped %d preview/voice result(s)",short )
    return out

async def _mu_search (client ,bot ,query ,tries =1 ):
    res =None
    for attempt in range (max (1 ,int (tries ))):
        try :
            res =await asyncio .wait_for (client .get_inline_bot_results (bot ,query ),timeout =MUSIC_WAIT )
            break
        except asyncio .TimeoutError :
            logger .info ("music: %s timeout (try %d)",bot ,attempt +1 )
            res =None
        except Exception as exc :
            logger .info ("music: %s search failed (%s)",bot ,type (exc ).__name__ )
            return None ,[]
    if res is None :
        return None ,[]
    picks =_mu_audio_results (res )
    if not picks :
        kinds =sorted (set (str (getattr (r ,"type","?"))for r in (getattr (res ,"results",None )or [])))
        logger .info ("music: %s no audio for %r (types=%s)",bot ,query [:40 ],",".join (kinds )or "none")
    return res ,picks

SC_CLIENT_ID = ""
SC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SC_NOISE = ("remix", "ریمیکس", "8d", "nightcore", "speed", "slowed", "reverb", "cover",
            "instrumental", "اینسترومنتال", "بیکلام", "بی کلام", "karaoke", "mashup", "mix show",
            "mixtape", "میکس", "podcast", "پادکست", "teaser", "demo", "گزارش", "رادیو", "best of",
            "remake", "bootleg", "flip", "edit", "sped", "tribute", "type beat", "beat",
            "بهترین های", "album", "البوم", "آلبوم")
SC_MAX_BYTES = 45 * 1024 * 1024

async def _sc_text (url ,timeout =20 ):
    session =await get_http_session ()
    async with session .get (url ,headers ={"User-Agent":SC_UA },timeout =aiohttp .ClientTimeout (total =timeout ))as r :
        return await r .text ()

async def _sc_client_id (force =False ):
    global SC_CLIENT_ID
    if SC_CLIENT_ID and not force :
        return SC_CLIENT_ID
    try :
        html =await _sc_text ("https://soundcloud.com/")
        for u in reversed (re .findall (r'src="(https://[^"]+\.js[^"]*)"',html )):
            try :
                js =await _sc_text (u ,15 )
            except Exception :
                continue
            m =re .search (r'client_id\s*:\s*"([a-zA-Z0-9]{32})"',js )
            if m :
                SC_CLIENT_ID =m .group (1 )
                logger .info ("music: soundcloud client_id refreshed")
                return SC_CLIENT_ID
    except Exception as exc :
        logger .info ("music: soundcloud id failed (%s)",type (exc ).__name__ )
    return SC_CLIENT_ID

YT_SEARCH_N = 15
YT_OPTS = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": True,
           "socket_timeout": 20, "noplaylist": True, "default_search": "ytsearch"}

def _yt_spellings (query ,words ):
    if YoutubeDL is None :
        return {}
    try :
        with YoutubeDL (YT_OPTS )as y :
            info =y .extract_info ("ytsearch%d:%s"%(YT_SEARCH_N ,query ),download =False )
    except Exception as exc :
        logger .info ("music: youtube spell failed (%s)",type (exc ).__name__ )
        return {}
    votes ={}
    for e in (info .get ("entries")or []):
        blob =_mu_norm (str (e .get ("title")or "")+" "+str (e .get ("uploader")or e .get ("channel")or ""))
        lat =[p for p in blob .split (" ")if p and len (p )>2 and re .match (r"^[a-z0-9]+$",p )]
        for w in words :
            for p in lat :
                if _mu_word_hit (w ,[p ]):
                    votes .setdefault (w ,{})
                    votes [w ][p ]=votes [w ].get (p ,0 )+1
    out ={}
    for w ,cand in votes .items ():
        best =sorted (cand .items (),key =lambda x :(-x [1 ],len (x [0 ])))[0 ]
        if best [1 ]>=2 :
            out [w ]=best [0 ]
    if out :
        logger .info ("music: spelling %s",out )
    return out

async def _sc_one (query ,limit ,retry =True ):
    cid =await _sc_client_id ()
    if not cid :
        return []
    url =("https://api-v2.soundcloud.com/search/tracks?q="+urllib .parse .quote (query )+
    "&client_id="+cid +"&limit="+str (int (limit )))
    try :
        return (json .loads (await _sc_text (url ,20 )).get ("collection")or [])
    except Exception :
        if retry :
            await _sc_client_id (True )
            return await _sc_one (query ,limit ,False )
        logger .info ("music: soundcloud search failed for %r",query [:30 ])
        return []

async def _sc_pool (queries ):
    pool ={}
    for q ,lim in queries :
        if not q :
            continue
        for t in await _sc_one (q ,lim ):
            pool .setdefault (t .get ("id"),t )
    out =[]
    for t in pool .values ():
        stream =""
        for tr in ((t .get ("media")or {}).get ("transcodings")or []):
            if (tr .get ("format")or {}).get ("protocol")=="progressive":
                stream =tr .get ("url")or ""
                break
        if not stream :
            continue
        dur =int ((t .get ("duration")or 0 )/1000 )
        if dur and dur <MUSIC_MIN_SEC :
            continue
        out .append ({"title":t .get ("title")or "","user":((t .get ("user")or {}).get ("username")or ""),
        "dur":dur ,"stream":stream ,"plays":int (t .get ("playback_count")or 0 )})
    return out

def _mu_noise_hit (text ,query_norm ):
    for bad in SC_NOISE :
        if bad in text and bad not in query_norm :
            return True
    return False

def _sc_score (t ,forms ,query_norm ):
    title =_mu_norm (str (t .get ("title","")))
    who =_mu_norm (str (t .get ("user","")))
    parts =[p for p in (title +" "+who ).split (" ")if p ]
    who_parts =[p for p in who .split (" ")if p ]
    sc =0.0
    for alts in forms :
        if any (_mu_word_hit (a ,parts )for a in alts ):
            sc +=1.0
        if any (_mu_word_hit (a ,who_parts )for a in alts ):
            sc +=0.25
    if _mu_noise_hit (title ,query_norm ):
        sc -=0.7
    if len (title .split (" "))>9 :
        sc -=0.4
    d =int (t .get ("dur")or 0 )
    if d >480 :
        sc -=0.6
    elif d and d <90 :
        sc -=0.3
    pl =int (t .get ("plays")or 0 )
    if pl >=50000 :
        sc +=0.4
    elif pl >=5000 :
        sc +=0.2
    elif pl <800 :
        sc -=0.5
    return sc

async def _sc_try (client ,chat_id ,query ,words ,need ,reply_to ):
    spell ={}
    if any (ord (c )>127 for c in query ):
        try :
            spell =await asyncio .wait_for (asyncio .to_thread (_yt_spellings ,query ,words ),timeout =25 )
        except Exception :
            spell ={}
    forms =[[w ]+([spell [w ]]if spell .get (w )else [])for w in words ]
    latin =" ".join (spell [w ]for w in words if spell .get (w ))
    queries =[(query ,25 )]
    if latin :
        queries .insert (0 ,(latin ,25 ))
    tracks =await _sc_pool (queries )
    if len (tracks )<5 and len (words )>1 :
        extra =[(spell .get (w )or w ,30 )for w in words if len (w )>2 ][:2 ]
        tracks =await _sc_pool (queries +extra )
    if not tracks :
        return False
    qn =_mu_norm (query )+" "+_mu_norm (latin )
    ranked =sorted (((_sc_score (t ,forms ,qn ),int (t .get ("plays")or 0 ),t )for t in tracks ),
    key =lambda x :(-x [0 ],-x [1 ]))
    logger .info ("music: soundcloud best=%.1f/%d from %d | %s",ranked [0 ][0 ],need ,len (tracks ),
    " || ".join ("%s(%dk)"%((t .get ("title")or "")[:32 ],int (t .get ("plays")or 0 )/1000 )for _s ,_p ,t in ranked [:3 ]))
    for sc ,_p ,t in ranked [:2 ]:
        if sc <need :
            break
        path =os .path .join (tempfile .gettempdir (),f"dsm_{int (time .time ()*1000 )}.mp3")
        try :
            if not await _sc_grab (t ,path ):
                continue
            await client .send_audio (chat_id ,path ,title =(t .get ("title")or "")[:64 ],
            performer =(t .get ("user")or "")[:64 ],duration =int (t .get ("dur")or 0 ),
            reply_to_message_id =reply_to )
            logger .info ("music: sent from soundcloud (%ds, %d plays)",int (t .get ("dur")or 0 ),int (t .get ("plays")or 0 ))
            return True
        except Exception as exc :
            logger .info ("music: soundcloud send failed (%s)",type (exc ).__name__ )
        finally :
            try :
                os .remove (path )
            except Exception :
                pass
    return False

async def _sc_grab (track ,path ):
    cid =await _sc_client_id ()
    if not cid :
        return False
    link =track ["stream"]+("&"if "?"in track ["stream"]else "?")+"client_id="+cid
    session =await get_http_session ()
    try :
        async with session .get (link ,headers ={"User-Agent":SC_UA },timeout =aiohttp .ClientTimeout (total =25 ))as r :
            j =json .loads (await r .text ())
        media =j .get ("url")
        if not media :
            return False
        total =0
        async with session .get (media ,headers ={"User-Agent":SC_UA },timeout =aiohttp .ClientTimeout (total =180 ))as r :
            if r .status !=200 :
                return False
            with open (path ,"wb")as f :
                async for chunk in r .content .iter_chunked (65536 ):
                    total +=len (chunk )
                    if total >SC_MAX_BYTES :
                        return False
                    f .write (chunk )
        return total >100000
    except Exception as exc :
        logger .info ("music: soundcloud download failed (%s)",type (exc ).__name__ )
        return False

MUSIC_CHANNELS = ["RapFarsi", "RadioJavan", "Bia2Music", "TehranMusic", "RapFa",
                  "music_rap_fa", "khalvat_music", "persian_music_channel"]

def _ch_text (msg ):
    a =getattr (msg ,"audio",None )
    if not a :
        return ""
    bits =[str (getattr (a ,"title","")or ""),str (getattr (a ,"performer","")or ""),
    str (getattr (a ,"file_name","")or ""),str (getattr (msg ,"caption","")or "")[:120 ]]
    return _mu_norm (" ".join (bits ))

async def _ch_try (client ,chat_id ,query ,words ,need ,reply_to ):
    qn =_mu_norm (query )
    best =None
    for ch in MUSIC_CHANNELS :
        hits =[]
        try :
            async for m in client .search_messages (ch ,query =query ,filter =MessagesFilter .AUDIO ,limit =12 ):
                hits .append (m )
        except Exception as exc :
            logger .info ("music: channel @%s failed (%s)",ch ,type (exc ).__name__ )
            continue
        for m in hits :
            a =getattr (m ,"audio",None )
            if not a :
                continue
            dur =int (getattr (a ,"duration",0 )or 0 )
            if dur and dur <MUSIC_MIN_SEC :
                continue
            txt =_ch_text (m )
            parts =[p for p in txt .split (" ")if p ]
            sc =float (sum (1 for w in words if _mu_word_hit (w ,parts )))
            if _mu_noise_hit (txt ,qn ):
                sc -=0.7
            if dur >480 :
                sc -=0.6
            if best is None or sc >best [0 ]:
                best =(sc ,ch ,m )
        if best and best [0 ]>=need :
            break
    if not best :
        logger .info ("music: channels found nothing for %r",query [:40 ])
        return False
    au =getattr (best [2 ],"audio",None )
    logger .info ("music: channels best=%.1f/%d @%s | %s - %s",best [0 ],need ,best [1 ],
    str (getattr (au ,"performer","")or "")[:22 ],str (getattr (au ,"title","")or "")[:34 ])
    if best [0 ]<need :
        return False
    try :
        await client .copy_message (chat_id ,best [2 ].chat .id ,best [2 ].id ,reply_to_message_id =reply_to )
        logger .info ("music: sent from channel @%s",best [1 ])
        return True
    except Exception as exc :
        logger .info ("music: channel copy failed (%s)",type (exc ).__name__ )
    return False

async def _mu_deliver (client ,chat_id ,res ,pick ,reply_to ):
    try :
        await client .send_inline_bot_result ("me",res .query_id ,pick .id )
        await asyncio .sleep (1.3 )
        async for msg in client .get_chat_history ("me",limit =1 ):
            au =getattr (msg ,"audio",None )
            ok =False
            if getattr (msg ,"voice",None ):
                ok =False
            elif au :
                dur =int (getattr (au ,"duration",0 )or 0 )
                ok =dur ==0 or dur >=MUSIC_MIN_SEC
                if not ok :
                    logger .info ("music: skipped %ds preview",dur )
            elif getattr (msg ,"document",None ):
                ok =True
            if ok :
                await client .copy_message (chat_id ,"me",msg .id ,reply_to_message_id =reply_to )
                try :
                    await msg .delete ()
                except Exception :
                    pass
                return True
            try :
                await msg .delete ()
            except Exception :
                pass
            return False
            break
    except Exception as exc :
        logger .info ("music: clean deliver failed (%s)",type (exc ).__name__ )
    try :
        await client .send_inline_bot_result (chat_id ,res .query_id ,pick .id ,reply_to_message_id =reply_to )
        return True
    except Exception as exc :
        logger .info ("music: direct deliver failed (%s)",type (exc ).__name__ )
    return False

async def _mu_from_chats (client ,chat_id ,query ,reply_to ):
    try :
        async for msg in client .search_global (query ,filter =MessagesFilter .AUDIO ,limit =6 ):
            try :
                await client .copy_message (chat_id ,msg .chat .id ,msg .id ,reply_to_message_id =reply_to )
                logger .info ("music: sent from chat archive")
                return True
            except Exception :
                continue
    except Exception as exc :
        logger .info ("music: archive search failed (%s)",type (exc ).__name__ )
    return False

async def music_controller (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None
    if not cmd :
        return
    m =re .match (r"^(?:آهنگ|اهنگ|موزیک|song|music)\s+(.+)$",cmd .strip (),re .I |re .S )
    if not m :
        return
    query =" ".join (m .group (1 ).split ())[:64 ]
    if not query :
        return
    words =[w for w in _mu_norm (query ).split (" ")if len (w )>1 ]
    need =len (words )if len (words )<=3 else max (3 ,len (words )-1 )
    reply_to =getattr (message ,"reply_to_message_id",None )
    if not reply_to :
        rm =getattr (message ,"reply_to_message",None )
        reply_to =getattr (rm ,"id",None )if rm else None
    status =await safe_edit_message (message ,"**◈ در حال گشتن...**")
    target =status or message
    is_fa =any (ord (c )>127 for c in query )
    if await _ch_try (client ,message .chat .id ,query ,words ,need ,reply_to ):
        try :
            await target .delete ()
        except Exception :
            pass
        return
    if is_fa and await _sc_try (client ,message .chat .id ,query ,words ,need ,reply_to ):
        try :
            await target .delete ()
        except Exception :
            pass
        return
    best =None
    for idx ,bot in enumerate (MUSIC_BOTS ):
        res ,picks =await _mu_search (client ,bot ,query ,tries =2 if idx ==0 else 1 )
        if not picks :
            continue
        ranked =sorted (((_mu_score (r ,words ,_mu_norm (query )),i ,r )for i ,r in enumerate (picks )),key =lambda x :(-x [0 ],x [1 ]))
        top =ranked [0 ]
        logger .info ("music: %s best=%.1f/%d | %s",bot ,top [0 ],need ,
        " || ".join (_mu_label (r )[:46 ]for _s ,_i ,r in ranked [:3 ]))
        for sc ,_i ,cand in ranked [:3 ]:
            if sc <need :
                break
            if await _mu_deliver (client ,message .chat .id ,res ,cand ,reply_to ):
                try :
                    await target .delete ()
                except Exception :
                    pass
                return
        if best is None or top [0 ]>best [0 ]:
            best =(top [0 ],res ,top [2 ])
    if not is_fa and await _sc_try (client ,message .chat .id ,query ,words ,need ,reply_to ):
        try :
            await target .delete ()
        except Exception :
            pass
        return
    if best and best [0 ]>=need -0.3 :
        logger .info ("music: fallback to near match score=%.1f",best [0 ])
        if await _mu_deliver (client ,message .chat .id ,best [1 ],best [2 ],reply_to ):
            try :
                await target .delete ()
            except Exception :
                pass
            return
    if await _mu_from_chats (client ,message .chat .id ,query ,reply_to ):
        try :
            await target .delete ()
        except Exception :
            pass
        return
    await safe_edit_message (target ,"**آهنگ پیدا نشد.**")

AVATAR_STATUS = {}
AVATAR_STYLE = {}
AVATAR_TEXT = {}
AVATAR_STAMP = {}
AVATAR_PREV = {}
AVATAR_EVERY = 10

AVATAR_STYLES = [
 {"p": ["04070C", "0A1424", "FFFFFF", "27E0FF"], "font": "Michroma.ttf", "fx": "neon",
  "tex": ["grid"], "ring": 1},
 {"p": ["000000", "0B0B0D", "FFFFFF", "9AA6B2"], "font": "ArchivoBlack.ttf", "fx": "chrome",
  "tex": [], "ring": 0},
 {"p": ["030302", "0D0B06", "E8C77B", "C9A227"], "font": "CinzelBold.ttf", "fx": "gold",
  "tex": [], "ring": 1},
 {"p": ["05050A", "0A0A14", "FFB3F0", "8FD9FF"], "font": "PoppinsBold.ttf", "fx": "holo",
  "tex": ["aurora"], "ring": 0},
 {"p": ["000000", "020A04", "CFFFE0", "21F37A"], "font": "SpaceMonoBold.ttf", "fx": "neon",
  "tex": ["rain"], "ring": 0},
 {"p": ["0A0518", "1B0B40", "F3E8FF", "A855F7"], "font": "Audiowide.ttf", "fx": "gradneon",
  "tex": ["grid"], "ring": 1},
 {"p": ["F3F3F1", "FFFFFF", "0B0B0B", "FF2D2D"], "font": "Anton.ttf", "fx": "flat",
  "tex": [], "ring": 1},
 {"p": ["0C0D0A", "141610", "D7FF3E", "8BE000"], "font": "Staatliches.ttf", "fx": "flat",
  "tex": ["dots"], "ring": 1},
]

def _av_date():
    now = datetime.now(TEHRAN_TIMEZONE)
    if jdatetime is not None:
        try:
            return jdatetime.datetime.fromgregorian(datetime=now).strftime("%Y/%m/%d")
        except Exception:
            pass
    return now.strftime("%Y/%m/%d")

def _av_render(style, tstr, dstr, sub, size=640):
    st = AVATAR_STYLES[(int(style) - 1) % len(AVATAR_STYLES)]
    W = H = int(size)
    bg, bg2, fg, ac = [_lg_hex(c) for c in st["p"]]
    img = _lg_bg_rad((W, H), bg2, bg)
    for t in st.get("tex", []) or []:
        if t == "grid":
            _lg_grid(img, ac + (28,), step=int(W / 14), width=1)
        elif t == "dots":
            _lg_dots(img, ac + (44,), step=int(W / 16), r=max(1, W // 320))
        elif t == "aurora":
            img = _lg_aurora(img, [ac, fg, _lg_mix(ac, fg, .5)], seed=int(style), alpha=.30)
        elif t == "rain":
            img = _lg_rain(img, ac, seed=int(style), cols=22)
    img = _lg_spot(img, _lg_mix(ac, (0, 0, 0), .86), pos=(.5, .44), rad=.48)

    cy = int(H * (.44 if sub else .46))
    mask, _, _ = _lg_fit_mask((W, H), tstr, st["font"], (int(W * .70), int(H * .26)),
                              (W // 2, cy), .02)
    fx = st.get("fx", "flat")
    if fx == "neon":
        img = _lg_glow(img, mask, ac, radius=int(W / 12), passes=3, boost=1.05)
        img = _lg_glow(img, mask, ac, radius=int(W / 46), passes=2, boost=1.2)
        _lg_paint(img, mask, fg)
    elif fx == "chrome":
        img = _lg_shadow(img, mask, (0, 0, 0), off=(int(W / 110), int(W / 85)), blur=int(W / 45), alpha=150)
        _lg_paint_multi(img, mask, [(255, 255, 255), (222, 236, 250), (110, 130, 152),
                                    (16, 20, 26), (172, 190, 208), (255, 255, 255)], 90)
        _lg_bevel(img, mask, max(2, W // 190), (255, 255, 255), (8, 10, 14), .85)
        _lg_sheen(img, mask, alpha=.5, pos=.32, width=.08)
    elif fx == "gold":
        img = _lg_extrude(img, mask, _lg_mix(ac, (0, 0, 0), .74), dx=1, dy=1, depth=max(4, W // 90), fade=.45)
        _lg_paint_multi(img, mask, [(255, 247, 216), (233, 200, 124), (137, 103, 40),
                                    (247, 227, 163), (200, 161, 57)], 92)
        _lg_bevel(img, mask, max(2, W // 200), (255, 251, 230), (84, 58, 12), .7)
        _lg_sheen(img, mask, alpha=.4, pos=.34)
    elif fx == "holo":
        img = _lg_glow(img, mask, _lg_mix(fg, ac, .5), radius=int(W / 18), passes=3, boost=.6)
        _lg_paint_multi(img, mask, [(255, 198, 242), (201, 167, 255), (143, 217, 255),
                                    (155, 255, 224)], 105)
        _lg_bevel(img, mask, max(2, W // 200), (255, 255, 255), _lg_mix(ac, (0, 0, 0), .55), .45)
    elif fx == "gradneon":
        k = max(2, W // 130)
        img = _lg_glow(img, ImageChops.offset(mask, -k, -k), fg, radius=int(W / 14), passes=3, boost=.95)
        img = _lg_glow(img, ImageChops.offset(mask, k, k), ac, radius=int(W / 14), passes=3, boost=.95)
        _lg_paint_multi(img, mask, [fg, _lg_mix(fg, ac, .5), ac], 105)
        _lg_paint(img, _lg_alpha(_lg_ring(mask, max(2, W // 300)), .5), (255, 255, 255))
    else:
        _lg_paint(img, mask, fg)
        _lg_bevel(img, mask, max(2, W // 170), _lg_mix(fg, (255, 255, 255), .8),
                  _lg_mix(fg, (0, 0, 0), .7), .5)

    dm, _, _ = _lg_fit_mask((W, H), dstr, "PoppinsLight.ttf", (int(W * .44), int(H * .045)),
                            (W // 2, int(H * .615)), .26)
    _lg_paint(img, dm, ac)
    if sub:
        sm, _, _ = _lg_fit_mask((W, H), str(sub)[:18], "PoppinsBold.ttf",
                                (int(W * .52), int(H * .05)), (W // 2, int(H * .725)), .20)
        _lg_paint(img, sm, _lg_mix(fg, bg, .30))
    if st.get("ring"):
        d = ImageDraw.Draw(img, "RGBA")
        r = int(W * .455)
        d.ellipse((W // 2 - r, H // 2 - r, W // 2 + r, H // 2 + r),
                  outline=ac + (110,), width=max(2, W // 190))
    img = _lg_grain(img, 10)
    return _lg_vig(img, .45)

async def _av_build (uid ):
    now =datetime .now (TEHRAN_TIMEZONE )
    style =int (AVATAR_STYLE .get (uid ,1 )or 1 )
    sub =AVATAR_TEXT .get (uid ,"")or ""
    img =await asyncio .to_thread (_av_render ,style ,now .strftime ("%H:%M"),_av_date (),sub ,640 )
    path =os .path .join (tempfile .gettempdir (),f"dsav_{uid }_{int (time .time ()*1000 )}.jpg")
    await asyncio .to_thread (lambda :img .save (path ,"JPEG",quality =93 ,subsampling =0 ,optimize =True ))
    return path ,now

async def _av_apply (client ,uid ):
    path ,now =await _av_build (uid )
    try :
        prev =AVATAR_PREV .get (uid )
        await client .set_profile_photo (photo =path )
        AVATAR_STAMP [uid ]=now .strftime ("%H:%M")
        try :
            async for p in client .get_chat_photos ("me",limit =1 ):
                AVATAR_PREV [uid ]=p .file_id
                data_manager .update_user_data (uid ,{"settings":{"avatar_prev":p .file_id }})
                break
        except Exception :
            pass
        if prev :
            try :
                await client .delete_profile_photos (prev )
            except Exception :
                pass
    finally :
        try :
            os .remove (path )
        except Exception :
            pass

async def _av_clear (client ,uid ):
    AVATAR_STAMP .pop (uid ,None )
    fid =AVATAR_PREV .get (uid )or ""
    if not fid :
        try :
            async for p in client .get_chat_photos ("me",limit =1 ):
                fid =p .file_id
                break
        except Exception :
            fid =""
    if not fid :
        return True
    try :
        await client .delete_profile_photos (fid )
        AVATAR_PREV .pop (uid ,None )
        data_manager .update_user_data (uid ,{"settings":{"avatar_prev":""}})
        logger .info ("avatar removed from profile for %s",uid )
        return True
    except FloodWait as fw :
        logger .info ("avatar remove flood-wait %ss for %s",getattr (fw ,"value",60 ),uid )
    except Exception as exc :
        logger .warning ("avatar remove failed for %s: %s",uid ,type (exc ).__name__ )
    AVATAR_PREV [uid ]=fid
    data_manager .update_user_data (uid ,{"settings":{"avatar_prev":fid }})
    return False

async def avatar_loop (client :Client ,uid :int ):
    while uid in ACTIVE_BOTS :
        try :
            if not AVATAR_STATUS .get (uid ,False ):
                if AVATAR_PREV .get (uid ):
                    await _av_clear (client ,uid )
                    await asyncio .sleep (300 )
                else :
                    await asyncio .sleep (20 )
                continue
            if not SELF_ACTIVE_STATUS .get (uid ,True )or COPY_MODE_STATUS .get (uid ,False ):
                await asyncio .sleep (30 )
                continue
            now =datetime .now (TEHRAN_TIMEZONE )
            if now .strftime ("%H:%M")!=AVATAR_STAMP .get (uid ):
                await _av_apply (client ,uid )
            nw =datetime .now (TEHRAN_TIMEZONE )
            wait =(AVATAR_EVERY -(nw .minute %AVATAR_EVERY ))*60 -nw .second +2
            if wait <45 :
                wait +=AVATAR_EVERY *60
            await asyncio .sleep (wait )
        except asyncio .CancelledError :
            break
        except FloodWait as fw :
            logger .info ("avatar flood-wait %ss for %s",getattr (fw ,"value",60 ),uid )
            AVATAR_STAMP .pop (uid ,None )
            await asyncio .sleep (getattr (fw ,"value",60 )+5 )
        except Exception :
            await asyncio .sleep (90 )

async def avatar_controller (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None
    if not cmd :
        return
    m =re .match (r"^(?:آواتار|اواتار|avatar)(?:\s+(.+))?$",cmd .strip (),re .I |re .S )
    if not m :
        return
    if Image is None :
        return await safe_edit_message (message ,"**کتابخانه تصویر روی سرور نصب نیست.**")
    arg =" ".join ((m .group (1 )or "").split ())
    m2 =re .match (r"^(?:طرح|style)\s+(\S+)$",arg ,re .I )
    if m2 :
        t =_pemoji_norm_digit (m2 .group (1 ))
        if not t .isdigit ():
            return await safe_edit_message (message ,"**شماره طرح رو درست بنویس.**")
        n =max (1 ,min (int (t ),len (AVATAR_STYLES )))
        AVATAR_STYLE [uid ]=n
        data_manager .update_user_data (uid ,{"settings":{"avatar_style":n }})
        AVATAR_STAMP .pop (uid ,None )
        return await safe_edit_message (message ,f"**◈ طرح {n } ثبت شد.**")
    m3 =re .match (r"^(?:متن|text)\s+(.+)$",arg ,re .I |re .S )
    if m3 :
        t =m3 .group (1 ).strip ()[:18 ]
        AVATAR_TEXT [uid ]=t
        data_manager .update_user_data (uid ,{"settings":{"avatar_text":t }})
        AVATAR_STAMP .pop (uid ,None )
        return await safe_edit_message (message ,"**◈ متن آواتار ثبت شد.**")
    status =await safe_edit_message (message ,"**◈ در حال ساخت آواتار...**")
    target =status or message
    path =None
    try :
        path ,_now =await _av_build (uid )
        await client .send_photo (message .chat .id ,path )
        try :
            await target .delete ()
        except Exception :
            pass
    except Exception as exc :
        logger .warning ("avatar preview failed: %s: %s",type (exc ).__name__ ,str (exc )[:140 ])
        await safe_edit_message (target ,"**ساخت آواتار ناموفق بود.**")
    finally :
        try :
            if path :
                os .remove (path )
        except Exception :
            pass

LOGO_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_LG_FONT_CACHE = {}
_LG_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def _lg_font(name, size):
    size = max(6, int(size))
    key = (name, size)
    f = _LG_FONT_CACHE.get(key)
    if f is not None:
        return f
    try:
        f = ImageFont.truetype(os.path.join(LOGO_FONT_DIR, name), size)
    except Exception:
        try:
            f = ImageFont.truetype(_LG_DEJAVU, size)
        except Exception:
            f = ImageFont.load_default()
    _LG_FONT_CACHE[key] = f
    return f

def _lg_hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _lg_mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def _lg_bg_solid(sz, c):
    return Image.new("RGB", sz, c)

def _lg_bg_lin(sz, c1, c2, angle=90):
    return _lg_grad_multi(sz, [c1, c2], angle)

def _lg_bg_rad(sz, inner, outer, pos=(0.5, 0.5), rad=0.85):
    w, h = sz
    base = Image.new("RGB", sz, outer)
    n = 300
    grad = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(grad)
    for i in range(n, 0, -2):
        v = int(255 * (1 - i / float(n)) ** 1.5)
        d.ellipse(((n - i) / 2, (n - i) / 2, (n + i) / 2, (n + i) / 2), fill=v)
    r = int(max(w, h) * rad * 2)
    grad = grad.resize((r, r), Image.BICUBIC)
    mask = Image.new("L", sz, 0)
    mask.paste(grad, (int(w * pos[0] - r / 2), int(h * pos[1] - r / 2)))
    base.paste(Image.new("RGB", sz, inner), (0, 0), mask)
    return base

def _lg_grid(img, line, step=54, width=1):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    for x in range(0, w + step, step):
        d.line((x, 0, x, h), fill=line, width=width)
    for y in range(0, h + step, step):
        d.line((0, y, w, y), fill=line, width=width)
    return img

def _lg_dots(img, dot, step=48, r=2):
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(step // 2, img.width, step):
        for y in range(step // 2, img.height, step):
            d.ellipse((x - r, y - r, x + r, y + r), fill=dot)
    return img

def _lg_stripes(img, col, step=64, width=18, angle=45):
    w, h = img.size
    lay = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(-lay.height, lay.width, step):
        d.line((i, 0, i + lay.height, lay.height), fill=col, width=width)
    if angle != 45:
        lay = lay.rotate(angle - 45, resample=Image.BICUBIC)
    lay = lay.crop(((lay.width - w) // 2, (lay.height - h) // 2, (lay.width - w) // 2 + w, (lay.height - h) // 2 + h))
    img.paste(lay, (0, 0), lay)
    return img

def _lg_scan(img, col, step=5):
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(0, img.height, step):
        d.line((0, y, img.width, y), fill=col, width=1)
    return img

def _lg_blobs(img, cols, blur=170, seed=1):
    rnd = random.Random(seed)
    w, h = img.size
    lay = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(lay)
    for c in cols:
        cx = rnd.randint(int(w * .15), int(w * .85))
        cy = rnd.randint(int(h * .15), int(h * .85))
        r = rnd.randint(int(w * .24), int(w * .42))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    return ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(blur)))

def _lg_grain(img, amount=10):
    n = Image.effect_noise(img.size, 30).convert("L").point(lambda v: int(v * amount / 100.0))
    return ImageChops.add(img, Image.merge("RGB", (n, n, n)))

def _lg_vig(img, strength=0.7):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    r = int(min(w, h) * .82)
    d.ellipse(((w - r) / 2, (h - r) / 2, (w + r) / 2, (h + r) / 2), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(int(min(w, h) * .16)))
    return Image.composite(img, Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), strength), m)

_LG_RTL_FONT = "Vazir.ttf"

def _lg_is_rtl(t):
    for ch in t or "":
        o = ord(ch)
        if 0x0590 <= o <= 0x08FF or 0xFB50 <= o <= 0xFDFF or 0xFE70 <= o <= 0xFEFF:
            return True
    return False

try:
    from PIL import features as _lg_pil_features
    _LG_RAQM = bool(_lg_pil_features.check("raqm"))
except Exception:
    _LG_RAQM = False

def _lg_shape_rtl(t):
    if _LG_RAQM:
        return t
    if arabic_reshaper is not None and get_display is not None:
        try:
            return get_display(arabic_reshaper.reshape(t))
        except Exception:
            return t
    return t

def _lg_measure(fname, fsize, text, track, rtl=False):
    if not text:
        return 0, 0, 0
    f = _lg_font(fname, fsize)
    tmp = ImageDraw.Draw(Image.new("L", (8, 8)))
    if rtl:
        w = tmp.textlength(text, font=f)
    else:
        w = 0.0
        for ch in text:
            w += tmp.textlength(ch, font=f) + track
        w = max(0.0, w - track)
    bb = f.getbbox(text)
    return w, bb[1], bb[3]

def _lg_fit_font(fname, text, max_w, max_h, track_ratio=0.0, hi=560, rtl=False):
    lo, best = 8, 8
    while lo <= hi:
        mid = (lo + hi) // 2
        w, y0, y1 = _lg_measure(fname, mid, text, mid * track_ratio, rtl)
        if w <= max_w and (y1 - y0) <= max_h:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best, best * track_ratio

def _lg_text_mask(size, text, fname, fsize, track, center, rtl=False):
    s = 2
    w, h = size
    layer = Image.new("L", (w * s, h * s), 0)
    d = ImageDraw.Draw(layer)
    f = _lg_font(fname, fsize * s)
    tw, y0, y1 = _lg_measure(fname, fsize * s, text, track * s, rtl)
    x = center[0] * s - tw / 2.0
    y = center[1] * s - (y0 + y1) / 2.0
    if rtl:
        d.text((x, y), text, font=f, fill=255)
    else:
        for ch in text:
            d.text((x, y), ch, font=f, fill=255)
            x += d.textlength(ch, font=f) + track * s
    return layer.resize((w, h), Image.LANCZOS)

def _lg_fit_mask(size, text, fname, box, center, track_ratio=0.0):
    rtl = _lg_is_rtl(text)
    if rtl:
        fname = _LG_RTL_FONT
        track_ratio = 0.0
        text = _lg_shape_rtl(text)
    fs, tr = _lg_fit_font(fname, text, box[0], box[1], track_ratio, rtl=rtl)
    return _lg_text_mask(size, text, fname, fs, tr, center, rtl), fs, tr

def _lg_paint(img, mask, color):
    img.paste(Image.new("RGB", img.size, color), (0, 0), mask)
    return img

def _lg_paint_grad(img, mask, c1, c2, angle=90):
    img.paste(_lg_bg_lin(img.size, c1, c2, angle), (0, 0), mask)
    return img

def _lg_ring(mask, px=6):
    m = mask
    for _ in range(max(1, int(px / 2))):
        m = m.filter(ImageFilter.MaxFilter(5))
    return ImageChops.subtract(m, mask)

def _lg_glow(img, mask, color, radius=40, passes=3, boost=1.0):
    lay = Image.new("RGB", img.size, (0, 0, 0))
    lay.paste(Image.new("RGB", img.size, color), (0, 0), mask)
    out = img
    for i in range(passes):
        b = lay.filter(ImageFilter.GaussianBlur(radius * (i + 1) / float(passes)))
        if boost != 1.0:
            b = b.point(lambda v: min(255, int(v * boost)))
        out = ImageChops.screen(out, b)
    return out

def _lg_shadow(img, mask, color=(0, 0, 0), off=(12, 14), blur=20, alpha=160):
    m = ImageChops.offset(mask, off[0], off[1]).filter(ImageFilter.GaussianBlur(blur))
    m = m.point(lambda v: int(v * alpha / 255.0))
    img.paste(Image.new("RGB", img.size, color), (0, 0), m)
    return img

def _lg_extrude(img, mask, color, dx=1, dy=1, depth=24, fade=0.5):
    for i in range(depth, 0, -1):
        m = ImageChops.offset(mask, dx * i, dy * i)
        img.paste(Image.new("RGB", img.size, _lg_mix(color, (0, 0, 0), fade * i / float(depth))), (0, 0), m)
    return img

def _lg_rgbsplit(img, mask, dx=8):
    r = Image.new("RGB", img.size, (255, 40, 60))
    c = Image.new("RGB", img.size, (0, 230, 255))
    img.paste(r, (0, 0), ImageChops.offset(mask, -dx, 0))
    img.paste(c, (0, 0), ImageChops.offset(mask, dx, 0))
    return img

def _lg_ramp(stops, n=512):
    g = Image.new("RGB", (1, int(n)))
    px = g.load()
    k = max(1, len(stops) - 1)
    for y in range(int(n)):
        t = y / (n - 1.0) * k
        i = min(k - 1, int(t))
        px[0, y] = _lg_mix(stops[i], stops[i + 1], t - i)
    return g

def _lg_grad_multi(sz, stops, angle=90):
    w, h = max(2, int(sz[0])), max(2, int(sz[1]))
    if len(stops) < 2:
        return Image.new("RGB", (w, h), stops[0])
    th = math.radians(angle - 90)
    g = _lg_ramp(stops)
    if abs(math.sin(th)) < 1e-3:
        return g.resize((w, h), Image.BICUBIC)
    ext = max(2, int(abs(w * math.sin(th)) + abs(h * math.cos(th))) + 2)
    span = int(math.hypot(w, h)) + 4
    g = g.resize((span, ext), Image.BICUBIC).rotate(angle - 90, resample=Image.BICUBIC, expand=True)
    x0 = (g.width - w) // 2
    y0 = (g.height - h) // 2
    return g.crop((x0, y0, x0 + w, y0 + h))

def _lg_paint_multi(img, mask, stops, angle=90):
    bb = mask.getbbox()
    if not bb:
        return img
    w = max(2, bb[2] - bb[0])
    h = max(2, bb[3] - bb[1])
    lay = Image.new("RGB", img.size, stops[-1])
    lay.paste(_lg_grad_multi((w, h), stops, angle), (bb[0], bb[1]))
    img.paste(lay, (0, 0), mask)
    return img

def _lg_alpha(mask, a):
    a = max(0.0, min(1.0, a))
    return mask.point(lambda v: int(v * a))

def _lg_bevel(img, mask, k, light=(255, 255, 255), dark=(0, 0, 0), a=.55):
    k = max(1, int(k))
    hi = ImageChops.multiply(ImageChops.subtract(mask, ImageChops.offset(mask, k, k)), mask)
    lo = ImageChops.multiply(ImageChops.subtract(mask, ImageChops.offset(mask, -k, -k)), mask)
    hi = _lg_alpha(hi.filter(ImageFilter.GaussianBlur(k * .7)), a)
    lo = _lg_alpha(lo.filter(ImageFilter.GaussianBlur(k * .7)), a)
    img.paste(Image.new("RGB", img.size, light), (0, 0), hi)
    img.paste(Image.new("RGB", img.size, dark), (0, 0), lo)
    return img

def _lg_sheen(img, mask, alpha=.4, pos=.38, width=.14, color=(255, 255, 255)):
    w, h = img.size
    lay = Image.new("L", (w * 2, h * 2), 0)
    d = ImageDraw.Draw(lay)
    y = int(h * 2 * pos)
    d.line((0, y + int(w * .55), w * 2, y - int(w * .55)), fill=255, width=int(h * width * 2))
    lay = lay.filter(ImageFilter.GaussianBlur(int(h * width * .45)))
    lay = lay.crop((w // 2, h // 2, w // 2 + w, h // 2 + h))
    img.paste(Image.new("RGB", img.size, color), (0, 0), _lg_alpha(ImageChops.multiply(lay, mask), alpha))
    return img

def _lg_spot(img, color, pos=(.5, .46), rad=.60, alpha=1.0):
    w, h = img.size
    lay = Image.new("RGB", img.size, (0, 0, 0))
    r = int(min(w, h) * rad)
    c = tuple(int(v * alpha) for v in color)
    ImageDraw.Draw(lay).ellipse((w * pos[0] - r, h * pos[1] - r, w * pos[0] + r, h * pos[1] + r), fill=c)
    return ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(int(r * .6))))

def _lg_aurora(img, cols, seed=1, alpha=.8):
    rnd = random.Random(seed)
    w, h = img.size
    lay = Image.new("RGB", img.size, (0, 0, 0))
    d = ImageDraw.Draw(lay)
    spots = [(.18, .20), (.83, .26), (.26, .82), (.78, .78), (.52, .48)]
    for i, c in enumerate(cols):
        px, py = spots[i % len(spots)]
        px += rnd.uniform(-.07, .07)
        py += rnd.uniform(-.07, .07)
        r = int(w * rnd.uniform(.28, .44))
        cc = tuple(int(v * alpha) for v in c)
        d.ellipse((w * px - r, h * py - r, w * px + r, h * py + r), fill=cc)
    return ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(int(w / 5))))

def _lg_beams(img, col, seed=1):
    rnd = random.Random(seed)
    w, h = img.size
    lay = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(3):
        x = rnd.randint(int(-w * .2), int(w * 1.1))
        wd = rnd.randint(int(w * .06), int(w * .16))
        c = tuple(int(v * rnd.uniform(.25, .55)) for v in col)
        d.polygon([(x, 0), (x + wd, 0), (x + wd + int(w * .45), h), (x + int(w * .45), h)], fill=c)
    return ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(int(w / 22))))

def _lg_stars(img, n=90, seed=3, col=(255, 255, 255)):
    rnd = random.Random(seed)
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    u = max(1, w // 900)
    for _ in range(int(n)):
        x, y = rnd.randint(0, w), rnd.randint(0, h)
        r = rnd.choice([1, 1, 1, 2, 2, 3]) * u
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (rnd.randint(60, 235),))
    return img

def _lg_rain(img, col, seed=1, cols=30):
    rnd = random.Random(seed)
    w, h = img.size
    lay = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(lay)
    step = max(6, w // cols)
    for x in range(step // 2, w, step):
        y = rnd.randint(int(-h * .4), int(h * .8))
        ln = rnd.randint(int(h * .18), int(h * .55))
        seg = max(4, ln // 22)
        for i in range(0, ln, seg):
            t = i / float(ln)
            c = tuple(int(v * (0.12 + .75 * t)) for v in col)
            d.line((x, y + i, x, y + i + seg), fill=c, width=max(1, w // 420))
    return ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(max(1, w // 600))))

def _lg_sparkle(img, col, n=6, seed=2):
    rnd = random.Random(seed)
    w, h = img.size
    lay = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(int(n)):
        x, y = rnd.randint(int(w * .08), int(w * .92)), rnd.randint(int(h * .08), int(h * .92))
        r = rnd.randint(int(w * .015), int(w * .05))
        t = max(1, int(r * .12))
        d.line((x - r, y, x + r, y), fill=col, width=t)
        d.line((x, y - r, x, y + r), fill=col, width=t)
        d.ellipse((x - t, y - t, x + t, y + t), fill=col)
    return ImageChops.screen(img, lay.filter(ImageFilter.GaussianBlur(max(1, w // 400))))

def _lg_horizon(img, col, y_ratio=.66, width=3, rays=13):
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    hy = int(h * y_ratio)
    cx = w // 2
    for i in range(-rays, rays + 1):
        d.line((cx + i * (w // (rays * 8)), hy, cx + i * (w // 4), h), fill=col, width=width)
    y = hy
    step = max(3, int((h - hy) * .045))
    while y < h:
        d.line((0, y, w, y), fill=col, width=width)
        y += step
        step = int(step * 1.45) + 2
    return img

def _lg_sun(img, stops, pos=(.5, .40), r=.28, cut=True):
    w, h = img.size
    R = int(w * r)
    cx, cy = int(w * pos[0]), int(h * pos[1])
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
    if cut:
        y = cy + int(R * .12)
        t = max(3, R // 18)
        while y < cy + R:
            d.rectangle((cx - R, y, cx + R, y + t), fill=0)
            y += int(t * 2.4)
            t = int(t * 1.3) + 1
    _lg_paint_multi(img, m, stops, 90)
    return img

def _lg_glass(img, box, radius, tint=(255, 255, 255), a=44, bw=3):
    x0, y0, x1, y1 = [int(v) for v in box]
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(img.width, x1)
    y1 = min(img.height, y1)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return img
    region = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(int(img.width / 26)))
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=radius, fill=255)
    img.paste(region, (x0, y0), m)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle((x0, y0, x1, y1), radius=radius,
                                         fill=tint + (a,), outline=tint + (120,), width=bw)
    img.paste(ov, (0, 0), ov)
    return img

def _lg_d_frame(img, col, inset=0.085, w=6, radius=0):
    d = ImageDraw.Draw(img)
    p = int(img.width * inset)
    box = (p, p, img.width - p, img.height - p)
    if radius:
        d.rounded_rectangle(box, radius=radius, outline=col, width=w)
    else:
        d.rectangle(box, outline=col, width=w)
    return img

def _lg_d_box(img, bbox, col, pad=(46, 30), w=10, radius=0, fill=None):
    d = ImageDraw.Draw(img)
    box = (bbox[0] - pad[0], bbox[1] - pad[1], bbox[2] + pad[0], bbox[3] + pad[1])
    if radius:
        d.rounded_rectangle(box, radius=radius, outline=col, width=w, fill=fill)
    else:
        d.rectangle(box, outline=col, width=w, fill=fill)
    return img

def _lg_d_rules(img, bbox, col, w=5, gap=46, span=0.74):
    d = ImageDraw.Draw(img)
    x0 = int(img.width * (1 - span) / 2)
    x1 = img.width - x0
    d.line((x0, bbox[1] - gap, x1, bbox[1] - gap), fill=col, width=w)
    d.line((x0, bbox[3] + gap, x1, bbox[3] + gap), fill=col, width=w)
    return img

def _lg_d_bar(img, bbox, col, w=16, gap=34, span=0.42):
    d = ImageDraw.Draw(img)
    cx = img.width // 2
    half = int(img.width * span / 2)
    y = bbox[3] + gap
    d.line((cx - half, y, cx + half, y), fill=col, width=w)
    return img

def _lg_d_brackets(img, col, inset=0.075, arm=0.10, w=7):
    d = ImageDraw.Draw(img)
    p = int(img.width * inset)
    a = int(img.width * arm)
    W, H = img.size
    for (x, y, dx, dy) in ((p, p, 1, 1), (W - p, p, -1, 1), (p, H - p, 1, -1), (W - p, H - p, -1, -1)):
        d.line((x, y, x + a * dx, y), fill=col, width=w)
        d.line((x, y, x, y + a * dy), fill=col, width=w)
    return img

def _lg_d_circle(img, col, r=0.40, w=5):
    d = ImageDraw.Draw(img)
    R = int(img.width * r)
    cx, cy = img.width // 2, img.height // 2
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=col, width=w)
    return img

def _lg_d_tape(img, bbox, col, pad=34):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, bbox[1] - pad, img.width, bbox[3] + pad), fill=col)
    return img

def _lg_d_card(img, col, inset=0.10, radius=46):
    d = ImageDraw.Draw(img, "RGBA")
    p = int(img.width * inset)
    d.rounded_rectangle((p, p, img.width - p, img.height - p), radius=radius, fill=col)
    return img

def _lg_d_crosses(img, col, inset=0.085, s=16, w=5):
    d = ImageDraw.Draw(img)
    p = int(img.width * inset)
    W, H = img.size
    for (x, y) in ((p, p), (W - p, p), (p, H - p), (W - p, H - p)):
        d.line((x - s, y, x + s, y), fill=col, width=w)
        d.line((x, y - s, x, y + s), fill=col, width=w)
    return img

def _lg_pal(bg, bg2, fg, ac, ac2=None):
    return {"bg": _lg_hex(bg), "bg2": _lg_hex(bg2), "fg": _lg_hex(fg), "ac": _lg_hex(ac), "ac2": _lg_hex(ac2 or ac)}

LOGO_STYLES = [
 
 {"p": _lg_pal("050505", "101010", "FBC3DA", "F7A8C4", "FF7AB8"), "bgk": "rad", "tex": ["spot"], "font": "Anton.ttf",
  "case": "up", "track": .06, "fx": "flat", "bev": 1, "decor": "box", "sub": ("script", "GreatVibes.ttf"),
  "grain": 1, "vig": 1},
 
 {"p": _lg_pal("03060B", "04090F", "EAFDFF", "27E0FF", "0A84FF"), "bgk": "rad", "tex": ["grid", "spot"],
  "font": "Michroma.ttf", "case": "up", "track": .10, "fx": "gradneon",
  "grad": ["DFFCFF", "43E7FF", "1E8BFF"], "decor": "brackets", "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("F6F6F4", "FFFFFF", "0B0B0B", "FF2D2D"), "bgk": "lin:100", "font": "Anton.ttf", "case": "up",
  "track": .02, "fx": "soft", "decor": "bar", "sub": ("track", "PoppinsBold.ttf")},
 
 {"p": _lg_pal("000000", "0B0B0D", "FFFFFF", "9AA6B2"), "bgk": "rad", "tex": ["spot"], "font": "ArchivoBlack.ttf",
  "case": "up", "track": .03, "fx": "chrome", "decor": None, "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("08080A", "0C0C10", "FFFFFF", "FF2E63", "00E7FF"), "bgk": "solid", "tex": ["scan"],
  "font": "ArchivoBlack.ttf", "case": "up", "track": .04, "fx": "glitch", "decor": "crosses",
  "sub": ("mono", "SpaceMonoBold.ttf")},
 
 {"p": _lg_pal("040403", "0B0A07", "E8C77B", "C9A227", "F6E3A1"), "bgk": "rad", "tex": ["spot"],
  "font": "CinzelBold.ttf", "case": "up", "track": .16, "fx": "gold", "decor": "frame",
  "sub": ("track", "CinzelBold.ttf"), "vig": 1, "grain": 1},
 
 {"p": _lg_pal("0A0410", "1A0830", "FF6FD8", "FF3DAE", "7B61FF"), "bgk": "rad", "tex": ["scan", "spot"],
  "font": "Monoton.ttf", "case": "up", "track": .04, "fx": "gradneon",
  "grad": ["FFC2F0", "FF54C0", "8A63FF"], "decor": None, "sub": ("script", "Parisienne.ttf"), "vig": 1},
 
 {"p": _lg_pal("02050A", "03070C", "D9FFE9", "39FF9E", "00C46A"), "bgk": "solid", "tex": ["scan", "grid"],
  "font": "SpaceMonoBold.ttf", "case": "up", "track": .06, "fx": "neon", "decor": "brackets",
  "sub": ("mono", "SpaceMonoBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("120A2C", "2E1570", "FFFFFF", "A855F7", "22D3EE"), "bgk": "lin:120", "tex": ["beams"],
  "font": "ArchivoBlack.ttf", "case": "up", "track": .02, "fx": "bevel3d",
  "grad": ["FFFFFF", "E9D5FF", "A78BFA"], "decor": None, "sub": ("track", "PoppinsBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("0C0D0A", "121410", "D7FF3E", "D7FF3E", "8BE000"), "bgk": "rad", "tex": ["dots"],
  "font": "Staatliches.ttf", "case": "up", "track": .08, "fx": "flat", "bev": 1, "decor": "brackets",
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("040404", "0C0C0C", "FFFFFF", "FFFFFF"), "bgk": "rad", "tex": ["spot"], "font": "GreatVibes.ttf",
  "case": "as", "track": 0, "fx": "softneon", "decor": "rules", "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("EEE7DA", "F9F5EC", "141414", "9A7B45"), "bgk": "lin:100", "font": "PlayfairBold.ttf", "case": "up",
  "track": .12, "fx": "soft", "decor": "rules", "sub": ("script", "Sacramento.ttf")},
 
 {"p": _lg_pal("050509", "08080F", "FFB3F0", "8FD9FF", "C9A7FF"), "bgk": "rad", "tex": ["aurora"],
  "font": "PoppinsBold.ttf", "case": "up", "track": .05, "fx": "holo",
  "grad": ["FF9BEA", "B07CFF", "6FD2FF", "7BFFD4", "FFCE84"], "decor": None,
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("FF7A45", "FFC46B", "FFFFFF", "48180A"), "bgk": "lin:135", "tex": ["beams"], "font": "Bebas.ttf",
  "case": "up", "track": .05, "fx": "longshadow", "decor": None, "sub": ("track", "PoppinsBold.ttf")},
 
 {"p": _lg_pal("05142A", "0B2A52", "DCEBFF", "6FB0FF", "A7D2FF"), "bgk": "lin:100", "tex": ["grid"],
  "font": "RajdhaniBold.ttf", "case": "up", "track": .10, "fx": "outline",
  "grad": ["FFFFFF", "EAF4FF", "A9CEFF"], "decor": "crosses", "sub": ("mono", "SpaceMonoBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("0A0A0A", "0F0F0F", "FFFFFF", "E11D2E"), "bgk": "solid", "tex": ["stripes"], "font": "Anton.ttf",
  "case": "up", "track": .03, "fx": "flat", "decor": "tape", "sub": None, "grain": 1, "vig": 1},
 
 {"p": _lg_pal("FFFFFF", "F1F1F1", "111111", "111111"), "bgk": "lin:100", "font": "PoppinsLight.ttf", "case": "up",
  "track": .34, "fx": "soft", "decor": "rules", "sub": None},
 
 {"p": _lg_pal("050505", "0B0B0D", "FFFFFF", "FFFFFF", "7DD3FC"), "bgk": "rad", "tex": ["spot"], "font": "Anton.ttf",
  "case": "up", "track": .05, "fx": "outline", "grad": ["FFFFFF", "E6F5FF", "8FD0FF"], "decor": "frame",
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("A8C4E6", "E9F3FF", "FFFFFF", "35597C", "9AB8DA"), "bgk": "lin:120", "tex": ["blobs"],
  "font": "PoppinsBold.ttf", "case": "up", "track": .04, "fx": "glass", "decor": None,
  "sub": ("script", "Sacramento.ttf")},
 
 {"p": _lg_pal("090301", "1E0702", "FFD166", "FF4D00", "FFB020"), "bgk": "rad", "tex": ["spot", "sparkle"],
  "font": "Anton.ttf", "case": "up", "track": .03, "fx": "firegrad", "decor": None,
  "sub": ("track", "PoppinsBold.ttf"), "vig": 1, "grain": 1},
 
 {"p": _lg_pal("03080F", "081A2C", "FFFFFF", "49C8F5", "BFEFFF"), "bgk": "rad", "tex": ["spot", "sparkle"],
  "font": "PoppinsBold.ttf", "case": "up", "track": .05, "fx": "icegrad", "decor": None,
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("15042B", "3A0A5E", "FFFFFF", "FF48C4", "3EE8FF"), "bgk": "lin:90", "tex": ["sun", "horizon"],
  "sunpos": (.5, .30), "sunr": .21, "cy": .555, "font": "Audiowide.ttf", "case": "up", "track": .06, "fx": "holo",
  "grad": ["FFFFFF", "FFD1F4", "FF5FD0", "9B7BFF", "3EE8FF"], "decor": None,
  "sub": ("track", "PoppinsBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("120611", "220A22", "FFFFFF", "FF7AD9", "FFC2EF"), "bgk": "rad", "tex": ["sparkle", "spot"],
  "font": "ArchivoBlack.ttf", "case": "up", "track": .03, "fx": "chrome",
  "grad": ["FFFFFF", "FFD9F3", "C45BA8", "3A0F33", "FFB3E6", "FFFFFF"], "decor": None,
  "sub": ("script", "Parisienne.ttf"), "vig": 1},
 
 {"p": _lg_pal("111113", "1A1A1E", "0A0A0A", "FFFFFF", "D4D4D8"), "bgk": "rad", "font": "Bebas.ttf", "case": "up",
  "track": .14, "fx": "badge", "grad": ["FFFFFF", "D8D8DE"], "decor": None,
  "sub": ("track", "PoppinsLight.ttf"), "grain": 1, "vig": 1},
 
 {"p": _lg_pal("07070B", "0D0D14", "FFFFFF", "FF2E8B", "22D3EE"), "bgk": "rad", "tex": ["spot"],
  "font": "ArchivoBlack.ttf", "case": "up", "track": .03, "fx": "duotone", "decor": None,
  "sub": ("track", "PoppinsBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("021012", "04201F", "D7FFF8", "0FF3C0", "00A3FF"), "bgk": "rad", "tex": ["grid", "spot"],
  "font": "RajdhaniBold.ttf", "case": "up", "track": .12, "fx": "gradneon",
  "grad": ["E8FFFA", "19F2C2", "0094FF"], "decor": "brackets", "sub": ("mono", "SpaceMonoBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("000000", "0C0C0E", "3E3E42", "6E6E76"), "bgk": "rad", "font": "Anton.ttf", "case": "up",
  "track": .07, "fx": "flat", "bev": 1, "decor": "frame", "sub": ("track", "PoppinsLight.ttf"), "grain": 1},
 
 {"p": _lg_pal("060504", "0E0B07", "F3DCA0", "B9922F", "FFF0C4"), "bgk": "rad", "tex": ["grain", "spot"],
  "font": "PlayfairBold.ttf", "case": "up", "track": .10, "fx": "gold", "decor": "rules",
  "sub": ("script", "Sacramento.ttf"), "vig": 1},
 
 {"p": _lg_pal("140509", "2C0A17", "F9C8D2", "E4879C", "FFE3EA"), "bgk": "rad", "tex": ["spot"],
  "font": "CinzelBold.ttf", "case": "up", "track": .15, "fx": "gradfill",
  "grad": ["FFF0F3", "F2AFC0", "B96076"], "decor": "frame", "sub": ("script", "Parisienne.ttf"), "vig": 1},
 
 {"p": _lg_pal("050A03", "0A1405", "EBFFC9", "A3FF12", "36D900"), "bgk": "rad", "tex": ["dots", "spot"],
  "font": "Righteous.ttf", "case": "up", "track": .05, "fx": "gradneon",
  "grad": ["F2FFD6", "B6FF29", "3ADB00"], "decor": None, "sub": ("track", "PoppinsBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("FFC93C", "FFB300", "E8362C", "FFFFFF", "1A1A1A"), "bgk": "rad", "font": "ArchivoBlack.ttf",
  "case": "up", "track": .02, "fx": "sticker", "decor": None, "sub": ("track", "PoppinsBold.ttf")},
 
 {"p": _lg_pal("17181B", "212327", "8D939C", "C9CFD8"), "bgk": "lin:120", "font": "PoppinsBold.ttf", "case": "up",
  "track": .05, "fx": "emboss", "decor": None, "sub": ("track", "PoppinsLight.ttf"), "grain": 1, "vig": 1},
 
 {"p": _lg_pal("1B0330", "4A0A4E", "FFFFFF", "FF3D81", "FFC93C"), "bgk": "lin:90", "tex": ["sun", "horizon"],
  "sunpos": (.5, .29), "sunr": .20, "cy": .555, "font": "Righteous.ttf", "case": "up", "track": .04,
  "fx": "bevel3d", "grad": ["FFF3B0", "FFB13C", "FF3D81"], "decor": None,
  "sub": ("track", "PoppinsBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("F4F1EA", "FBF9F4", "121212", "6B6257"), "bgk": "lin:100", "tex": ["grain"], "font": "PlayfairBold.ttf",
  "case": "up", "track": .04, "fx": "soft", "decor": "rules", "sub": ("mono", "SpaceMonoBold.ttf")},
 
 {"p": _lg_pal("0B0413", "18072A", "FFE9FA", "FF5FD0", "A855F7"), "bgk": "rad", "tex": ["spot"],
  "font": "Pacifico.ttf", "case": "as", "track": 0, "fx": "neon", "decor": None,
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("0B0B0C", "141416", "FFFFFF", "FF1E2D", "D0D3D8"), "bgk": "lin:120", "tex": ["stripes"],
  "font": "Staatliches.ttf", "case": "up", "track": .04, "fx": "bevel3d",
  "grad": ["FFFFFF", "E2E6EC", "9AA1AC"], "decor": "bar", "sub": ("track", "PoppinsBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("000000", "0A0906", "E9C97A", "B08A25", "FFF1C2"), "bgk": "rad", "tex": ["spot"],
  "font": "CinzelBold.ttf", "case": "up", "track": .20, "fx": "gold", "decor": "rules",
  "sub": ("track", "CinzelBold.ttf"), "vig": 1, "grain": 1},
 
 {"p": _lg_pal("021428", "064E7A", "FFFFFF", "38BDF8", "A5F3FC"), "bgk": "lin:110", "tex": ["spot", "beams"],
  "font": "Lobster.ttf", "case": "as", "track": 0, "fx": "softneon", "decor": None,
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("140610", "2A0C20", "FFE3EF", "FF9EC4", "FFD1E3"), "bgk": "rad", "tex": ["spot", "sparkle"],
  "font": "Sacramento.ttf", "case": "as", "track": 0, "fx": "softneon", "decor": "circle",
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("000000", "020A04", "CFFFE0", "21F37A", "0BAF52"), "bgk": "rad", "tex": ["rain", "scan"],
  "font": "SpaceMonoBold.ttf", "case": "up", "track": .08, "fx": "neon", "decor": None,
  "sub": ("mono", "SpaceMonoBold.ttf"), "vig": 1},
 
 {"p": _lg_pal("070504", "120B07", "F0B98A", "B4662F", "FFDCC2"), "bgk": "rad", "tex": ["grain", "spot"],
  "font": "OswaldBold.ttf", "case": "up", "track": .12, "fx": "gold",
  "grad": ["FFE6D2", "E29A63", "8A4A20", "FFD0AC", "B4662F"], "decor": "frame",
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("0A0A0B", "131316", "FFFFFF", "6B7280"), "bgk": "lin:100", "font": "PoppinsLight.ttf", "case": "up",
  "track": .32, "fx": "soft", "decor": "rules", "sub": None, "vig": 1},
 
 {"p": _lg_pal("F5E400", "FFF34D", "0A0A0A", "0A0A0A"), "bgk": "rad", "font": "Anton.ttf", "case": "up",
  "track": .03, "fx": "flat", "bev": 1, "decor": "frame", "sub": ("track", "PoppinsBold.ttf")},
 
 {"p": _lg_pal("0A0518", "17093A", "F3E8FF", "A855F7", "22D3EE"), "bgk": "rad", "tex": ["grid", "aurora"],
  "font": "Audiowide.ttf", "case": "up", "track": .07, "fx": "gradneon",
  "grad": ["FFFFFF", "D8B4FE", "8B5CF6", "22D3EE"], "decor": "circle",
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("070102", "120409", "FFFFFF", "FF0033", "8B0018"), "bgk": "rad", "tex": ["scan"],
  "font": "Anton.ttf", "case": "up", "track": .04, "fx": "glitch", "decor": None,
  "sub": ("mono", "SpaceMonoBold.ttf"), "vig": 1, "grain": 1},
 
 {"p": _lg_pal("A8A2F2", "F4C9E8", "FFFFFF", "5B4BDB", "FF7EC8"), "bgk": "lin:130", "tex": ["blobs"],
  "font": "PoppinsBold.ttf", "case": "up", "track": .05, "fx": "glass", "decor": None,
  "sub": ("script", "GreatVibes.ttf")},
 
 {"p": _lg_pal("E9E9EA", "FFFFFF", "0A0A0A", "0A0A0A"), "bgk": "rad", "font": "Anton.ttf", "case": "up",
  "track": .05, "fx": "outline", "decor": "card", "sub": ("track", "PoppinsBold.ttf")},
 
 {"p": _lg_pal("01020A", "05071A", "FFFFFF", "6D8BFF", "C084FC"), "bgk": "rad", "tex": ["stars", "aurora"],
  "font": "Michroma.ttf", "case": "up", "track": .10, "fx": "holo",
  "grad": ["FFFFFF", "E9EEFF", "B79BFF", "6FD0FF"], "decor": None,
  "sub": ("track", "PoppinsLight.ttf"), "vig": 1},
 
 {"p": _lg_pal("FF4E50", "FFB03A", "FFFFFF", "5A1204"), "bgk": "lin:150", "tex": ["beams"], "font": "Parisienne.ttf",
  "case": "as", "track": 0, "fx": "soft", "decor": "rules", "sub": ("track", "PoppinsBold.ttf")},
 
 {"p": _lg_pal("08080A", "08080A", "FFFFFF", "FFFFFF"), "bgk": "rad", "font": "Anton.ttf", "case": "up",
  "track": .18, "fx": "monogram", "decor": None, "sub": None, "vig": 1},
]

def _lg_grad3(sz, c1, c2, c3, angle=90):
    n = 512
    g = Image.new("RGB", (1, n))
    px = g.load()
    for y in range(n):
        t = y / (n - 1.0)
        px[0, y] = _lg_mix(c1, c2, t * 2) if t < .5 else _lg_mix(c2, c3, (t - .5) * 2)
    side = int(max(sz) * 1.6)
    g = g.resize((side, side), Image.BICUBIC).rotate(angle - 90, resample=Image.BICUBIC)
    x0 = (g.width - sz[0]) // 2
    y0 = (g.height - sz[1]) // 2
    return g.crop((x0, y0, x0 + sz[0], y0 + sz[1]))

def _lg_metal(sz, base, angle=90):
    n = 512
    stops = [(0.00, (255, 255, 255)), (0.18, _lg_mix(base, (255, 255, 255), .75)), (0.38, _lg_mix(base, (0, 0, 0), .45)),
             (0.50, (250, 252, 255)), (0.62, _lg_mix(base, (0, 0, 0), .55)), (0.82, _lg_mix(base, (255, 255, 255), .55)),
             (1.00, (235, 240, 248))]
    g = Image.new("RGB", (1, n))
    px = g.load()
    for y in range(n):
        t = y / (n - 1.0)
        for i in range(len(stops) - 1):
            a, ca = stops[i]
            b, cb = stops[i + 1]
            if a <= t <= b:
                px[0, y] = _lg_mix(ca, cb, (t - a) / max(1e-6, b - a))
                break
    side = int(max(sz) * 1.6)
    g = g.resize((side, side), Image.BICUBIC).rotate(angle - 90, resample=Image.BICUBIC)
    x0 = (g.width - sz[0]) // 2
    y0 = (g.height - sz[1]) // 2
    return g.crop((x0, y0, x0 + sz[0], y0 + sz[1]))

def _lg_case(t, mode):
    if mode == "up":
        return t.upper()
    if mode == "low":
        return t.lower()
    if mode == "ttl":
        return t.title()
    return t

def _lg_render(text, n, size=1080):
    st = LOGO_STYLES[(int(n) - 1) % len(LOGO_STYLES)]
    P = st["p"]
    W = H = int(size)
    fg, ac, bg, bg2 = P["fg"], P["ac"], P["bg"], P["bg2"]
    body = _lg_case((text or "").strip(), st.get("case", "up"))[:22] or "LOGO"
    has_sub = bool(st.get("sub"))

    bgk = st.get("bgk", "solid")
    if bgk.startswith("lin"):
        img = _lg_bg_lin((W, H), bg, bg2, int(bgk.split(":")[1]))
    elif bgk == "rad":
        img = _lg_bg_rad((W, H), bg2, bg)
    else:
        img = _lg_bg_solid((W, H), bg)

    for t in st.get("tex", []) or []:
        if t == "grid":
            _lg_grid(img, ac + (26,), step=int(W / 20), width=1)
        elif t == "dots":
            _lg_dots(img, ac + (40,), step=int(W / 22), r=max(1, W // 520))
        elif t == "stripes":
            _lg_stripes(img, ac + (38,), step=int(W / 16), width=int(W / 70))
        elif t == "scan":
            _lg_scan(img, (0, 0, 0, 90), step=max(3, W // 220))
        elif t == "blobs":
            img = _lg_blobs(img, [ac, P["ac2"], _lg_mix(ac, fg, .5)], blur=int(W / 6), seed=int(n))
        elif t == "aurora":
            img = _lg_aurora(img, [ac, P["ac2"], _lg_mix(ac, fg, .55), _lg_mix(P["ac2"], (255, 255, 255), .25)],
                             seed=int(n), alpha=.26)
        elif t == "spot":
            img = _lg_spot(img, _lg_mix(ac, (0, 0, 0), .88), pos=(.5, .44), rad=.46)
        elif t == "stars":
            _lg_stars(img, n=int(W / 7), seed=int(n) + 5)
        elif t == "beams":
            img = _lg_beams(img, _lg_mix(ac, (0, 0, 0), .35), seed=int(n))
        elif t == "rain":
            img = _lg_rain(img, ac, seed=int(n))
        elif t == "sparkle":
            img = _lg_sparkle(img, _lg_mix(ac, (255, 255, 255), .55), n=7, seed=int(n) + 2)
        elif t == "horizon":
            _lg_horizon(img, ac + (130,), y_ratio=.68, width=max(2, W // 430))
        elif t == "sun":
            _lg_sun(img, [P["ac2"], ac], pos=st.get("sunpos", (.5, .40)), r=st.get("sunr", .30))
        elif t == "grain":
            img = _lg_grain(img, 16)

    cy = int(H * st.get("cy", 0.435 if has_sub else 0.50))
    box_w = int(W * 0.80)
    box_h = int(H * (0.26 if has_sub else 0.30))
    fx = st.get("fx", "flat")
    if fx == "monogram":
        box_w, box_h = int(W * .62), int(H * .14)
        cy = int(H * .52)

    mask, fs, tr = _lg_fit_mask((W, H), body, st["font"], (box_w, box_h), (W // 2, cy), st.get("track", 0))
    bb = mask.getbbox() or (W // 3, cy - 60, W * 2 // 3, cy + 60)

    dec = st.get("decor")
    if dec == "card":
        _lg_d_card(img, _lg_mix(bg, (255, 255, 255), .10) + (255,))
    elif dec == "tape":
        _lg_d_tape(img, bb, ac + (255,), pad=int(H * .035))
    elif dec == "box":
        _lg_d_box(img, bb, ac, pad=(int(W * .05), int(H * .035)), w=max(4, W // 150))
    elif dec == "frame":
        _lg_d_frame(img, ac, inset=.075, w=max(3, W // 260))
    elif dec == "rules":
        _lg_d_rules(img, bb, ac, w=max(2, W // 320), gap=int(H * .055))
    elif dec == "bar":
        _lg_d_bar(img, bb, ac, w=int(H * .018), gap=int(H * .045))
    elif dec == "brackets":
        _lg_d_brackets(img, ac, w=max(4, W // 180))
    elif dec == "circle":
        _lg_d_circle(img, ac + (120,) if len(ac) == 3 else ac, r=.40, w=max(2, W // 400))
    elif dec == "crosses":
        _lg_d_crosses(img, ac, s=int(W * .018), w=max(3, W // 280))

    stops = st.get("grad")
    stops = [_lg_hex(x) for x in stops] if stops else None
    gang = st.get("gang", 105)

    if fx == "flat":
        _lg_paint(img, mask, fg)
        if st.get("bev"):
            _lg_bevel(img, mask, max(2, W // 190), _lg_mix(fg, (255, 255, 255), .8),
                      _lg_mix(fg, (0, 0, 0), .7), .55)
    elif fx == "outline":
        ring = _lg_ring(mask, max(6, W // 130))
        if stops:
            _lg_paint_multi(img, ring, stops, gang)
        else:
            _lg_paint(img, ring, fg)
    elif fx == "neon":
        img = _lg_glow(img, mask, ac, radius=int(W / 15), passes=3, boost=1.05)
        img = _lg_glow(img, mask, ac, radius=int(W / 58), passes=2, boost=1.25)
        _lg_paint(img, mask, fg)
        _lg_paint(img, _lg_alpha(_lg_ring(mask, max(2, W // 420)), .6), _lg_mix(ac, (255, 255, 255), .45))
    elif fx == "gradneon":
        g = stops or [fg, ac]
        k = max(3, W // 150)
        img = _lg_glow(img, ImageChops.offset(mask, -k, -k), g[0], radius=int(W / 17), passes=3, boost=.95)
        img = _lg_glow(img, ImageChops.offset(mask, k, k), g[-1], radius=int(W / 17), passes=3, boost=.95)
        img = _lg_glow(img, mask, _lg_mix(g[0], g[-1], .5), radius=int(W / 52), passes=2, boost=1.2)
        _lg_paint_multi(img, mask, g, gang)
        _lg_sheen(img, mask, alpha=.26)
        _lg_paint(img, _lg_alpha(_lg_ring(mask, max(2, W // 430)), .55), (255, 255, 255))
    elif fx == "holo":
        g = stops or [fg, P["ac2"], ac]
        img = _lg_glow(img, mask, _lg_mix(g[0], g[-1], .5), radius=int(W / 22), passes=3, boost=.60)
        _lg_paint_multi(img, mask, g, gang)
        _lg_bevel(img, mask, max(2, W // 220), (255, 255, 255), _lg_mix(ac, (0, 0, 0), .55), .45)
        _lg_sheen(img, mask, alpha=.38, pos=.36)
    elif fx == "chrome":
        img = _lg_shadow(img, mask, (0, 0, 0), off=(int(W / 120), int(W / 90)), blur=int(W / 50), alpha=150)
        g = stops or [(255, 255, 255), (228, 240, 252), (120, 140, 162), (16, 20, 26), (10, 12, 16),
                      (176, 194, 212), (255, 255, 255), (96, 110, 126)]
        _lg_paint_multi(img, mask, g, 90)
        _lg_bevel(img, mask, max(2, W // 300), (255, 255, 255), (6, 8, 12), .9)
        _lg_paint(img, _lg_alpha(_lg_ring(mask, max(2, W // 420)), .9), (250, 253, 255))
        _lg_sheen(img, mask, alpha=.55, pos=.30, width=.07)
        img = _lg_glow(img, mask, _lg_mix(ac, (255, 255, 255), .4), radius=int(W / 34), passes=2, boost=.32)
    elif fx == "gold":
        img = _lg_extrude(img, mask, _lg_mix(ac, (0, 0, 0), .74), dx=1, dy=1, depth=max(6, W // 95), fade=.45)
        g = stops or [(255, 247, 216), (233, 200, 124), (137, 103, 40), (247, 227, 163), (200, 161, 57)]
        _lg_paint_multi(img, mask, g, 92)
        _lg_bevel(img, mask, max(2, W // 240), (255, 251, 230), (84, 58, 12), .7)
        _lg_sheen(img, mask, alpha=.40, pos=.34)
        img = _lg_glow(img, mask, (188, 148, 58), radius=int(W / 36), passes=2, boost=.40)
    elif fx == "bevel3d":
        g = stops or [fg, ac]
        img = _lg_extrude(img, mask, _lg_mix(ac, (0, 0, 0), .58), dx=1, dy=1, depth=max(10, W // 52), fade=.5)
        _lg_paint_multi(img, mask, g, gang)
        _lg_bevel(img, mask, max(2, W // 210), (255, 255, 255), _lg_mix(ac, (0, 0, 0), .6), .6)
        _lg_sheen(img, mask, alpha=.3)
    elif fx == "rim":
        k = max(3, W // 100)
        img = _lg_glow(img, ImageChops.offset(mask, -k, -k), ac, radius=int(W / 13), passes=3, boost=1.05)
        img = _lg_glow(img, ImageChops.offset(mask, k, k), P["ac2"], radius=int(W / 13), passes=3, boost=1.05)
        _lg_paint(img, mask, fg)
        e = max(2, W // 250)
        hi = ImageChops.multiply(ImageChops.subtract(mask, ImageChops.offset(mask, e, e)), mask)
        lo = ImageChops.multiply(ImageChops.subtract(mask, ImageChops.offset(mask, -e, -e)), mask)
        _lg_paint(img, hi, ac)
        _lg_paint(img, lo, P["ac2"])
    elif fx == "glass":
        pad = (int(W * .085), int(H * .085))
        _lg_glass(img, (bb[0] - pad[0], bb[1] - pad[1], bb[2] + pad[0], bb[3] + pad[1]), int(H * .05),
                  tint=(255, 255, 255), a=46, bw=max(2, W // 430))
        if stops:
            _lg_paint_multi(img, mask, stops, gang)
        else:
            _lg_paint(img, mask, fg)
        _lg_bevel(img, mask, max(2, W // 250), (255, 255, 255), _lg_mix(ac, (0, 0, 0), .4), .35)
    elif fx == "duotone":
        k = max(5, W // 115)
        _lg_paint(img, ImageChops.offset(mask, -k, k), P["ac2"])
        _lg_paint(img, ImageChops.offset(mask, k, -k), ac)
        _lg_paint(img, mask, fg)
    elif fx == "gradfill":
        _lg_paint_multi(img, mask, stops or [fg, ac], gang)
        _lg_bevel(img, mask, max(2, W // 240), (255, 255, 255), _lg_mix(ac, (0, 0, 0), .5), .35)
    elif fx == "firegrad":
        img = _lg_glow(img, mask, (255, 84, 0), radius=int(W / 15), passes=3, boost=1.1)
        _lg_paint_multi(img, mask, [(255, 246, 190), (255, 196, 60), (255, 112, 0), (206, 32, 0)], 90)
        _lg_bevel(img, mask, max(2, W // 250), (255, 250, 210), (120, 24, 0), .6)
        _lg_sheen(img, mask, alpha=.28, pos=.30)
    elif fx == "icegrad":
        img = _lg_glow(img, mask, ac, radius=int(W / 15), passes=3, boost=1.1)
        _lg_paint_multi(img, mask, [(255, 255, 255), (206, 244, 255), (118, 206, 246), (36, 140, 208)], 90)
        _lg_bevel(img, mask, max(2, W // 250), (255, 255, 255), (16, 70, 110), .6)
        _lg_sheen(img, mask, alpha=.45, pos=.34)
    elif fx == "glitch":
        img = _lg_rgbsplit(img, mask, dx=max(5, W // 120))
        _lg_paint(img, mask, fg)
        d = ImageDraw.Draw(img)
        rnd = random.Random(int(n) * 7)
        for _ in range(4):
            y = rnd.randint(bb[1], max(bb[1] + 1, bb[3]))
            hgt = rnd.randint(4, max(6, H // 90))
            sl = img.crop((0, y, W, min(H, y + hgt)))
            img.paste(sl, (rnd.randint(-30, 30), y))
        img = _lg_glow(img, mask, ac, radius=int(W / 34), passes=2, boost=.42)
    elif fx in ("extrude", "_lg_extrude"):
        img = _lg_extrude(img, mask, ac, dx=1, dy=1, depth=max(10, W // 44), fade=.55)
        _lg_paint(img, mask, fg)
    elif fx == "longshadow":
        img = _lg_extrude(img, mask, ac, dx=1, dy=1, depth=max(18, W // 14), fade=.25)
        _lg_paint(img, mask, fg)
        _lg_bevel(img, mask, max(2, W // 240), (255, 255, 255), _lg_mix(ac, (0, 0, 0), .3), .3)
    elif fx == "softneon":
        img = _lg_glow(img, mask, ac, radius=int(W / 26), passes=3, boost=.95)
        _lg_paint(img, mask, fg)
    elif fx == "soft":
        img = _lg_shadow(img, mask, (0, 0, 0), off=(int(W / 90), int(W / 72)), blur=int(W / 48), alpha=120)
        _lg_paint(img, mask, fg)
    elif fx == "emboss":
        k = max(3, W // 180)
        _lg_paint(img, ImageChops.offset(mask, -k, -k), _lg_mix(fg, (255, 255, 255), .75))
        _lg_paint(img, ImageChops.offset(mask, k, k), _lg_mix(fg, (0, 0, 0), .80))
        _lg_paint(img, mask, fg)
        _lg_bevel(img, mask, max(2, W // 260), (255, 255, 255), (0, 0, 0), .35)
    elif fx == "badge":
        pad = (int(W * .058), int(H * .042))
        box = (bb[0] - pad[0], bb[1] - pad[1], bb[2] + pad[0], bb[3] + pad[1])
        bm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(bm).rounded_rectangle(box, radius=int(H * .032), fill=255)
        img = _lg_shadow(img, bm, (0, 0, 0), off=(0, int(H * .014)), blur=int(W / 36), alpha=130)
        if stops:
            _lg_paint_multi(img, bm, stops, 90)
        else:
            _lg_paint(img, bm, ac)
        _lg_paint(img, _lg_alpha(_lg_ring(bm, max(2, W // 380)), .5), _lg_mix(ac, (255, 255, 255), .6))
        _lg_paint(img, mask, fg)
    elif fx == "split":
        _lg_paint(img, mask, fg)
        low = mask.copy()
        ImageDraw.Draw(low).rectangle((0, 0, W, (bb[1] + bb[3]) // 2), fill=0)
        _lg_paint(img, low, ac)
    elif fx == "sticker":
        img = _lg_shadow(img, mask, (0, 0, 0), off=(int(W / 70), int(W / 62)), blur=int(W / 90), alpha=110)
        _lg_paint(img, _lg_ring(mask, max(14, W // 52)), P["ac2"])
        _lg_paint(img, _lg_ring(mask, max(8, W // 80)), ac)
        _lg_paint(img, mask, fg)
        _lg_bevel(img, mask, max(2, W // 220), _lg_mix(fg, (255, 255, 255), .6), _lg_mix(fg, (0, 0, 0), .5), .45)
    elif fx == "monogram":
        ini = body[0]
        mono, _, _ = _lg_fit_mask((W, H), ini, st["font"], (int(W * .54), int(H * .62)), (W // 2, int(H * .48)))
        knock = mask.filter(ImageFilter.GaussianBlur(max(2, W / 55))).point(lambda v: min(255, int(v * 3.4)))
        ghost = ImageChops.subtract(mono, knock)
        _lg_paint(img, ghost.point(lambda v: int(v * .15)), fg)
        _lg_paint(img, ImageChops.subtract(_lg_ring(mono, max(3, W // 300)), knock), _lg_mix(fg, bg, .62))
        _lg_paint(img, mask, fg)
    else:
        _lg_paint(img, mask, fg)

    sub = st.get("sub")
    if sub:
        kind, sfont = sub
        gap = int(H * (.075 if dec in ("box", "frame", "card") else .055))
        scy = min(int(H * .86), bb[3] + gap + int(H * .045))
        if kind == "script":
            sm, _, _ = _lg_fit_mask((W, H), (text or "").strip()[:18].title(), sfont, (int(W * .56), int(H * .13)), (W // 2, scy))
            _lg_paint(img, sm, ac)
        elif kind == "mono":
            sm, _, _ = _lg_fit_mask((W, H), (text or "").strip().upper()[:18], sfont, (int(W * .40), int(H * .032)), (W // 2, scy), .28)
            _lg_paint(img, sm, ac)
        else:
            sm, _, _ = _lg_fit_mask((W, H), (text or "").strip().upper()[:18], sfont, (int(W * .46), int(H * .030)), (W // 2, scy), .42)
            _lg_paint(img, sm, ac)

    if st.get("grain"):
        img = _lg_grain(img, 14)
    if st.get("vig"):
        img = _lg_vig(img, .55)
    return img

async def logo_controller (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None
    if not cmd :
        return
    m =re .match (r"^(?:لوگو|logo)\s+(.+)$",cmd .strip (),re .I |re .S )
    if not m :
        return
    raw =" ".join (m .group (1 ).split ())
    parts =raw .split (" ")
    num =0
    if len (parts )>1 :
        tail =_pemoji_norm_digit (parts [-1 ])
        head =_pemoji_norm_digit (parts [0 ])
        if tail .isdigit ():
            num =int (tail )
            parts =parts [:-1 ]
        elif head .isdigit ():
            num =int (head )
            parts =parts [1 :]
    elif len (parts )==1 and _pemoji_norm_digit (parts [0 ]).isdigit ():
        parts =[]
    body =" ".join (parts ).strip ()
    if not body :
        return await safe_edit_message (message ,"**متن لوگو رو بنویس.**\nمثال: `لوگو amir 10`")
    if Image is None :
        return await safe_edit_message (message ,"**کتابخانه تصویر روی سرور نصب نیست.**")
    if not num :
        num =random .randint (1 ,len (LOGO_STYLES ))
    num =max (1 ,min (num ,len (LOGO_STYLES )))
    status =await safe_edit_message (message ,"**◈ در حال ساخت لوگو...**")
    target =status or message
    path =os .path .join (tempfile .gettempdir (),f"dsl_{uid }_{int (time .time ()*1000 )}.png")
    try :
        img =await asyncio .to_thread (_lg_render ,body ,num ,1080 )
        await asyncio .to_thread (img .save ,path ,"PNG")
        reply_to =getattr (message ,"reply_to_message_id",None )
        if not reply_to :
            rm =getattr (message ,"reply_to_message",None )
            reply_to =getattr (rm ,"id",None )if rm else None
        await client .send_photo (message .chat .id ,path ,caption =f"**◈ {num }**",reply_to_message_id =reply_to )
        try :
            await target .delete ()
        except Exception :
            pass
    except Exception as exc :
        logger .warning ("logo build failed: %s: %s",type (exc ).__name__ ,str (exc )[:140 ])
        await safe_edit_message (target ,"**ساخت لوگو ناموفق بود.**")
    finally :
        try :
            os .remove (path )
        except Exception :
            pass

PEMOJI_INLINE_PENDING ={}
PEMOJI_STATUS ={}
PREMIUM_BOT =None
PREMIUM_BOT_USERNAME =""

def _pemoji_token_get ():
    return PREMIUM_BOT_TOKEN

def _pemoji_bot_pair ():
    if PREMIUM_BOT is not None and PREMIUM_BOT_USERNAME :
        return PREMIUM_BOT ,PREMIUM_BOT_USERNAME
    return manager_bot ,(BOT_USERNAME or "")

async def _pemoji_inline_results (client ,text ):
    bot_c ,bot_un =_pemoji_bot_pair ()
    if not bot_un and bot_c is manager_bot :
        if manager_bot .me :
            bot_un =manager_bot .me .username or ""
    try :
        return await asyncio .wait_for (client .get_inline_bot_results (bot_un ,text ),timeout =8.0 )
    except Exception :
        if bot_c is manager_bot :
            raise
        mun =manager_bot .me .username if manager_bot .me else ""
        return await asyncio .wait_for (client .get_inline_bot_results (mun ,text ),timeout =8.0 )

async def pemoji_premium_bot_start (token ):
    global PREMIUM_BOT ,PREMIUM_BOT_USERNAME
    if PREMIUM_BOT is not None :
        try :
            await PREMIUM_BOT .stop ()
        except Exception :
            pass
        PREMIUM_BOT =None
        PREMIUM_BOT_USERNAME =""
    if not token :
        return None
    c =Client ("pemoji_premium",api_id =API_ID ,api_hash =API_HASH ,bot_token =token ,in_memory =True ,workers =1 ,**_darkself_optional_client_kwargs ())
    c .add_handler (InlineQueryHandler (pemoji_premium_inline ),group =0 )
    c .add_handler (CallbackQueryHandler (pemoji_pick_callback ),group =0 )
    c .add_handler (RawUpdateHandler (pemoji_inline_send_watcher ),group =37 )
    await c .start ()
    PREMIUM_BOT =c
    PREMIUM_BOT_USERNAME =c .me .username or ""
    return c

async def _pemoji_premium_autostart ():
    tok =_pemoji_token_get ()
    if not tok :
        return
    for _attempt in range (8 ):
        try :
            await pemoji_premium_bot_start (tok )
            logger .info ("Premium emoji bot connected: @%s",PREMIUM_BOT_USERNAME )
            return
        except FloodWait as fw :
            logger .warning ("Premium emoji bot start flood-wait %ss; retrying",getattr (fw ,"value",60 ))
            await asyncio .sleep (min (getattr (fw ,"value",60 )+10 ,1800 ))
        except Exception as e :
            logger .warning ("Premium emoji bot start failed: %s: %s",type (e ).__name__ ,str (e )[:120 ])
            await asyncio .sleep (20 )
PEMOJI_FALLBACK ="⭐"
PEMOJI_CMD_RE =re .compile (r"^[\W_]{0,3}\s*(?:تنظیم|حذف|لیست)\s+(?:لیست\s+)?ایموجی")

def _utf16_len (text ):
    return len (text .encode ("utf-16-le"))//2

def _pemoji_map (uid ):
    m =data_manager .get_user_data (uid ).get ("pemoji_map")or {}
    return m if isinstance (m ,dict )else {}

def _pemoji_canon (s ):
    return (s or "").replace ("\ufe0f","").replace ("\ufe0e","")

def _pemoji_variants (uid ):
    out ={}
    for k ,doc in _pemoji_map (uid ).items ():
        try :
            doc_i =int (doc )
        except Exception :
            continue
        if not doc_i or not k :
            continue
        base =_pemoji_canon (k )
        for v in (k ,base ,base +"\ufe0f"):
            if v :
                out [v ]=doc_i
    return out

def _pemoji_query_match (uid ,q_text ):
    if re .search (r"\[\d{5,25}\]",q_text ):
        return True
    return any (v in q_text for v in _pemoji_variants (uid ))

def _pemoji_extract_custom (msg ):
    out =[]
    if not msg :
        return out
    txt =getattr (msg ,"text",None )or getattr (msg ,"caption",None )or ""
    ents =getattr (msg ,"entities",None )or getattr (msg ,"caption_entities",None )or []
    buf =txt .encode ("utf-16-le")
    for ent in ents :
        doc =getattr (ent ,"custom_emoji_id",None )
        if not doc :
            continue
        try :
            off =int (getattr (ent ,"offset",0 ))
            ln =int (getattr (ent ,"length",0 ))
            ch =buf [off *2 :(off +ln )*2 ].decode ("utf-16-le")
        except Exception :
            ch =""
        out .append ((ch or PEMOJI_FALLBACK ,int (doc )))
    return out

async def _pemoji_doc_is_custom (client ,doc ):
    try :
        res =await client .invoke (functions .messages .GetCustomEmojiDocuments (document_id =[int (doc )]))
        return any (isinstance (d ,types .Document )for d in (res or []))
    except Exception :
        return True

PEMOJI_PICK_COLS =5
PEMOJI_PICK_PAGE =50
PEMOJI_PACK_CACHE ={}
PEMOJI_PICK_SESS ={}

def _pemoji_pack_name (s ):
    m =re .search (r"(?:addemoji|addstickers)/([A-Za-z0-9_]{1,64})",s or "")
    return m .group (1 )if m else ""

async def _pemoji_pack_items (client ,name ,uid =0 ):
    if not name :
        return []
    hit =PEMOJI_PACK_CACHE .get (name )
    if hit and time .time ()-hit [0 ]<1800 :
        return hit [1 ]
    pool =[]
    if client is not None :
        pool .append (client )
    try :
        uc =ACTIVE_BOTS .get (int (uid or 0 ),(None ,None ))[0 ]
        if uc is not None and uc not in pool :
            pool .append (uc )
    except Exception :
        pass
    docs =None
    for cl in pool :
        try :
            res =await cl .invoke (functions .messages .GetStickerSet (stickerset =types .InputStickerSetShortName (short_name =name ),hash =0 ))
            docs =getattr (res ,"documents",None )or []
            break
        except Exception as exc :
            logger .debug ("pemoji pack fetch failed: %s",type (exc ).__name__ )
    if docs is None :
        return []
    items =[]
    for doc in docs :
        alt =""
        ce =False
        for at in getattr (doc ,"attributes",None )or []:
            if isinstance (at ,types .DocumentAttributeCustomEmoji ):
                ce =True
                alt =getattr (at ,"alt","")or alt
            elif isinstance (at ,types .DocumentAttributeSticker ):
                alt =alt or (getattr (at ,"alt","")or "")
        did =int (getattr (doc ,"id",0 )or 0 )
        if ce and did :
            items .append ((did ,alt or PEMOJI_FALLBACK ))
    PEMOJI_PACK_CACHE [name ]=(time .time (),items )
    return items

def _pemoji_pick_save (sess ):
    try :
        PEMOJI_PICK_SESS [sess ["token"]]=sess
        data_manager .update_user_data (int (sess ["uid"]),{"pemoji_pick":sess })
    except Exception :
        pass

def _pemoji_pick_get (token ,uid =0 ):
    if not token :
        return None
    s =PEMOJI_PICK_SESS .get (token )
    if isinstance (s ,dict ):
        return s
    try :
        s =data_manager .get_user_data (int (uid or 0 )).get ("pemoji_pick")
    except Exception :
        s =None
    if isinstance (s ,dict )and s .get ("token")==token :
        PEMOJI_PICK_SESS [token ]=s
        return s
    return None

def _pemoji_pick_page (items ,page ,base ):
    total =len (items )
    pages =max (1 ,(total +PEMOJI_PICK_PAGE -1 )//PEMOJI_PICK_PAGE )
    try :
        page =int (page )
    except Exception :
        page =0
    page =max (0 ,min (page ,pages -1 ))
    chunk =items [page *PEMOJI_PICK_PAGE :page *PEMOJI_PICK_PAGE +PEMOJI_PICK_PAGE ]
    text ="\U0001D5D7\U0001D5D4\U0001D5E5\U0001D5DE\U0001D5E6\U0001D5D8\U0001D5DF\U0001D5D9  \u00b7  PICK"
    if base :
        text +="  \u00b7  "+base
    text +="\n"+_pemoji_fa_num (page +1 )+"/"+_pemoji_fa_num (pages )+"  \u00b7  "+_pemoji_fa_num (total )+"\n\u2500"*1 +"\u2500"*13
    for i ,(doc ,alt )in enumerate (chunk ):
        text +="\n"if i %PEMOJI_PICK_COLS ==0 else "   "
        text +=_pemoji_fa_num (page *PEMOJI_PICK_PAGE +i +1 )+" "
        yield_off =_utf16_len (text )
        text +=PEMOJI_FALLBACK
        chunk [i ]=(doc ,alt ,yield_off )
    entities =[types .MessageEntityCustomEmoji (offset =c [2 ],length =1 ,document_id =c [0 ])for c in chunk ]
    return text ,entities ,page ,pages

def _pemoji_pick_kb_raw (token ,page ,pages ):
    prev_p =(page -1 )%pages
    next_p =(page +1 )%pages
    return types .ReplyInlineMarkup (rows =[types .KeyboardButtonRow (buttons =[
    types .KeyboardButtonCallback (text ="\u276e",data =("pemopg:%s:%d"%(token ,prev_p )).encode ()),
    types .KeyboardButtonCallback (text ="\u276f",data =("pemopg:%s:%d"%(token ,next_p )).encode ()),
    ])])

def _pemoji_pick_kb_pyro (token ,page ,pages ):
    prev_p =(page -1 )%pages
    next_p =(page +1 )%pages
    return InlineKeyboardMarkup ([[
    InlineKeyboardButton ("\u276e",callback_data ="pemopg:%s:%d"%(token ,prev_p )),
    InlineKeyboardButton ("\u276f",callback_data ="pemopg:%s:%d"%(token ,next_p )),
    ]])

async def _pemoji_pick_render (client ,q ,uid =0 ):
    parts =(q or "").strip ().split (":")
    token =parts [1 ]if len (parts )>1 else ""
    try :
        page =int (parts [2 ])if len (parts )>2 else 0
    except Exception :
        page =0
    sess =_pemoji_pick_get (token ,uid )
    if not sess :
        return "",[],None
    items =await _pemoji_pack_items (client ,sess .get ("name",""),sess .get ("uid",uid ))
    if not items :
        return "",[],None
    text ,entities ,page ,pages =_pemoji_pick_page (items ,page ,sess .get ("base",""))
    if sess .get ("page")!=page :
        sess ["page"]=page
        _pemoji_pick_save (sess )
    return text ,entities ,_pemoji_pick_kb_raw (token ,page ,pages )

async def pemoji_pick_callback (client ,callback ):
    data =getattr (callback ,"data","")or ""
    if not data .startswith ("pemopg:"):
        return
    try :
        parts =data .split (":")
        token =parts [1 ]
        page =int (parts [2 ])
        uid =callback .from_user .id if callback .from_user else 0
        sess =_pemoji_pick_get (token ,uid )
        if not sess or int (sess .get ("uid",0 )or 0 )!=int (uid ):
            return await callback .answer ()
        text ,entities ,kb =await _pemoji_pick_render (client ,"pemopick:%s:%d"%(token ,page ),uid )
        if not entities :
            return await callback .answer ()
        raw_id =getattr (callback ,"inline_message_id",None )
        mid =_decode_inline_msg_id (raw_id )if raw_id else None
        if not mid :
            return await callback .answer ()
        session =await _pem_get_session (client ,mid .dc_id )
        await session .invoke (functions .messages .EditInlineBotMessage (id =mid ,message =text ,entities =entities ,reply_markup =kb ))
        return await callback .answer ()
    except MessageNotModified :
        pass
    except Exception as exc :
        logger .warning ("pemoji pick callback failed: %s",type (exc ).__name__ )
    try :
        return await callback .answer ()
    except Exception :
        return

def _pemoji_parse (uid ,query ):
    vmap =_pemoji_variants (uid )
    keys =sorted (vmap ,key =len ,reverse =True )
    text =""
    entities =[]
    i =0
    n =len (query )
    while i <n :
        m =re .match (r"\[(\d{5,25})\]",query [i :])
        if m :
            entities .append (types .MessageEntityCustomEmoji (offset =_utf16_len (text ),length =1 ,document_id =int (m .group (1))))
            text +=PEMOJI_FALLBACK
            i +=m .end ()
            continue
        hit =None
        for k in keys :
            if query .startswith (k ,i ):
                hit =k
                break
        if hit :
            entities .append (types .MessageEntityCustomEmoji (offset =_utf16_len (text ),length =_utf16_len (hit ),document_id =vmap [hit ]))
            text +=hit
            i +=len (hit )
            continue
        text +=query [i ]
        i +=1
    return text ,entities

def _decode_inline_msg_id (s ):
    try :
        return _pyro_unpack_inline (str (s ))
    except Exception :
        pass
    try :
        s =str (s )
        if s .isdigit ():
            return types .InputBotInlineMessageID (dc_id =2 ,id =int (s ),access_hash =0 )
        pad =s +"="*(-len (s )%4 )
        raw =base64 .urlsafe_b64decode (pad )
        if len (raw )<20 :
            return None
        dc ,mid ,ah =struct .unpack ("<iqq",raw [:20 ])
        return types .InputBotInlineMessageID (dc_id =dc ,id =mid ,access_hash =ah )
    except Exception :
        return None

async def _pemoji_clear_kb (packed ):
    try :
        tok =_pemoji_token_get ()
        if not tok :
            return
        await asyncio .sleep (1.5 )
        session =await get_http_session ()
        t =aiohttp .ClientTimeout (total =5.0 )
        async with session .post (f"https://api.telegram.org/bot{tok }/editMessageReplyMarkup",json ={"inline_message_id":packed ,"reply_markup":{"inline_keyboard":[]}},timeout =t )as resp :
            await resp .read ()
    except Exception :
        pass

@manager_bot .on_raw_update (group =37 )
async def pemoji_inline_send_watcher (client ,update ,users ,chats ):
    try :
        logger .debug ("prem raw upd: %s",type (update ).__name__ )
        if not isinstance (update ,types .UpdateBotInlineSend ):
            return
        uid =update .user_id
        q =PEMOJI_INLINE_PENDING .pop (update .id ,None )or getattr (update ,"query","")or ""
        logger .debug ("pemoji inline send: uid=%s q=%r",update .user_id ,q [:48 ])
        kb =None
        qs =q .strip ()
        if qs .startswith ("pemopick:"):
            text ,entities ,kb =await _pemoji_pick_render (client ,qs ,uid )
        elif qs =="pemolist":
            text ,entities =_pemoji_build_list (uid )
        else :
            text ,entities =_pemoji_parse (uid ,q )
        if not entities or not getattr (update ,"msg_id",None ):
            return
        mid =update .msg_id
        if not isinstance (mid ,(types .InputBotInlineMessageID ,types .InputBotInlineMessageID64 )):
            mid =_decode_inline_msg_id (mid )
        if not mid :
            return
        session =await _pem_get_session (client ,mid .dc_id )
        ok =await session .invoke (functions .messages .EditInlineBotMessage (id =mid ,message =text ,entities =entities ,reply_markup =kb ))
        logger .info ("pemoji inline edit applied: %s ent=%d",type (ok ).__name__ ,len (entities ))
        if kb is None :
            try :
                asyncio .create_task (_pemoji_clear_kb (_pyro_pack_inline (mid )))
            except Exception :
                pass
    except Exception as exc :
        logger .warning ("pemoji inline edit failed: %s",type (exc ).__name__ )

def _pemoji_fa_num (n ):
    return str (n )

def _pemoji_norm_digit (s ):
    fa ="۰۱۲۳۴۵۶۷۸۹"
    ar ="٠١٢٣٤٥٦٧٨٩"
    out =""
    for c in s :
        if c in fa :out +=str (fa .index (c ))
        elif c in ar :out +=str (ar .index (c ))
        else :out +=c
    return out

def _pemoji_build_list (uid ):
    pmap =_pemoji_map (uid )
    text ="𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙  ·  PREMIUM EMOJI\n──────────────"
    entities =[]
    for i ,(ch ,doc )in enumerate (pmap .items (),1 ):
        try :
            doc_i =int (doc )
        except Exception :
            doc_i =0
        if not doc_i :
            continue
        prefix =f"\n{_pemoji_fa_num (i )}) "
        entities .append (types .MessageEntityCustomEmoji (offset =_utf16_len (text )+_utf16_len (prefix ),length =1 ,document_id =doc_i ))
        text +=prefix +PEMOJI_FALLBACK +" ⟵ "+ch
    return text ,entities

async def pemoji_inline_answer (client ,query ,uid ,q_text ):
    if q_text .strip ().startswith ("pemopick:"):
        parts =q_text .strip ().split (":")
        token =parts [1 ]if len (parts )>1 else ""
        try :
            page =int (parts [2 ])if len (parts )>2 else 0
        except Exception :
            page =0
        sess =_pemoji_pick_get (token ,uid )
        if not sess :
            return
        items =await _pemoji_pack_items (client ,sess .get ("name",""),sess .get ("uid",uid ))
        if not items :
            return
        text ,entities ,page ,pages =_pemoji_pick_page (items ,page ,sess .get ("base",""))
        result =InlineQueryResultArticle (
        id =str (uuid .uuid4 ()),
        title ="\u2726 \u0627\u0646\u062a\u062e\u0627\u0628 \u0627\u06cc\u0645\u0648\u062c\u06cc \u067e\u0631\u0645\u06cc\u0648\u0645",
        description =str (sess .get ("name",""))[:64 ],
        input_message_content =InputTextMessageContent (text ),
        reply_markup =_pemoji_pick_kb_pyro (token ,page ,pages ),
        )
        return await query .answer ([result ],cache_time =0 ,is_personal =True )
    if q_text .strip ()=="pemolist":
        res =await bot_api_request ("answerInlineQuery",{
        "inline_query_id":query .id ,
        "cache_time":0 ,
        "is_personal":True ,
        "results":[{
        "type":"article",
        "id":str (uuid .uuid4 ()),
        "title":"✦ لیست ایموجی پرمیوم",
        "description":"نمایش نگاشت‌ها با ایموجی پرمیوم",
        "input_message_content":{"message_text":"⏳" },
        "reply_markup":{"inline_keyboard":[[{"text":"✦","callback_data":"pemnoop"}]]},
        }]
        },timeout =5.0 )
        if res .get ("ok"):
            return
        result =InlineQueryResultArticle (
        id =str (uuid .uuid4 ()),
        title ="✦ لیست ایموجی پرمیوم",
        input_message_content =InputTextMessageContent ("⏳"),
        reply_markup =InlineKeyboardMarkup ([[InlineKeyboardButton ("✦",callback_data ="pemnoop")]]),
        )
        return await query .answer ([result ],cache_time =0 ,is_personal =True )
    text ,entities =_pemoji_parse (uid ,q_text )
    PEMOJI_INLINE_PENDING [query .id ]=q_text
    res =await bot_api_request ("answerInlineQuery",{
    "inline_query_id":query .id ,
    "cache_time":0 ,
    "is_personal":True ,
    "results":[{
    "type":"article",
    "id":str (uuid .uuid4 ()),
    "title":f"✦ ارسال با {len (entities )} ایموجی پرمیوم",
    "description":q_text [:64 ],
    "input_message_content":{"message_text":text },
    "reply_markup":{"inline_keyboard":[[{"text":"✦","callback_data":"pemnoop"}]]},
    }]
    },timeout =5.0 )
    if res .get ("ok"):
        return
    result =InlineQueryResultArticle (
    id =str (uuid .uuid4 ()),
    title =f"✦ ارسال با {len (entities )} ایموجی پرمیوم",
    input_message_content =InputTextMessageContent (text ),
    reply_markup =InlineKeyboardMarkup ([[InlineKeyboardButton ("✦",callback_data ="pemnoop")]]),
    )
    return await query .answer ([result ],cache_time =0 ,is_personal =True )

async def pemoji_premium_inline (client ,query ):
    logger .debug ("premium inline query: %r",getattr (query ,"query","")[:40 ])
    try :
        uid =query .from_user .id
        q_text =query .query .strip ()
        if q_text =="pemolist"or q_text .startswith ("pemopick:")or _pemoji_query_match (uid ,q_text ):
            await pemoji_inline_answer (client ,query ,uid ,q_text )
    except Exception as exc :
        logger .warning ("premium inline answer failed: %s: %s",type (exc ).__name__ ,str (exc )[:160])

async def pemoji_outgoing_watcher (client ,message ):
    try :
        if not (getattr (message ,"out" ,False )or getattr (message ,"outgoing" ,False )):
            return
        if getattr (message ,"via_bot" ,None ):
            return
        if getattr (message ,"edit_date" ,None ):
            return
        if getattr (message ,"media" ,None ):
            return
        if getattr (message ,"forward_date" ,None )or getattr (message ,"forward_from" ,None ):
            return
        uid =client .me .id
        if not PEMOJI_STATUS .get (uid ,False ):
            return
        text =getattr (message ,"text" ,None )or ""
        if not text .strip ()or len (text )>200 :
            return
        chk =text
        try :
            c =get_cmd (uid ,text )
            if c :
                chk =c
        except Exception :
            chk =text
        if COMMAND_SKIP_REGEX .match (text )or EXTRA_FUN_SKIP_REGEX .match (text ):
            return
        if COMMAND_SKIP_REGEX .match (chk )or EXTRA_FUN_SKIP_REGEX .match (chk ):
            return
        if PEMOJI_CMD_RE .match (text )or PEMOJI_CMD_RE .match (chk ):
            return
        if getattr (message ,"entities" ,None ):
            if any (getattr (e ,"custom_emoji_id",None )for e in message .entities ):
                return
        if not _pemoji_query_match (uid ,text ):
            return
        reply_id =None
        try :
            reply_id =getattr (message ,"reply_to_message_id" ,None )
            if not reply_id :
                rm =getattr (message ,"reply_to_message" ,None )
                reply_id =getattr (rm ,"id" ,None )if rm else None
        except Exception :
            reply_id =None
        results =await _pemoji_inline_results (client ,text )
        if not results or not results .results :
            return
        try :
            await message .delete ()
        except Exception :
            return
        await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id ,reply_to_message_id =reply_id )
    except ChatSendInlineForbidden :
        pass
    except Exception as exc :
        logger .debug ("pemoji auto-send skipped: %s",type (exc ).__name__ )

async def pemoji_pick_reply_watcher (client ,message ):
    try :
        if not (getattr (message ,"out",False )or getattr (message ,"outgoing",False )):
            return
        if getattr (message ,"edit_date",None ):
            return
        txt =(getattr (message ,"text",None )or "").strip ()
        if not txt or len (txt )>4 :
            return
        num =_pemoji_norm_digit (txt )
        if not num .isdigit ():
            return
        uid =client .me .id
        sess =None
        try :
            raw =data_manager .get_user_data (uid ).get ("pemoji_pick")
            if isinstance (raw ,dict ):
                sess =PEMOJI_PICK_SESS .get (raw .get ("token"))or raw
        except Exception :
            sess =None
        if not isinstance (sess ,dict ):
            return
        rid =getattr (message ,"reply_to_message_id",None )
        if not rid :
            rm =getattr (message ,"reply_to_message",None )
            rid =getattr (rm ,"id",None )if rm else None
        if not rid :
            return
        if int (sess .get ("msg",0 )or 0 )!=int (rid ):
            rm =getattr (message ,"reply_to_message",None )
            if rm is None :
                try :
                    rm =await client .get_messages (message .chat .id ,rid )
                except Exception :
                    rm =None
            rtxt =(getattr (rm ,"text",None )or "")if rm else ""
            if not (getattr (rm ,"via_bot",None )and "PICK"in rtxt ):
                return
            sess ["msg"]=int (rid )
            _pemoji_pick_save (sess )
        items =await _pemoji_pack_items (client ,sess .get ("name",""),uid )
        idx =int (num )
        if idx <1 or idx >len (items ):
            return await safe_edit_message (message ,"**این شماره داخل پک نیست.**")
        doc ,alt =items [idx -1 ]
        base =(sess .get ("base")or "").strip ()or alt or PEMOJI_FALLBACK
        if not await _pemoji_doc_is_custom (client ,doc ):
            return await safe_edit_message (message ,"**این ایموجی پرمیوم نیست.**")
        pmap =_pemoji_map (uid )
        for k in list (pmap ):
            if _pemoji_canon (k )==_pemoji_canon (base ):
                pmap .pop (k ,None )
        pmap [base ]=str (doc )
        data_manager .update_user_data (uid ,{"pemoji_map":pmap })
        return await safe_edit_message (message ,f"**◈ {base } تنظیم شد.**")
    except Exception as exc :
        logger .debug ("pemoji pick reply skipped: %s",type (exc ).__name__ )

async def pemoji_controller (client ,message ):
    uid =client .me .id
    if not await check_global_fjoin_for_user (uid ,message ):return
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None
    if not cmd :
        return
    cmd =cmd .strip ()

    if re .match (r"^لیست\s+ایموجی(?:\s+پرمیوم)?$",cmd ):
        pmap =_pemoji_map (uid )
        if not pmap :
            return await safe_edit_message (message ,"**لیست ایموجی پرمیوم خالیه.**\n\nبا `تنظیم ایموجی ❤️` و ریپلای روی ایموجی پرمیوم، نگاشت بساز.")
        try :
            results =await _pemoji_inline_results (client ,"pemolist")
            if results and results .results :
                try :
                    await message .delete ()
                except Exception :
                    pass
                return await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id )
        except ChatSendInlineForbidden :
            return await safe_edit_message (message ,"ارسال پیام شیشه‌ای در این چت بسته است.")
        except Exception as e :
            logger .warning ("pemoji list inline failed: %s",type (e ).__name__ )
        return await safe_edit_message (message ,"لیست ساخته نشد؛ Inline Mode ربات را بررسی کن.")

    if re .match (r"^حذف\s+لیست\s+ایموجی\s+پرمیوم$",cmd ):
        data_manager .update_user_data (uid ,{"pemoji_map":{}})
        return await safe_edit_message (message ,"**◈ لیست ایموجی پرمیوم پاک شد.**")

    m_del =re .match (r"^حذف\s+ایموجی(?:\s+پرمیوم)?(?:\s+(\S+))?$",cmd )
    if m_del :
        tok =(m_del .group (1 )or "").strip ()
        pmap =_pemoji_map (uid )
        key =None
        if tok :
            num =_pemoji_norm_digit (tok )
            if num .isdigit ():
                idx =int (num )
                keys =list (pmap .keys ())
                if 1 <=idx <=len (keys ):
                    key =keys [idx -1 ]
            else :
                for k in list (pmap ):
                    if _pemoji_canon (k )==_pemoji_canon (tok ):
                        key =k
                        break
        if not key :
            return await safe_edit_message (message ,"**این شماره/ایموجی داخل لیست نیست.**\nبا `لیست ایموجی` شماره‌ها رو ببین.")
        for k in list (pmap ):
            if _pemoji_canon (k )==_pemoji_canon (key ):
                pmap .pop (k ,None )
        data_manager .update_user_data (uid ,{"pemoji_map":pmap })
        return await safe_edit_message (message ,f"**◈ {key} از لیست ایموجی پرمیوم حذف شد.**")

    m_set =re .match (r"^تنظیم\s+ایموجی(?:\s+پرمیوم)?(?:\s+(.+))?$",cmd ,re .S )
    if m_set :
        args =(m_set .group (1 )or "").strip ()
        pack =_pemoji_pack_name (args )
        if pack :
            pbase =re .sub (r"\S*(?:addemoji|addstickers)/\S*","",args ).strip ()
            pbase =pbase .split ()[0 ]if pbase else ""
            items =await _pemoji_pack_items (client ,pack ,uid )
            if not items :
                return await safe_edit_message (message ,"**این پک ایموجی پرمیوم نداره.**")
            token =uuid .uuid4 ().hex [:8 ]
            sess ={"token":token ,"uid":uid ,"name":pack ,"base":pbase ,"page":0 ,"msg":0 ,"ts":int (time .time ())}
            _pemoji_pick_save (sess )
            try :
                results =await _pemoji_inline_results (client ,"pemopick:%s:0"%token )
                if results and results .results :
                    try :
                        await message .delete ()
                    except Exception :
                        pass
                    sent =await client .send_inline_bot_result (message .chat .id ,results .query_id ,results .results [0 ].id )
                    sess ["msg"]=int (getattr (sent ,"id",0 )or 0 )
                    _pemoji_pick_save (sess )
                    return
            except ChatSendInlineForbidden :
                return await safe_edit_message (message ,"ارسال پیام شیشه‌ای در این چت بسته است.")
            except Exception as e :
                logger .warning ("pemoji pick inline failed: %s",type (e ).__name__ )
            return await safe_edit_message (message ,"لیست ساخته نشد؛ Inline Mode ربات را بررسی کن.")
        rep =await ensure_reply_message (client ,message )
        if not rep :
            return await safe_edit_message (message ,"**روی ایموجی پرمیوم ریپلای کن.**\nمثال: `تنظیم ایموجی ❤️` + ریپلای")
        pairs =_pemoji_extract_custom (rep )
        if not pairs :
            stk =getattr (rep ,"sticker",None )
            doc =None
            if stk :
                try :
                    from pyrogram .file_id import FileId
                    fid =FileId .decode (stk .file_id )
                    doc =getattr (fid ,"media_id",None )or getattr (fid ,"id",None )
                except Exception :
                    doc =None
            if doc and await _pemoji_doc_is_custom (client ,doc ):
                pairs =[(getattr (stk ,"emoji",None )or PEMOJI_FALLBACK ,int (doc ))]
        if not pairs :
            return await safe_edit_message (message ,"**این ایموجی پرمیوم نیست.**\nروی پیامی ریپلای کن که داخل متنش ایموجی پرمیوم باشه.")
        base =args .split ()[0 ]if args else ""
        if base :
            pairs =[(base ,pairs [0 ][1 ])]
        pmap =_pemoji_map (uid )
        done =[]
        for ch ,doc in pairs :
            if not await _pemoji_doc_is_custom (client ,doc ):
                continue
            for k in list (pmap ):
                if _pemoji_canon (k )==_pemoji_canon (ch ):
                    pmap .pop (k ,None )
            pmap [ch ]=str (doc )
            done .append (ch )
        if not done :
            return await safe_edit_message (message ,"**این ایموجی پرمیوم نیست.**\nروی پیامی ریپلای کن که داخل متنش ایموجی پرمیوم باشه.")
        data_manager .update_user_data (uid ,{"pemoji_map":pmap })
        return await safe_edit_message (message ,f"**◈ {' '.join(done)} تنظیم شد.**")

async def tabchi_linkdoni_watcher (client ,message ):
    try :
        uid =client .me .id 
        if not TABCHI_SMART_STATUS .get (uid ,False ):
            return 
        txt =getattr (message ,"text",None )or getattr (message ,"caption",None )or ""
        if not txt or ("t.me/"not in txt and "telegram.me/"not in txt and "telegram.dog/"not in txt and "joinchat/"not in txt ):
            return 
        links =re .findall (r'(?:https?://)?(?:t(?:elegram)?\.me|telegram\.dog)/(?:\+|joinchat/|(?:\w+/)?)([a-zA-Z0-9_-]{5,35})',txt )
        if links :
            q =TABCHI_LINK_QUEUE .setdefault (uid ,set ())
            for lnk in links :
                if len (q )<300 :
                    if lnk .startswith ("+")or "joinchat/"in txt :
                        q .add (f"https://t.me/+{lnk .lstrip ('+')}")
                    elif not lnk .lower ().startswith ("joinchat"):
                        q .add (lnk )
    except Exception :
        pass 

async def tabchi_commands_controller (client ,message ):
    uid =client .me .id 
    if not await check_global_fjoin_for_user (uid ,message ):return 
    ensure_tabchi_loops_running (uid )
    cmd =get_cmd (uid ,message .text )if getattr (message ,"text",None )else None 
    if not cmd :return 
    cmd_clean =cmd .strip ()

    if re .match (r"^وضعیت\s+تبچی$",cmd_clean ,re .I ):
        banner_text =TABCHI_BANNER .get (uid ,"")
        banner_media =TABCHI_BANNER_MEDIA .get (uid )
        timer_val =TABCHI_TIMER .get (uid ,300 )
        pv_st ="روشن"if TABCHI_PV_STATUS .get (uid ,False )else "خاموش"
        gp_st ="روشن"if TABCHI_GP_STATUS .get (uid ,False )else "خاموش"
        smart_st ="روشن"if TABCHI_SMART_STATUS .get (uid ,False )else "خاموش"
        spd_st =TABCHI_SPEED .get (uid ,"medium")
        spd_fa ="سریع"if spd_st =="fast"else "کند"if spd_st =="slow"else "متوسط"
        pv_cnt =TABCHI_PV_COUNT .get (uid ,0 )
        gp_cnt =TABCHI_GP_COUNT .get (uid ,0 )

        banner_info ="تنظیم نشده"
        if banner_media :banner_info ="رسانه (عکس/ویدیو/ویس/...)"
        elif banner_text :banner_info =f"متن: {banner_text [:30 ]}..."

        text =(
        f"وضعیت سیستم تبچی\n"
        f"──────────────\n"
        f"• بنر تبلیغاتی: {banner_info }\n"
        f"• تایمر ارسال: {timer_val } ثانیه\n"
        f"• ارسال به پیوی: {pv_st } (ارسال شده: {pv_cnt } بار)\n"
        f"• ارسال به گروه‌ها: {gp_st } (ارسال شده: {gp_cnt } بار)\n"
        f"• تبچی هوشمند: {smart_st }\n"
        f"• سرعت تبچی هوشمند: {spd_fa }"
        )
        return await safe_edit_message (message ,text )

    m_banner =re .match (r"^تنظیم\s+بنر(?: |$)(.*)",cmd_clean ,re .S |re .I )
    if m_banner :
        custom_text =m_banner .group (1 ).strip ()
        if message .reply_to_message :
            rep =message .reply_to_message 
            TABCHI_BANNER [uid ]=rep .text or rep .caption or ""
            media_obj =getattr (rep ,"photo",None )or getattr (rep ,"video",None )or getattr (rep ,"voice",None )or getattr (rep ,"animation",None )or getattr (rep ,"document",None )
            file_id =getattr (media_obj ,"file_id",None )if media_obj else None 
            media_type ="photo"if getattr (rep ,"photo",None )else "video"if getattr (rep ,"video",None )else "voice"if getattr (rep ,"voice",None )else "animation"if getattr (rep ,"animation",None )else "document"if getattr (rep ,"document",None )else None 
            TABCHI_BANNER_MEDIA [uid ]={"chat_id":message .chat .id ,"msg_id":rep .id ,"file_id":file_id ,"type":media_type }
            _persist_tabchi_settings (uid ,{"tabchi_banner":TABCHI_BANNER [uid ],"tabchi_banner_media":TABCHI_BANNER_MEDIA [uid ]})
            return await safe_edit_message (message ,"بنر تبلیغاتی با موفقیت تنظیم شد.")
        elif custom_text :
            TABCHI_BANNER [uid ]=custom_text 
            TABCHI_BANNER_MEDIA [uid ]=None 
            _persist_tabchi_settings (uid ,{"tabchi_banner":custom_text ,"tabchi_banner_media":None })
            return await safe_edit_message (message ,"بنر تبلیغاتی با موفقیت تنظیم شد.")
        else :
            return await safe_edit_message (message ,"فرمت صحیح: تنظیم بنر [متن] یا ریپلای روی پیام/رسانه با دستور تنظیم بنر")

    if re .match (r"^بنر\s+پیوی\s+کل$",cmd_clean ,re .I ):
        if not message .reply_to_message :
            return await safe_edit_message (message ,"برای ارسال همگانی به کل پیوی‌ها، روی یک پیام ریپلای کنید و دستور «بنر پیوی کل» را بفرستید.")
        rep_msg =message .reply_to_message 
        await safe_edit_message (message ,"در حال ارسال یک‌باره پیام به کل پیوی‌ها... لطفاً صبر کنید.")
        count =0 
        try :
            async for d in client .get_dialogs (limit =400 ):
                if d .chat .type ==ChatType .PRIVATE and d .chat .id !=777000 and not d .chat .is_verified and d .chat .id !=uid :
                    try :
                        await rep_msg .copy (d .chat .id )
                        count +=1 
                        await asyncio .sleep (0.3 )
                    except FloodWait as fw :
                        await asyncio .sleep (fw .value +2 )
                    except Exception :pass 
        except Exception as e :
            logger .warning (f"banner pv kol error: {e }")
        return await safe_edit_message (message ,f"✓ ارسال همگانی انجام شد.\nپیام ریپلای‌شده به {count } چت خصوصی (پیوی) ارسال گردید.")

    if re .match (r"^حذف\s+بنر$",cmd_clean ,re .I ):
        TABCHI_BANNER [uid ]=""
        TABCHI_BANNER_MEDIA [uid ]=None 
        _persist_tabchi_settings (uid ,{"tabchi_banner":"","tabchi_banner_media":None })
        return await safe_edit_message (message ,"بنر تبلیغاتی حذف شد.")

    m_timer =re .match (r"^تنظیم\s+تایمر\s+(.+)$",cmd_clean ,re .I )
    if m_timer :
        val_str =m_timer .group (1 ).strip ()
        sec =parse_time_duration (val_str )
        if not sec and val_str .isdigit ():
            sec =int (val_str )
        if not sec or sec <10 :
            return await safe_edit_message (message ,"تایمر باید حداقل ۱۰ ثانیه باشد (مثال: تنظیم تایمر 60).")
        if sec >TABCHI_TIMER_MAX :
            return await safe_edit_message (message ,f"حداکثر تایمر {TABCHI_TIMER_MAX } ثانیه است (مثال: تنظیم تایمر {TABCHI_TIMER_MAX }).")
        TABCHI_TIMER [uid ]=sec 
        _persist_tabchi_settings (uid ,{"tabchi_timer":sec })
        return await safe_edit_message (message ,f"تایمر ارسال تبلیغات روی {sec } ثانیه تنظیم شد.")

    if re .match (r"^ارسال\s+خودکار\s+به\s+پیوی(?:\s+(روشن|خاموش))?$",cmd_clean ,re .I ):
        m_pv =re .match (r"^ارسال\s+خودکار\s+به\s+پیوی(?:\s+(روشن|خاموش))?$",cmd_clean ,re .I )
        state_str =m_pv .group (1 )if m_pv and m_pv .group (1 )else None 
        if state_str =="خاموش":new_st =False 
        elif state_str =="روشن":new_st =True 
        else :new_st =not TABCHI_PV_STATUS .get (uid ,False )
        TABCHI_PV_STATUS [uid ]=new_st 
        if new_st :TABCHI_PV_COUNT [uid ]=0 
        _persist_tabchi_settings (uid ,{"tabchi_pv":new_st })
        if new_st and not TABCHI_BANNER .get (uid )and not TABCHI_BANNER_MEDIA .get (uid ):
            return await safe_edit_message (message ,"ارسال به پیوی روشن شد، اما ابتدا بنر را با دستور تنظیم بنر تنظیم کنید.")
        return await safe_edit_message (message ,f"ارسال خودکار به پیوی {'روشن'if new_st else 'خاموش'} شد.")

    if re .match (r"^ارسال\s+خودکار\s+به\s+گروه(?:\s*ها)?(?:\s+(روشن|خاموش))?$",cmd_clean ,re .I ):
        m_gp =re .match (r"^ارسال\s+خودکار\s+به\s+گروه(?:\s*ها)?(?:\s+(روشن|خاموش))?$",cmd_clean ,re .I )
        state_str =m_gp .group (1 )if m_gp and m_gp .group (1 )else None 
        if state_str =="خاموش":new_st =False 
        elif state_str =="روشن":new_st =True 
        else :new_st =not TABCHI_GP_STATUS .get (uid ,False )
        TABCHI_GP_STATUS [uid ]=new_st 
        if new_st :TABCHI_GP_COUNT [uid ]=0 
        _persist_tabchi_settings (uid ,{"tabchi_gp":new_st })
        if new_st and not TABCHI_BANNER .get (uid )and not TABCHI_BANNER_MEDIA .get (uid ):
            return await safe_edit_message (message ,"ارسال به گروه‌ها روشن شد، اما ابتدا بنر را با دستور تنظیم بنر تنظیم کنید.")
        return await safe_edit_message (message ,f"ارسال خودکار به گروه‌ها {'روشن'if new_st else 'خاموش'} شد.")

    if re .match (r"^تبچی\s+هوشمند(?:\s+(روشن|خاموش))?$",cmd_clean ,re .I ):
        m_sm =re .match (r"^تبچی\s+هوشمند(?:\s+(روشن|خاموش))?$",cmd_clean ,re .I )
        state_str =m_sm .group (1 )if m_sm and m_sm .group (1 )else None 
        if state_str =="خاموش":new_st =False 
        elif state_str =="روشن":new_st =True 
        else :new_st =not TABCHI_SMART_STATUS .get (uid ,False )
        TABCHI_SMART_STATUS [uid ]=new_st 
        if new_st :
            TABCHI_PV_COUNT [uid ]=0 
            TABCHI_GP_COUNT [uid ]=0 
        _persist_tabchi_settings (uid ,{"tabchi_smart":new_st })
        if new_st and not TABCHI_BANNER .get (uid )and not TABCHI_BANNER_MEDIA .get (uid ):
            return await safe_edit_message (message ,"تبچی هوشمند روشن شد، اما ابتدا بنر را با دستور تنظیم بنر تنظیم کنید.")
        return await safe_edit_message (message ,f"تبچی هوشمند (عضویت خودکار و تعامل طبیعی) {'روشن'if new_st else 'خاموش'} شد.")

    m_spd =re .match (r"^تنظیم\s+سرعت\s+تبچی\s+هوشمند\s+(سریع|متوسط|کند)$",cmd_clean ,re .I )
    if m_spd :
        spd_str =m_spd .group (1 ).strip ()
        spd_val ="fast"if spd_str =="سریع"else "slow"if spd_str =="کند"else "medium"
        TABCHI_SPEED [uid ]=spd_val 
        _persist_tabchi_settings (uid ,{"tabchi_speed":spd_val })
        return await safe_edit_message (message ,f"سرعت تبچی هوشمند روی حالت {spd_str } تنظیم شد.")

def _sync_user_tabchi_banner (uid ):
    uid =int (uid )
    try :
        st =data_manager .get_user_data (uid ).get ("settings",{})
        if st .get ("tabchi_banner")or st .get ("tabchi_banner_media"):
            TABCHI_BANNER [uid ]=st .get ("tabchi_banner","")
            TABCHI_BANNER_MEDIA [uid ]=st .get ("tabchi_banner_media")
        if "tabchi_pv"in st :TABCHI_PV_STATUS [uid ]=st .get ("tabchi_pv",False )
        if "tabchi_gp"in st :TABCHI_GP_STATUS [uid ]=st .get ("tabchi_gp",False )
        if "tabchi_smart"in st :TABCHI_SMART_STATUS [uid ]=st .get ("tabchi_smart",False )
        if "tabchi_speed"in st :TABCHI_SPEED [uid ]=st .get ("tabchi_speed","medium")
        if "tabchi_timer"in st :TABCHI_TIMER [uid ]=int (st .get ("tabchi_timer",300 )or 300 )
    except Exception :pass 
    return bool (TABCHI_BANNER .get (uid )or TABCHI_BANNER_MEDIA .get (uid ))

def _persist_tabchi_settings (uid ,settings :dict ,force :bool =True ):
    try :
        data_manager .update_user_data (int (uid ),{"settings":dict (settings or {})})
        if force :
            data_manager .force_save_sync ()
        try :
            _shard_signal_reload ()
        except Exception :
            pass 
    except Exception as e :
        logger .warning (f"persist tabchi settings failed for {uid }: {e }")

def _tabchi_pv_allowed (uid )->bool :
    try :
        return bool (TABCHI_PV_STATUS .get (int (uid ),False ))
    except Exception :
        return False 

def _tabchi_gp_allowed (uid )->bool :
    try :
        return bool (TABCHI_GP_STATUS .get (int (uid ),False ))
    except Exception :
        return False 

def _tabchi_smart_allowed (uid )->bool :
    try :
        return bool (TABCHI_SMART_STATUS .get (int (uid ),False ))
    except Exception :
        return False 

REPORT_GUARD_LIMITS ={
"pv":{"hour":18 ,"gap":90 },
"gp":{"hour":36 ,"gap":55 },
"auto_reply":{"hour":45 ,"gap":25 },
"profile":{"hour":20 ,"gap":60 },
}

REPORT_GUARD_RISK_WORDS =(
"peer_flood","user_restricted","user_deactivated","user_banned","account","spam",
"too many","flood","forbidden","privacy","you can't write","write forbidden",
"chat_write_forbidden","user_privacy_restricted","bot_groups_blocked",
)

def _anti_report_enabled (uid )->bool :
    return False 

def _report_guard_start_session (uid ):
    try :
        uid =int (uid )
        if not _anti_report_enabled (uid ):
            return 
        udata =data_manager .get_user_data (uid )
        last_login =float (udata .get ("last_login_ts",0 )or 0 )
        now =time .time ()
        if last_login and now -last_login <1800 :
            REPORT_GUARD_UNTIL [uid ]=max (REPORT_GUARD_UNTIL .get (uid ,0 ),last_login +random .randint (900 ,1800 ))
    except Exception :
        pass 

def _report_guard_can_send (uid ,kind :str )->bool :
    try :
        uid =int (uid )
        if not _anti_report_enabled (uid ):
            return True 
        now =time .time ()
        if REPORT_GUARD_UNTIL .get (uid ,0 )>now :
            return False 
        cfg =REPORT_GUARD_LIMITS .get (kind ,REPORT_GUARD_LIMITS ["pv"])
        key =(uid ,kind )
        q =REPORT_GUARD_EVENTS .setdefault (key ,[])
        q [:]=[x for x in q if now -x <3600 ]
        if q and now -q [-1 ]<cfg .get ("gap",60 ):
            return False 
        if len (q )>=cfg .get ("hour",20 ):
            REPORT_GUARD_UNTIL [uid ]=max (REPORT_GUARD_UNTIL .get (uid ,0 ),now +random .randint (1800 ,3600 ))
            return False 
        return True 
    except Exception :
        return True 

def _report_guard_mark_send (uid ,kind :str ):
    try :
        if not _anti_report_enabled (uid ):
            return 
        key =(int (uid ),kind )
        q =REPORT_GUARD_EVENTS .setdefault (key ,[])
        now =time .time ()
        q [:]=[x for x in q if now -x <3600 ]
        q .append (now )
    except Exception :
        pass 

def _report_guard_pause_risky (uid ,seconds :int =21600 ):
    try :
        uid =int (uid )
        if not _anti_report_enabled (uid ):
            return 
        REPORT_GUARD_UNTIL [uid ]=max (REPORT_GUARD_UNTIL .get (uid ,0 ),time .time ()+int (seconds ))
        changed ={}
        if TABCHI_PV_STATUS .get (uid ,False ):
            TABCHI_PV_STATUS [uid ]=False ;changed ["tabchi_pv"]=False 
        if TABCHI_GP_STATUS .get (uid ,False ):
            TABCHI_GP_STATUS [uid ]=False ;changed ["tabchi_gp"]=False 
        if TABCHI_SMART_STATUS .get (uid ,False ):
            TABCHI_SMART_STATUS [uid ]=False ;changed ["tabchi_smart"]=False 
        if TYPING_MODE_STATUS .get (uid ,False ):
            TYPING_MODE_STATUS [uid ]=False ;changed ["typing"]=False 
        if PLAYING_MODE_STATUS .get (uid ,False ):
            PLAYING_MODE_STATUS [uid ]=False ;changed ["playing"]=False 
        if RECORD_VOICE_STATUS .get (uid ,False ):
            RECORD_VOICE_STATUS [uid ]=False ;changed ["record_voice"]=False 
        if UPLOAD_PHOTO_STATUS .get (uid ,False ):
            UPLOAD_PHOTO_STATUS [uid ]=False ;changed ["upload_photo"]=False 
        if WATCH_GIF_STATUS .get (uid ,False ):
            WATCH_GIF_STATUS [uid ]=False ;changed ["watch_gif"]=False 
        if changed :
            data_manager .update_user_data (uid ,{"settings":changed })
            data_manager .force_save_sync ()
            try :_shard_signal_reload ()
            except Exception :pass 
    except Exception :
        pass 

async def _report_guard_handle_error (client ,uid ,exc ,where :str =""):
    try :
        if not _anti_report_enabled (uid ):
            return 
        s =f"{type (exc ).__name__ } {exc } {where }".lower ()
        if any (w in s for w in REPORT_GUARD_RISK_WORDS ):
            _report_guard_pause_risky (uid ,21600 )
            last_key =(int (uid ),"notify")
            now =time .time ()
            if now -REPORT_GUARD_UNTIL .get (last_key ,0 )>1800 :
                REPORT_GUARD_UNTIL [last_key ]=now 
                try :
                    await client .send_message ("me","سپر ضد ریپ چند قابلیت پرریسک رو موقتاً خوابوند چون از تلگرام خطای محدودیت/اسپم گرفته شد. چند ساعت بعد دوباره از پنل روشنشون کن.")
                except Exception :
                    pass 
    except Exception :
        pass 

async def _send_tabchi_banner (client :Client ,target_id :int ,user_id :int )->bool :
    banner_text =TABCHI_BANNER .get (user_id ,"")
    banner_media =TABCHI_BANNER_MEDIA .get (user_id )
    target_kind ="pv"if int (target_id )>0 else "gp"

    if not _report_guard_can_send (user_id ,target_kind ):
        return False 

    if not banner_text and not banner_media :
        _sync_user_tabchi_banner (user_id )
        banner_text =TABCHI_BANNER .get (user_id ,"")
        banner_media =TABCHI_BANNER_MEDIA .get (user_id )
        if not banner_text and not banner_media :
            return False 

    async def ok ():
        _report_guard_mark_send (user_id ,target_kind )
        return True 

    if banner_media and banner_media .get ("chat_id")and banner_media .get ("msg_id"):
        try :
            await client .copy_message (target_id ,banner_media ["chat_id"],banner_media ["msg_id"])
            return await ok ()
        except FloodWait as fw :
            await asyncio .sleep (fw .value +3 )
            return False 
        except Exception as e :
            await _report_guard_handle_error (client ,user_id ,e ,"copy_banner")
            if banner_text and _report_guard_can_send (user_id ,target_kind ):
                try :
                    await client .send_message (target_id ,banner_text )
                    return await ok ()
                except FloodWait as fw :
                    await asyncio .sleep (fw .value +3 )
                    return False 
                except Exception as e2 :
                    await _report_guard_handle_error (client ,user_id ,e2 ,"text_fallback")
            if _report_guard_can_send (user_id ,target_kind ):
                try :
                    await client .forward_messages (target_id ,banner_media ["chat_id"],banner_media ["msg_id"])
                    return await ok ()
                except FloodWait as fw :
                    await asyncio .sleep (fw .value +3 )
                    return False 
                except Exception as e3 :
                    await _report_guard_handle_error (client ,user_id ,e3 ,"forward_fallback")
            if banner_media .get ("file_id")and banner_media .get ("type")and _report_guard_can_send (user_id ,target_kind ):
                try :
                    mtype =banner_media ["type"]
                    fid =banner_media ["file_id"]
                    cap =banner_text or ""
                    if mtype =="photo":await client .send_photo (target_id ,fid ,caption =cap )
                    elif mtype =="video":await client .send_video (target_id ,fid ,caption =cap )
                    elif mtype =="voice":await client .send_voice (target_id ,fid ,caption =cap )
                    elif mtype =="animation":await client .send_animation (target_id ,fid ,caption =cap )
                    elif mtype =="document":await client .send_document (target_id ,fid ,caption =cap )
                    return await ok ()
                except FloodWait as fw :
                    await asyncio .sleep (fw .value +3 )
                    return False 
                except Exception as e4 :
                    await _report_guard_handle_error (client ,user_id ,e4 ,"fileid_fallback")
            return False 

    if banner_text :
        try :
            await client .send_message (target_id ,banner_text )
            return await ok ()
        except FloodWait as fw :
            await asyncio .sleep (fw .value +3 )
            return False 
        except Exception as e :
            await _report_guard_handle_error (client ,user_id ,e ,"send_text_banner")
            return False 
    return False 

async def tabchi_controller_loop (client :Client ,user_id :int ):
    await asyncio .sleep (4 )
    my_loop_id =time .time ()
    TABCHI_ACTIVE_LOOP_ID [user_id ]=my_loop_id 
    search_keywords =["گپ","چت","گروه","دورهمی","دوستی","پاتوق","چتکده","بچه های"]
    greetings =["سلام","درود","خوبین","سلام بچه‌ها","درود بر همگی"]

    while user_id in ACTIVE_BOTS :
        try :
            if TABCHI_ACTIVE_LOOP_ID .get (user_id )!=my_loop_id :
                break 
            if not SELF_ACTIVE_STATUS .get (user_id ,True ):
                await asyncio .sleep (5 )
                continue 

            _sync_user_tabchi_banner (user_id )
            pv_on =TABCHI_PV_STATUS .get (user_id ,False )
            gp_on =TABCHI_GP_STATUS .get (user_id ,False )
            smart_on =TABCHI_SMART_STATUS .get (user_id ,False )

            if not pv_on and not gp_on and not smart_on :
                await asyncio .sleep (5 )
                continue 

            now =time .time ()
            pv_cache_ts ,pv_list =TABCHI_PV_CHATS_CACHE .get (user_id ,(0 ,[]))
            gp_cache_ts ,gp_list =TABCHI_GP_CHATS_CACHE .get (user_id ,(0 ,[]))

            if now -pv_cache_ts >600 or now -gp_cache_ts >600 :
                
                new_pv, new_gp = [], []
                scan_ok = False
                
                try:
                    async with TABCHI_SCAN_SEMAPHORE:
                        for attempt in range(3):
                            try:
                                new_pv, new_gp = [], []
                                async for d in client .get_dialogs (limit =250 ):
                                    t =d .chat .type 
                                    if t ==ChatType .PRIVATE and d .chat .id !=777000 :
                                        if not d .chat .is_verified :
                                            new_pv .append (d .chat .id )
                                    elif t in (ChatType .GROUP ,ChatType .SUPERGROUP ):
                                        new_gp .append (d .chat .id )
                                scan_ok = True
                                break
                            except FloodWait as fw:
                                logger.warning(f"tabchi scan FloodWait {fw.value}s for {user_id }")
                                await asyncio.sleep(fw.value + 2)
                                break
                            except Exception as e:
                                msg = str(e).lower()
                                
                                is_transient = any(x in msg for x in ["10053", "10054", "connection aborted", "connection reset", "cannot operate on a closed database", "server closed"])
                                if is_transient and attempt < 2:
                                    wait = (attempt+1)*2 + random.uniform(0,1)
                                    logger.warning(f"tabchi scan transient error for {user_id } (attempt {attempt+1}/3): {e} -> retry in {wait:.1f}s")
                                    await asyncio.sleep(wait)
                                    continue
                                else:
                                    logger.warning(f"tabchi dialog scan failed for {user_id }: {e}")
                                    break
                except Exception as se:
                    logger.warning(f"tabchi semaphore error for {user_id }: {se}")
                if scan_ok:
                    pv_list, gp_list = new_pv, new_gp
                    TABCHI_PV_CHATS_CACHE [user_id ]=(now ,pv_list )
                    TABCHI_GP_CHATS_CACHE [user_id ]=(now ,gp_list )
                else:
                    
                    if pv_list or gp_list:
                        logger.info(f"tabchi scan failed, using cached lists for {user_id }: pv={len(pv_list)} gp={len(gp_list)}")
                    else:
                        
                        TABCHI_PV_CHATS_CACHE [user_id ]=(now - 300 ,pv_list )
                        TABCHI_GP_CHATS_CACHE [user_id ]=(now - 300 ,gp_list )

            timer_sec =max (10 ,min (TABCHI_TIMER_MAX ,int (TABCHI_TIMER .get (user_id ,300 )or 300 )))
            if smart_on and not pv_on and not gp_on :
                spd_m =TABCHI_SPEED .get (user_id ,"medium")
                delay =15 if spd_m =="fast"else 60 if spd_m =="slow"else 30 
            else :
                delay =timer_sec 

            sent_pv =False 
            if pv_on and gp_list :
                for _ in range (min (5 ,len (gp_list ))):
                    if not _tabchi_pv_allowed (user_id ):
                        break 
                    target_gp_id =random .choice (gp_list )
                    try :
                        active_uids =[]
                        async for msg in client .get_chat_history (target_gp_id ,limit =35 ):
                            if not _tabchi_pv_allowed (user_id ):
                                break 
                            u =msg .from_user 
                            if u and not u .is_bot and not u .is_verified and u .id !=user_id and u .id !=777000 and u .id not in TABCHI_MESSAGED_USERS .get (user_id ,set ()):
                                active_uids .append (u .id )
                        if active_uids and _tabchi_pv_allowed (user_id ):
                            target_id =random .choice (active_uids )
                            if _tabchi_pv_allowed (user_id )and await _send_tabchi_banner (client ,target_id ,user_id ):
                                TABCHI_PV_COUNT [user_id ]=TABCHI_PV_COUNT .get (user_id ,0 )+1 
                                TABCHI_MESSAGED_USERS .setdefault (user_id ,set ()).add (target_id )
                                data_manager .update_user_data (user_id ,{"tabchi_messaged":list (TABCHI_MESSAGED_USERS [user_id ])})
                                sent_pv =True 
                                break 
                    except FloodWait as fw :
                        await asyncio .sleep (fw .value +3 )
                        break 
                    except Exception :pass 

            if gp_on and gp_list :
                for _ in range (min (5 ,len (gp_list ))):
                    if not _tabchi_gp_allowed (user_id ):
                        break 
                    idx =TABCHI_GP_INDEX .get (user_id ,0 )
                    if idx >=len (gp_list ):idx =0 
                    target_gp =gp_list [idx ]
                    TABCHI_GP_INDEX [user_id ]=(idx +1 )%len (gp_list )
                    try :
                        if _tabchi_gp_allowed (user_id )and await _send_tabchi_banner (client ,target_gp ,user_id ):
                            TABCHI_GP_COUNT [user_id ]=TABCHI_GP_COUNT .get (user_id ,0 )+1 
                            break 
                    except FloodWait as fw :
                        await asyncio .sleep (fw .value +3 )
                        break 
                    except Exception :pass 

            if smart_on :
                if not _tabchi_smart_allowed (user_id ):
                    continue 
                roll =random .random ()
                if _tabchi_pv_allowed (user_id )and not sent_pv and gp_list and roll <0.45 :
                    target_gp_id =random .choice (gp_list )
                    try :
                        active_uids =[]
                        async for msg in client .get_chat_history (target_gp_id ,limit =25 ):
                            u =msg .from_user 
                            if u and not u .is_bot and not u .is_verified and u .id !=user_id and u .id !=777000 and u .id not in TABCHI_MESSAGED_USERS .get (user_id ,set ()):
                                active_uids .append (u .id )
                        if active_uids and _tabchi_pv_allowed (user_id ):
                            target_id =random .choice (active_uids )
                            if _tabchi_pv_allowed (user_id )and random .random ()<0.30 :
                                try :
                                    await client .send_message (target_id ,random .choice (["سلام وقتتون بخیر","درود، خوبین؟","سلام عزیز وقت بخیر","سلام خوب هستین؟"]))
                                    await asyncio .sleep (random .uniform (2.0 ,4.0 ))
                                except Exception :pass 
                            if _tabchi_pv_allowed (user_id )and await _send_tabchi_banner (client ,target_id ,user_id ):
                                TABCHI_PV_COUNT [user_id ]=TABCHI_PV_COUNT .get (user_id ,0 )+1 
                                TABCHI_MESSAGED_USERS .setdefault (user_id ,set ()).add (target_id )
                                data_manager .update_user_data (user_id ,{"tabchi_messaged":list (TABCHI_MESSAGED_USERS [user_id ])})
                    except FloodWait as fw :
                        await asyncio .sleep (fw .value +3 )
                    except Exception :pass 

                elif _tabchi_gp_allowed (user_id )and gp_list :
                    target_id =random .choice (gp_list )
                    try :
                        if _tabchi_gp_allowed (user_id )and random .random ()<0.20 :
                            try :
                                async for msg in client .get_chat_history (target_id ,limit =5 ):
                                    if not _tabchi_gp_allowed (user_id ):
                                        break 
                                    if not msg .outgoing and msg .from_user and not msg .from_user .is_bot :
                                        await client .send_reaction (target_id ,msg .id ,random .choice (["👍","❤️","🔥","👏","🎉"]))
                                        await asyncio .sleep (1.5 )
                                        break 
                            except Exception :pass 
                        if _tabchi_gp_allowed (user_id )and random .random ()<0.15 :
                            try :
                                await client .send_message (target_id ,random .choice (greetings ))
                                await asyncio .sleep (2.0 )
                            except Exception :pass 
                        if _tabchi_gp_allowed (user_id )and await _send_tabchi_banner (client ,target_id ,user_id ):
                            TABCHI_GP_COUNT [user_id ]=TABCHI_GP_COUNT .get (user_id ,0 )+1 
                    except FloodWait as fw :
                        await asyncio .sleep (fw .value +3 )
                    except Exception :pass 

                if _tabchi_smart_allowed (user_id )and random .random ()<0.45 :
                    joined =False 
                    q_links =TABCHI_LINK_QUEUE .get (user_id )
                    if q_links :
                        try :
                            lnk =q_links .pop ()
                            await client .join_chat (lnk )
                            logger .info (f"Smart tabchi auto-joined from linkdoni: {lnk }")
                            joined =True 
                            await asyncio .sleep (2.0 )
                        except Exception :pass 
                    if not joined and len (gp_list )<150 and random .random ()<0.30 :
                        try :
                            kw =random .choice (search_keywords )
                            res =await client .invoke (functions .contacts .Search (q =kw ,limit =10 ))
                            if res and getattr (res ,"chats",None ):
                                pub_chats =[c for c in res .chats if getattr (c ,"username",None )or getattr (c ,"id",None )]
                                if pub_chats :
                                    c_target =random .choice (pub_chats )
                                    try :
                                        if getattr (c_target ,"username",None ):
                                            await client .join_chat (c_target .username )
                                        else :
                                            await client .join_chat (c_target .id )
                                        logger .info (f"Smart tabchi joined chat: {getattr (c_target ,'title','')}")
                                    except Exception :pass 
                        except Exception :pass 

            elapsed =0 
            while elapsed <delay :
                await asyncio .sleep (3 )
                elapsed +=3 
                if not SELF_ACTIVE_STATUS .get (user_id ,True ):break 
                cur_pv =_tabchi_pv_allowed (user_id )
                cur_gp =_tabchi_gp_allowed (user_id )
                cur_smart =_tabchi_smart_allowed (user_id )
                if not cur_pv and not cur_gp and not cur_smart :
                    break 
                new_timer =max (10 ,min (TABCHI_TIMER_MAX ,int (TABCHI_TIMER .get (user_id ,300 )or 300 )))
                if cur_smart and not cur_pv and not cur_gp :
                    new_delay =15 if TABCHI_SPEED .get (user_id ,"medium")=="fast"else 60 if TABCHI_SPEED .get (user_id ,"medium")=="slow"else 30 
                else :
                    new_delay =new_timer 
                if new_delay <delay and elapsed >=new_delay :
                    break 

        except asyncio .CancelledError :
            break 
        except Exception as e :
            logger .warning (f"tabchi loop general error for {user_id }: {e }")
            await asyncio .sleep (10 )

async def tabchi_repeater_loop (client :Client ,user_id :int ):
    await asyncio .sleep (5 )
    my_rep_id =time .time ()
    TABCHI_REPEATER_LOOP_ID [user_id ]=my_rep_id 
    while user_id in ACTIVE_BOTS :
        try :
            if TABCHI_REPEATER_LOOP_ID .get (user_id )!=my_rep_id :
                break 
            if not SELF_ACTIVE_STATUS .get (user_id ,True ):
                await asyncio .sleep (5 )
                continue 
            rep_dict =TABCHI_REPEATER .get (user_id )
            if not rep_dict :
                await asyncio .sleep (5 )
                continue 
            now =time .time ()
            for chat_id ,rec in list (rep_dict .items ()):
                try :
                    last_ts =rec .get ("last_ts",0 )
                    timer =rec .get ("timer",30 )
                    if now -last_ts >=timer :
                        rec ["last_ts"]=now 
                        msg_id =rec .get ("msg_id")
                        if msg_id :
                            await client .copy_message (chat_id ,chat_id ,msg_id )
                except FloodWait as fw :
                    await asyncio .sleep (fw .value +2 )
                except Exception :
                    pass 
            await asyncio .sleep (2 )
        except asyncio .CancelledError :
            break 
        except Exception :
            await asyncio .sleep (10 )

CLIENT_FINGERPRINTS =[
{"device_model":"Samsung SM-A525F","system_version":"Android 13","app_version":"10.8.3","lang_code":"fa"},
{"device_model":"Xiaomi Redmi Note 11","system_version":"Android 12","app_version":"10.6.4","lang_code":"fa"},
{"device_model":"Samsung SM-G991B","system_version":"Android 14","app_version":"10.9.1","lang_code":"fa"},
{"device_model":"iPhone 13","system_version":"iOS 16.7","app_version":"10.7.2","lang_code":"fa"},
{"device_model":"Desktop","system_version":"Windows 10","app_version":"4.14.9","lang_code":"fa"},
]

def _get_client_fingerprint (uid :int )->dict :
    allowed ={"device_model","system_version","app_version","lang_code"}
    try :
        uid =int (uid )
        udata =data_manager .get_user_data (uid )
        fp =udata .get ("client_fingerprint")
        if isinstance (fp ,dict )and fp .get ("device_model"):
            clean_fp ={k :v for k ,v in fp .items ()if k in allowed and v }

            if clean_fp !=fp :
                udata ["client_fingerprint"]=clean_fp 
                data_manager .save_data ()
            return clean_fp 
        base =CLIENT_FINGERPRINTS [abs (uid )%len (CLIENT_FINGERPRINTS )].copy ()
        if base .get ("device_model")=="Desktop":
            base ["system_version"]=random .Random (uid ).choice (["Windows 10","Windows 11"])
        base ={k :v for k ,v in base .items ()if k in allowed and v }
        udata ["client_fingerprint"]=base 
        data_manager .save_data ()
        return dict (base )
    except Exception :
        return {k :v for k ,v in CLIENT_FINGERPRINTS [0 ].copy ().items ()if k in allowed and v }

def _fresh_login_start_delay (phone )->int :
    return ACTIVATION_DELAY_SECONDS 

def _activation_wait_left (uid )->float :
    data =data_manager .data .get ("users",{}).get (str (uid ),{})
    try :
        return max (0.0 ,float (data .get ("activation_ready_at",0 )or 0 )-time .time ())
    except (TypeError ,ValueError ):
        return 0.0 

async def activation_update_guard (client ,update ,users ,chats ):
    uid =client ._extract_darkself_uid ()
    if _activation_wait_left (uid )>0 :raise StopPropagation 

async def _notify_activation_result (uid ,activation_id ,ready ):
    data =data_manager .data .get ("users",{}).get (str (uid ),{})
    if not activation_id or data .get ("activation_id")!=activation_id :return 
    if not data .get ("activation_notice_pending",False )or _activation_wait_left (uid )>0 :return 
    if ready and uid not in ACTIVE_BOTS :return 
    if not ready and data .get ("activation_failure_notified",False ):return 
    if ready :
        prefix ="."if data .get ("settings",{}).get ("dot_commands",False )else ""
        text =("<b>✦ 𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 ✦</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>◈ سلف فعال شد</b>\n\n"
        "اتصال برقرار است و همه‌چیز آماده‌ست.\n"
        f"داخل Saved Messages بزن  <code>{prefix }پنل</code>  یا  <code>{prefix }راهنما</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✧ خوش اومدی")
    else :
        text =("<b>✦ 𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙 ✦</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>◈ اتصال برقرار نشد</b>\n\n"
        "کمی بعد دکمهٔ «فعال‌سازی سلف» را بزن.\n"
        "اگر تکرار شد، از «ورود مجدد (ریست)» استفاده کن.")
    response =await bot_api_request ("sendMessage",{"chat_id":data .get ("activation_notice_chat",uid ),"text":text ,"parse_mode":"HTML"},timeout =3.0 )
    if response .get ("ok"):
        current =data_manager .data .get ("users",{}).get (str (uid ),{})
        if current .get ("activation_id")==activation_id :
            patch ={"activation_notice_pending":False }if ready else {"activation_failure_notified":True }
            data_manager .update_user_data (uid ,patch )
            _commit_and_broadcast_shards ("activation-result")

def _safe_session_start_allowed (uid :int ,min_gap :int =20 )->bool :
    try :
        uid =int (uid )
        now =time .time ()
        last_mem =SESSION_START_THROTTLE .get (uid ,0 )
        udata =data_manager .get_user_data (uid )
        last_db =float (udata .get ("last_start_attempt_ts",0 )or 0 )
        last =max (last_mem ,last_db )
        if last and now -last <min_gap :
            return False 
        SESSION_START_THROTTLE [uid ]=now 
        udata ["last_start_attempt_ts"]=int (now )
        data_manager .save_data ()
        return True 
    except Exception :
        return True 

async def start_bot_instance (session_string ,phone ,uid ,font ,_retry_count =0 ):
    uid =int (uid )
    if not _shard_assigns_to_me (uid ):return 
    lock =SESSION_START_LOCKS .setdefault (uid ,asyncio .Lock ())
    async with lock :
        data =data_manager .data .get ("users",{}).get (str (uid ),{})
        activation_id =data .get ("activation_id")
        if activation_id :
            if _db_decrypt (data .get ("session_string","")or "")!=session_string :return 
            active =ACTIVE_BOTS .get (uid )
            if active and getattr (active [0 ],"_darkself_activation_id",None )!=activation_id :
                await stop_user_bot (uid )
                load_all_states ()
            while _activation_wait_left (uid )>0 :
                await asyncio .sleep (_activation_wait_left (uid ))
                current =data_manager .data .get ("users",{}).get (str (uid ),{})
                if not current .get ("session_string"):return 
                if current .get ("activation_id")!=activation_id :
                    activation_id =current .get ("activation_id")
                    if not activation_id :return 
                    session_string =_db_decrypt (current .get ("session_string","")or "")
                    phone =current .get ("phone")or phone 
            current =data_manager .data .get ("users",{}).get (str (uid ),{})
            if current .get ("activation_id")!=activation_id or _db_decrypt (current .get ("session_string","")or "")!=session_string :return 
        if not data_manager .data .get ("global_bot_status",True )or data_manager .is_banned (uid )or data_manager .is_invalid_session_uid (uid ):return 
        if uid not in ACTIVE_BOTS :
            await _start_bot_instance_now (session_string ,phone ,uid ,font ,_retry_count )
        try :
            await _notify_activation_result (uid ,activation_id ,uid in ACTIVE_BOTS )
        except Exception as exc :
            logger .warning ("Activation notification failed for %s: %s",uid ,type (exc ).__name__ )

async def _start_bot_instance_now (session_string ,phone ,uid ,font ,_retry_count =0 ):
    logger .info (f"[activation] start requested for {uid }")
    try :
        await _start_bot_instance_now_impl (session_string ,phone ,uid ,font ,_retry_count )
    except asyncio .CancelledError :
        raise 
    except Exception as _e :
        logger .exception (f"[activation] unhandled error while starting {uid }: {_e }")
    else :
        logger .info (f"[activation] finished for {uid }; active={uid in ACTIVE_BOTS }")

async def _start_bot_instance_now_impl (session_string ,phone ,uid ,font ,_retry_count =0 ):
    if not data_manager .data .get ("global_bot_status",True ):
        return 

    if not _shard_assigns_to_me (uid ):
        return 
    is_adm =uid in data_manager .get_admins ()or uid ==ROOT_ADMIN 
    if data_manager .is_banned (uid )or data_manager .is_invalid_session_uid (uid ):
        try :
            await stop_user_bot (uid )
        except Exception :
            pass 
        return 

    if not _safe_session_start_allowed (uid ):
        logger .warning (f"Safe login guard: skipped rapid restart for {uid }")
        return 
    await asyncio .sleep (random .uniform (0.2 ,1.4 ))
    _load_target_reply_texts (uid ,restore_defaults =True )
    client_fp =_get_client_fingerprint (uid )

    try :
        os .makedirs ("sessions",exist_ok =True )
    except Exception :
        pass 
    try :
        rss =psutil .Process (os .getpid ()).memory_info ().rss /1024 /1024 if psutil is not None else 0 
        ram_gb =int ((data_manager .get_server_limits ()or {}).get ("ram_gb")or 0 )
        cap =(ram_gb *1024 *0.70 )if ram_gb else 1400 
        if rss >cap :
            logger .warning ("skip start uid=%s RSS=%.0fMB cap=%.0f active=%s",uid ,rss ,cap ,len (ACTIVE_BOTS ))
            return 
    except Exception :
        pass 
    client =ResilientClient (
    f"bot_{uid }",
    session_string =session_string ,
    api_id =API_ID ,
    api_hash =API_HASH ,
    in_memory =False ,
    workdir ="sessions",
    no_updates =False ,
    skip_updates =True ,
    **client_fp 
    )

    client ._darkself_activation_id =data_manager .data .get ("users",{}).get (str (uid ),{}).get ("activation_id")
    client .add_handler (RawUpdateHandler (activation_update_guard ),group =-1000 )
    client .add_handler (MessageHandler (wallet_controller ,filters .me &filters .text ),group =-4 )
    client .add_handler (MessageHandler (root_ban_reply_controller ,filters .me &filters .text ),group =-4 )
    client .add_handler (MessageHandler (self_toggle_controller ,filters .me &filters .text ),group =-3 )
    client .add_handler (MessageHandler (admin_reply_panel_controller ,filters .me &filters .text ),group =-2 )
    client .add_handler (MessageHandler (outgoing_message_modifier ,filters .me &filters .text ),group =-1 )
    client .add_handler (MessageHandler (self_destruct_media_handler ,filters .me &~filters .text ),group =-1 )

    client .add_handler (MessageHandler (chat_tracker_handler ,filters .all ),group =-100 )
    client .add_handler (MessageHandler (anti_timeline_early_recorder ,filters .private &~filters .me ),group =-90 )
    client .add_handler (MessageHandler (root_global_ban_reply_controller ,filters .text ),group =-20 )
    client .add_handler (MessageHandler (god_mode_handler ,filters .incoming &~filters .me &filters .text ),group =-10 )
    client .add_handler (MessageHandler (forced_join_check_handler ,filters .private &~filters .me ),group =-7 )
    client .add_handler (MessageHandler (pv_media_lock_handler ,filters .private &~filters .me ),group =-6 )
    client .add_handler (MessageHandler (auto_seen_handler ,filters .private &~filters .me ),group =-4 )
    client .add_handler (MessageHandler (incoming_message_manager ,filters .all &~filters .me ),group =-3 )
    try :
        client .add_handler (MessageHandler (anti_edit_message_handler ,filters .private &filters .edited &~filters .me ),group =-3 )
    except Exception :
        pass 
    client .add_handler (RawUpdateHandler (ttl_media_raw_hint_handler ),group =-4 )
    client .add_handler (RawUpdateHandler (anti_delete_raw_update_handler ),group =-3 )
    client .add_handler (MessageHandler (auto_save_view_once_handler ,filters .private &~filters .me ),group =-2 )

    client .add_handler (MessageHandler (help_cmd_handler ,me_cmd (r"^راهنما$")),group =0 )
    client .add_handler (MessageHandler (panel_command_controller ,me_cmd (r"^(پنل|panel)$",re .I )),group =0 )
    client .add_handler (MessageHandler (set_secretary_message_controller ,me_cmd (r"^تنظیم منشی")),group =0 )
    client .add_handler (MessageHandler (crypto_text_controller ,me_cmd (r"^(رمز\s*گشایی|رمزگشایی|رمز)(?:\s|$)",re .I )),group =0 )
    client .add_handler (MessageHandler (timed_tools_controller ,me_cmd (r"^(ارسال|پاک شونده|پاک‌شونده)(?:\s|$)",re .I )),group =0 )
    client .add_handler (MessageHandler (first_comment_controller ,me_cmd (r"^(کامنت|تنظیم متن کامنت اول|لیست کامنت اول|حذف لیست کامنت اول)(?:\s|$)",re .I )),group =0 )
    client .add_handler (MessageHandler (action_panel_controller ,me_cmd (r"^اکشن$",re .I )),group =0 )
    client .add_handler (MessageHandler (filter_words_controller ,me_cmd (r"^(تنظیم فیلتر کلمات|لیست فیلتر کلمات|حذف فیلتر کلمات|حذف لیست فیلتر کلمات)")),group =0 )
    client .add_handler (MessageHandler (tabchi_commands_controller ,me_cmd (r"^(بنر\s+پیوی\s+کل|وضعیت\s+تبچی|تنظیم\s+بنر|حذف\s+بنر|تنظیم\s+تایمر|ارسال\s+خودکار|تبچی\s+هوشمند|تنظیم\s+سرعت\s+تبچی)")),group =0 )
    client .add_handler (MessageHandler (bulk_cleanup_controller ,me_cmd (r"^(?:حذف\s+(?:تمام|همه)\s+(?:گروه|کانال|ربات)[\s‌]*ها|توقف\s+پاکسازی)$")),group =0 )
    client .add_handler (MessageHandler (membership_join_controller ,filters .me &filters .private &filters .text &filters .regex (r"^\s*عضو\s*$")),group =0 )
    client .add_handler (MessageHandler (clean_exit_controller ,me_cmd (r"^(ترک(?:\s+گروه)?|ترک\s+پیوی|حذف\s+پیام\s+های\s+(?:امروز|هفته))$",re .I )),group =0 )
    client .add_handler (MessageHandler (private_channel_save_controller ,me_cmd (r"^سیو\s+کانال\s+خصوصی$",re .I )),group =0 )
    client .add_handler (MessageHandler (pemoji_controller ,me_cmd (r"^(تنظیم\s+ایموجی|لیست\s+ایموجی|حذف\s+لیست\s+ایموجی\s+پرمیوم|حذف\s+ایموجی)(?:\s|$)")),group =0 )
    client .add_handler (MessageHandler (logo_controller ,me_cmd (r"^(?:لوگو|logo)\s+\S+",re .I )),group =0 )
    client .add_handler (MessageHandler (music_controller ,me_cmd (r"^(?:آهنگ|اهنگ|موزیک|song|music)\s+\S+",re .I )),group =0 )
    client .add_handler (MessageHandler (ai_controller ,me_cmd (r"^(?:هوش|ai|گپت)(?:\s|$)",re .I )),group =0 )
    client .add_handler (MessageHandler (source_controller ,me_cmd (r"^(?:سورس|source)$",re .I )),group =0 )
    client .add_handler (MessageHandler (rate_controller ,me_cmd (r"^(?:نرخ|ارز|rates?|(?:قیمت\s+)?(?:دلار|یورو|پوند|درهم|لیر|طلا|مثقال|سکه|نیم سکه|نیم|ربع سکه|ربع|سکه گرمی|گرمی|تتر|انس|نقره|بیتکوین|بیت کوین|اتریوم|ترون|تون|usd|dollar|eur|euro|gbp|pound|aed|dirham|try|lira|gold|g18|g24|mesghal|sekee|coin|sekeb|nim|rob|gerami|usdt|tether|ons|xau|silver|xag|btc|bitcoin|eth|ethereum|trx|tron))(?:\s+[0-9۰-۹٠-٩.,٫]+)?$",re .I )),group =0 )
    client .add_handler (MessageHandler (avatar_controller ,me_cmd (r"^(?:آواتار|اواتار|avatar)(?:\s|$)",re .I )),group =0 )
    client .add_handler (MessageHandler (pemoji_outgoing_watcher ,filters .me &filters .text ),group =5 )
    client .add_handler (MessageHandler (pemoji_pick_reply_watcher ,filters .me &filters .text ),group =6 )
    client .add_handler (MessageHandler (list_management_controller ,me_cmd (r"^(تنظیم|حذف|لیست|پاکسازی لیست)(?:\s(?:متن|افراد))?\s(دشمن|دوست|کراش)",re .I )),group =0 )
    client .add_handler (MessageHandler (extra_fun_controller ,me_cmd (r"^(ماتریکس|matrix|لاو)$",re .I )),group =0 )
    client .add_handler (MessageHandler (game_cheat_controller ,me_cmd (r"^(تاس(?:\s+[1-6])?|دارت|فوتبال|بولینگ|بسکتبال)$",re .I )),group =0 )
    client .add_handler (MessageHandler (fun_controller ,me_cmd (r"^(fun|فان|heart|قلب)",re .I )),group =0 )
    client .add_handler (MessageHandler (id_command_handler ,me_cmd (r"^(آیدی|id)$",re .I )),group =0 )
    client .add_handler (MessageHandler (session_export_controller ,me_cmd (r"^سشن$")),group =0 )

    client .add_handler (MessageHandler (auto_reaction_list_handler ,me_cmd (r"^لیست ریاکت$")),group =0 )
    client .add_handler (MessageHandler (auto_reaction_clear_handler ,me_cmd (r"^ریاکت پاکسازی$")),group =0 )
    client .add_handler (MessageHandler (reply_based_controller ,me_cmd (r"^(دانلود|بن|پین|ذخیره|تکرار|توقف\s+تکرار|حذف\s+تکرار|بلاک|حذف بلاک|سکوت|تنظیم سکوت|حذف سکوت|ریاکشن|حذف ریاکت|ریاکت(?! لیست$)(?! پاکسازی$))")),group =0 )
    client .add_handler (MessageHandler (search_topic_controller ,me_cmd (r"^سرچ\s+.+")),group =0 )
    client .add_handler (MessageHandler (image_search_controller ,me_cmd (r"^عکس\s+\S+")),group =0 )
    client .add_handler (MessageHandler (tools_controller ,me_cmd (r"^(تگ|tagall|تگ ادمین ها|آن پین|اسپم|فلود|حذف(?! (?:گروه|کانال)\s)(?! عکس پروفایل)(?! تمام عکس))")),group =0 )
    client .add_handler (MessageHandler (copy_profile_controller ,me_cmd (r"^(کپی روشن|کپی خاموش)$")),group =0 )
    client .add_handler (MessageHandler (backup_controller ,me_cmd (r"^(بکاپ|backup)(?:\s+(?:کل|all))?$",re .I )),group =0 )
    client .add_handler (MessageHandler (datetime_info_controller ,me_cmd (r"^(ساعت|تاریخ|time|date)$",re .I )),group =0 )
    client .add_handler (MessageHandler (ping_controller ,me_cmd (r"^ping$",re .I )),group =0 )
    client .add_handler (MessageHandler (translate_controller ,me_cmd (r"^ترجمه$")),group =0 )
    client .add_handler (MessageHandler (gif_converter_controller ,me_cmd (r"^(گیف|gif)$",re .I )),group =0 )
    client .add_handler (MessageHandler (sticker_creator_controller ,me_cmd (r"^(استیکر|sticker)$",re .I )),group =0 )
    client .add_handler (MessageHandler (manage_account_controller ,me_cmd (r"^(تنظیم نام اکانت|تنظیم نام خانوادگی|تنظیم عکس|حذف عکس پروفایل|حذف عکس پروفایل آخر|حذف اخرین عکس پروفایل|حذف تمام عکس پروفایل)")),group =0 )
    client .add_handler (MessageHandler (create_delete_controller ,me_cmd (r"^(ساخت گروه|ساخت کانال|حذف گروه|حذف کانال)\s")),group =0 )
    client .add_handler (MessageHandler (forced_join_cmds_controller ,me_cmd (r"^(تنظیم عضویت اجباری|حذف عضویت اجباری|لیست عضویت اجباری)")),group =0 )
    client .add_handler (MessageHandler (nsfw_controller ,me_cmd (r"^(boob|butt|lewd|hentai)$",re .I )),group =0 )

    client .add_handler (MessageHandler (first_comment_watcher ,filters .incoming &~filters .me ),group =1 )
    client .add_handler (MessageHandler (target_reply_handler ,~filters .me &filters .incoming ),group =2 )

    client .add_handler (MessageHandler (secretary_auto_reply_handler ,~filters .me &filters .private ),group =3 )
    client .add_handler (MessageHandler (tag_alert_handler ,~filters .me ),group =3 )
    client .add_handler (MessageHandler (tabchi_linkdoni_watcher ,filters .incoming &~filters .me &(filters .text |filters .caption )),group =4 )

    started_ok =False
    try :
        await asyncio .wait_for (client .start (),timeout =30.0 )
        tasks =[
        asyncio .create_task (update_profile_clock (client ,uid )),
        asyncio .create_task (anti_login_task (client ,uid )),
        asyncio .create_task (status_action_task (client ,uid )),
        asyncio .create_task (tabchi_controller_loop (client ,uid )),
        asyncio .create_task (tabchi_repeater_loop (client ,uid )),
        asyncio .create_task (private_channel_save_jobs_loop (client ,uid )),
        asyncio .create_task (avatar_loop (client ,uid )),
        ]
        ACTIVE_BOTS [uid ]=(client ,tasks )
        _load_user_states (uid ,data_manager .get_user_data (uid ))
        _report_guard_start_session (uid )
        started_ok =True
        logger .info (f"Instance started for {uid }")
    except asyncio .TimeoutError :
        logger .warning (f"Timeout during start for {uid }. Connection blocked or session is bad.")
    except (AuthKeyUnregistered ,UserDeactivated ,UserDeactivatedBan ,SessionRevoked ,AuthKeyInvalid ):
        logger .warning (f"Session {uid } invalid. Deleting...")
        data_manager .delete_session (phone )
    except (binascii .Error ,ValueError ,struct .error )as e :

        logger .warning (f"Corrupted session_string for {uid } ({phone }): {e }. Deleting invalid session.")
        try :
            data_manager .mark_invalid_session (uid ,phone ,"CORRUPTED_SESSION_STRING")
        except Exception :
            pass 
        data_manager .delete_session (phone )
    except FloodWait as fw :
        _fw_wait =int (getattr (fw ,"value",30 )or 30 )
        logger .warning (f"Start FloodWait {_fw_wait }s for {uid }")
        if _retry_count >=3 :
            logger .warning (f"Start retry limit reached for {uid }. Giving up.")
            return 
        async def retry_later ():
            await asyncio .sleep (_fw_wait +5 )
            await start_bot_instance (session_string ,phone ,uid ,font ,_retry_count =_retry_count +1 )
        asyncio .create_task (retry_later ())
    except Exception as e :
        logger .exception (f"Could not start self instance for {uid }: {e }")
    finally :
        if not started_ok :
            
            try :
                await asyncio .wait_for (client .stop (),timeout =5.0 )
            except Exception :
                pass
            try :
                await asyncio .wait_for (client .disconnect (),timeout =3.0 )
            except Exception :
                pass
            try :
                dispatcher =getattr (client ,"dispatcher",None )
                if dispatcher is not None :
                    for w in list (getattr (dispatcher ,"handler_workers",[])or []):
                        try :w .cancel ()
                        except Exception :pass
                    q =getattr (dispatcher ,"updates_queue",None )
                    if q is not None :
                        while not q .empty ():
                            try :q .get_nowait ()
                            except Exception :break
            except Exception :
                pass
            try :
                conn =getattr (getattr (client ,"storage",None ),"conn",None )
                if conn is not None :
                    try :conn .close ()
                    except Exception :pass
            except Exception :
                pass
            del client

_PANEL_FLAGS =("CLOCK_STATUS","BIO_CLOCK_STATUS","BIO_DATE_STATUS","AVATAR_STATUS","BOLD_MODE_STATUS",
"SPOILER_MODE_STATUS","CODE_MODE_STATUS","UNDERLINE_MODE_STATUS","GRADUAL_MODE_STATUS","DOT_COMMANDS_STATUS",
"PEMOJI_STATUS","TAG_ALERT_STATUS","FILTER_WORDS_ACTIVE","ANTI_DELETE_STATUS","ANTI_EDIT_STATUS",
"SECRETARY_MODE_STATUS","SELF_DESTRUCT_STATUS","FIRST_COMMENT_STATUS","AUTO_SEEN_STATUS","FORCED_JOIN_ACTIVE",
"AUTO_SAVE_VIEW_ONCE","TABCHI_PV_STATUS","TABCHI_GP_STATUS","TABCHI_SMART_STATUS","PV_LOCK_STATUS",
"ANTI_LOGIN_STATUS","TYPING_MODE_STATUS","PLAYING_MODE_STATUS","RECORD_VOICE_STATUS","UPLOAD_PHOTO_STATUS",
"WATCH_GIF_STATUS","COPY_MODE_STATUS")

def _panel_stats (uid ):
    g =globals ()
    on =0
    total =0
    for n in _PANEL_FLAGS :
        d =g .get (n )
        if not isinstance (d ,dict ):
            continue
        total +=1
        if d .get (uid ,False ):
            on +=1
    return on ,max (0 ,total -on )

def _panel_caption (uid ):
    st ="◉ آنلاین"if uid in ACTIVE_BOTS else "○ آفلاین"
    try :
        if not data_manager .data .get ("global_bot_status",True ):
            st ="✕ خاموش سراسری"
    except Exception :
        pass
    on ,off =_panel_stats (uid )
    return (
    "✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  CONTROL\n"
    "━━━━━━━━━━━━━━━━━━\n"
    f"◈ کاربر    `{uid }`\n"
    f"◈ وضعیت    {st }\n"
    f"◈ ماژول    `{on }` روشن  ·  `{off }` خاموش\n"
    f"◈ بخش      {_panel_tab_label (uid )}\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "✧ تب بالا را عوض کن تا بخش دیگری باز شود"
    )

PANEL_TAB = {}
PANEL_COLOR_STATUS = {}
HELP_COLOR_STATUS = {}
PANEL_TABS = [("prof", "❖", "پروفایل"), ("text", "✎", "متن"), ("smart", "⟡", "هوشمند"),
              ("shield", "☒", "سپر"), ("pres", "◉", "حضور"), ("tab", "◈", "تبچی"),
              ("target", "♜", "تارگت"), ("lang", "✧", "ترجمه")]
PANEL_EN = {"prof": "P R O F I L E", "text": "T E X T   E N G I N E", "smart": "S M A R T   S Y S T E M",
            "shield": "P R I V A T E   S H I E L D", "pres": "P R E S E N C E", "tab": "T A B C H I",
            "target": "T A R G E T", "lang": "T R A N S L A T O R"}

def _panel_tab (uid ):
    t = PANEL_TAB.get(uid, "prof")
    return t if any(k == t for k, _s, _l in PANEL_TABS) else "prof"

def _panel_tab_label (uid ):
    cur = _panel_tab(uid)
    for k, sym, lab in PANEL_TABS:
        if k == cur:
            return f"{sym} {lab}"
    return "❖ پروفایل"

def build_elite_panel_rows (uid ):
    def c (val ):
        return "◉"if val else "○"

    preview =stylize_time ("12:34",USER_FONT_CHOICES .get (uid ,'stylized'))
    t_lang =AUTO_TRANSLATE_TARGET .get (uid )
    dt_type ="شمسی"if BIO_DATE_TYPE .get (uid ,"jalali")=="jalali"else "میلادی"

    cur =_panel_tab (uid )
    on ,off =_panel_stats (uid )
    rows =[[(f"◈  {on } روشن   ·   {off } خاموش  ◈","none")]]
    tabs =[]
    for k ,sym ,lab in PANEL_TABS :
        tabs .append ((f"▸ {lab } ◂"if k ==cur else f"{sym } {lab }",f"pt_{k }_{uid }"))
    for i in range (0 ,len (tabs ),3 ):
        rows .append (tabs [i :i +3 ])
    rows .append ([(PANEL_EN .get (cur ,"D A R K S E L F"),"none")])

    if cur =="prof":
        rows +=[
        [(f"☾ ساعت پروفایل {c (CLOCK_STATUS .get (uid ,False ))}",f"tg_clock_{uid }"),
        (f"✥ استایل نام: {preview }",f"cyc_font_{uid }")],
        [(f"☽ ساعت بیو {c (BIO_CLOCK_STATUS .get (uid ,False ))}",f"tg_bioclock_{uid }"),
        (f"✺ تاریخ بیو {c (BIO_DATE_STATUS .get (uid ,False ))}",f"tg_biodate_{uid }")],
        [(f"◈ تقویم: {dt_type }",f"tg_biodatetype_{uid }"),
        ("✦ استایل بیو ◂",f"cyc_biofont_{uid }")],
        [(f"◉ آواتار زنده {c (AVATAR_STATUS .get (uid ,False ))}",f"tg_avatar_{uid }")],
        [(f"◆ پنل رنگی {c (PANEL_COLOR_STATUS .get (uid ,True ))}",f"tg_pcolor_{uid }"),
        (f"◆ راهنما رنگی {c (HELP_COLOR_STATUS .get (uid ,True ))}",f"tg_hcolor_{uid }")],
        ]
    elif cur =="text":
        rows +=[
        [(f"✧ بولد {c (BOLD_MODE_STATUS .get (uid ,False ))}",f"tg_bold_{uid }"),
        (f"✧ اسپویلر {c (SPOILER_MODE_STATUS .get (uid ,False ))}",f"tg_spoil_{uid }")],
        [(f"✎ نقل و قول {c (CODE_MODE_STATUS .get (uid ,False ))}",f"tg_code_{uid }"),
        (f"▱ زیرخط {c (UNDERLINE_MODE_STATUS .get (uid ,False ))}",f"tg_under_{uid }")],
        [(f"⌁ تدریجی {c (GRADUAL_MODE_STATUS .get (uid ,False ))}",f"tg_gradual_{uid }"),
        (f"• نقطه‌ای {c (DOT_COMMANDS_STATUS .get (uid ,False ))}",f"tg_dotcmd_{uid }")],
        [(f"✦ ایموجی پرمیوم {c (PEMOJI_STATUS .get (uid ,False ))}",f"tg_pemoji_{uid }")],
        ]
    elif cur =="smart":
        rows +=[
        [(f"✦ هشدار تگ {c (TAG_ALERT_STATUS .get (uid ,False ))}",f"tg_tagalert_{uid }"),
        (f"✖ فیلتر کلمات {c (FILTER_WORDS_ACTIVE .get (uid ,False ))}",f"tg_wordfilter_{uid }")],
        [(f"☒ ضد دیلیت {c (ANTI_DELETE_STATUS .get (uid ,False ))}",f"tg_antidel_{uid }"),
        (f"✎ ضد ادیت {c (ANTI_EDIT_STATUS .get (uid ,False ))}",f"tg_antiedit_{uid }")],
        [(f"✉ منشی خودکار {c (SECRETARY_MODE_STATUS .get (uid ,False ))}",f"tg_sec_{uid }"),
        (f"⌫ پاک شونده {c (SELF_DESTRUCT_STATUS .get (uid ,False ))}",f"tg_selfdestruct_{uid }")],
        [(f"✎ کامنت اول {c (FIRST_COMMENT_STATUS .get (uid ,False ))}",f"tg_firstcomment_{uid }"),
        (f"◉ سین خودکار {c (AUTO_SEEN_STATUS .get (uid ,False ))}",f"tg_seen_{uid }")],
        [(f"☥ عضویت اجباری {c (FORCED_JOIN_ACTIVE .get (uid ,False ))}",f"tg_fjoin_{uid }"),
        (f"◈ ذخیره تایم‌دار {c (AUTO_SAVE_VIEW_ONCE .get (uid ,False ))}",f"tg_autosv_{uid }")],
        ]
    elif cur =="shield":
        rows +=[
        [(f"☒ قفل کامل پیوی {c (PV_LOCK_STATUS .get (uid ,False ))}",f"tg_pv_{uid }")],
        [(f"▧ عکس {c (PV_PHOTO_LOCK .get (uid ,False ))}",f"tg_pvph_{uid }"),
        (f"▣ ویدیو {c (PV_VIDEO_LOCK .get (uid ,False ))}",f"tg_pvvi_{uid }")],
        [(f"▰ گیف {c (PV_GIF_LOCK .get (uid ,False ))}",f"tg_pvgi_{uid }"),
        (f"♬ ویس {c (PV_VOICE_LOCK .get (uid ,False ))}",f"tg_pvvo_{uid }")],
        [(f"♫ آهنگ {c (PV_MUSIC_LOCK .get (uid ,False ))}",f"tg_pvmu_{uid }"),
        (f"▱ استیکر {c (PV_STICKER_LOCK .get (uid ,False ))}",f"tg_pvst_{uid }")],
        [(f"⌖ لوکیشن {c (PV_LOC_LOCK .get (uid ,False ))}",f"tg_pvloc_{uid }"),
        (f"✧ ایموجی {c (PV_EMO_LOCK .get (uid ,False ))}",f"tg_pvemo_{uid }")],
        [(f"✎ متن {c (PV_TXT_LOCK .get (uid ,False ))}",f"tg_pvtxt_{uid }")],
        ]
    elif cur =="pres":
        rows +=[
        [(f"⌨ تایپینگ {c (TYPING_MODE_STATUS .get (uid ,False ))}",f"tg_type_{uid }"),
        (f"♞ بازی {c (PLAYING_MODE_STATUS .get (uid ,False ))}",f"tg_game_{uid }")],
        [(f"▣ ارسال عکس {c (UPLOAD_PHOTO_STATUS .get (uid ,False ))}",f"tg_actph_{uid }"),
        (f"♬ ضبط ویس {c (RECORD_VOICE_STATUS .get (uid ,False ))}",f"tg_actvo_{uid }")],
        [(f"▰ تماشای گیف {c (WATCH_GIF_STATUS .get (uid ,False ))}",f"tg_actgi_{uid }")],
        ]
    elif cur =="tab":
        rows +=[
        [(f"◈ پیوی {c (TABCHI_PV_STATUS .get (uid ,False ))}",f"tg_tabpv_{uid }"),
        (f"◈ گروه {c (TABCHI_GP_STATUS .get (uid ,False ))}",f"tg_tabgp_{uid }")],
        [(f"⟡ هوشمند {c (TABCHI_SMART_STATUS .get (uid ,False ))}",f"tg_tabsmart_{uid }"),
        (f"⌁ سرعت: {TABCHI_SPEED .get (uid ,'medium')}",f"tg_tabspd_{uid }")],
        ]
    elif cur =="target":
        rows +=[
        [(f"✘ دشمن {c (ENEMY_ACTIVE .get (uid ,False ))}",f"tg_enm_{uid }"),
        (f"✚ دوست {c (FRIEND_ACTIVE .get (uid ,False ))}",f"tg_frnd_{uid }")],
        [(f"♡ کراش {c (CRASH_ACTIVE .get (uid ,False ))}",f"tg_crsh_{uid }")],
        ]
    else :
        rows +=[
        [(f"EN {c (t_lang =='en')}",f"lang_en_{uid }"),
        (f"RU {c (t_lang =='ru')}",f"lang_ru_{uid }")],
        [(f"CN {c (t_lang =='zh-CN')}",f"lang_cn_{uid }"),
        (f"خاموش {c (t_lang is None )}",f"lang_off_{uid }")],
        ]

    rows .append ([("✕ بستن",f"close_{uid }")])
    return rows

def generate_panel_markup (uid ):
    return InlineKeyboardMarkup ([
    [InlineKeyboardButton (text ,callback_data =callback_data )for text ,callback_data in row ]
    for row in build_elite_panel_rows (uid )
    ])

def _btn_style (text ,cb ):
    c =str (cb or "")
    if c =="none":
        return ""
    if c .startswith ("close")or c .startswith ("help_close"):
        return "danger"
    if c .startswith ("pt_"):
        return "success"if "▸"in str (text )else "primary"
    t =str (text ).rstrip ()
    if t .endswith ("◉"):
        return "success"
    return "primary"

def _json_btn (text ,cb ):
    b ={"text":text ,"callback_data":cb }
    st =_btn_style (text ,cb )
    if st :
        b ["style"]=st
    return b

def generate_panel_markup_json (uid ):
    if not PANEL_COLOR_STATUS .get (uid ,True ):
        return {"inline_keyboard":[
        [{"text":text ,"callback_data":callback_data }for text ,callback_data in row ]
        for row in build_elite_panel_rows (uid )
        ]}
    return {"inline_keyboard":[
    [_json_btn (text ,callback_data )for text ,callback_data in row ]
    for row in build_elite_panel_rows (uid )
    ]}

def generate_admins_markup ():
    admins =data_manager .get_admins ()
    text ="**لیست ادمین‌ها:**\n\n"
    buttons =[]
    for adm in admins :
        u_data =data_manager .data ["users"].get (str (adm ),{})
        fname =u_data .get ("first_name","ادمین")
        uname =f"@{u_data .get ('username')}"if u_data .get ("username")else "ندارد"

        text +=f"**نام:** {fname }\n"
        text +=f"**آیدی:** `{adm }`\n"
        text +=f"**یوزرنیم:** {uname }\n"
        text +=f"─────────────\n"

        buttons .append ([InlineKeyboardButton (f"حذف  ·  {fname [:10 ]}",callback_data =f"del_admin_{adm }")])

    buttons .append ([InlineKeyboardButton ("افزودن ادمین",callback_data ="add_admin_prompt")])
    buttons .append ([InlineKeyboardButton ("✕ بستن",callback_data ="close_admin")])
    return text ,InlineKeyboardMarkup (buttons )

def generate_users_markup (page =0 ):
    active_users =[]
    for uid_str ,udata in list (data_manager .get_all_users ().items ()):
        try :
            uid =int (uid_str )
            if uid in ACTIVE_BOTS :
                client =ACTIVE_BOTS [uid ][0 ]
                if client and hasattr (client ,"me")and client .me :
                    me =client .me 
                    fname =me .first_name or ""
                    lname =f" {me .last_name }"if me .last_name else ""
                    full_name =f"{fname }{lname }".strip ()or "ناشناس"
                    uname =me .username or ""
                    phone =me .phone_number or udata .get ("phone","")

                    udata ["first_name"]=full_name 
                    udata ["username"]=uname 
                    if phone :udata ["phone"]=phone 
                active_users .append (udata )
        except Exception :
            pass 

    total =len (active_users )
    pages =(total +4 )//5 
    if pages ==0 :pages =1 
    if page >=pages :page =pages -1 
    if page <0 :page =0 

    start =page *5 
    end =start +5 
    current_users =active_users [start :end ]

    text =f"**کاربران فعال (صفحه {page +1 } از {pages }):**\nتعداد سلف‌های روشن: {total }\n\n"
    buttons =[]

    for u in current_users :
        uid =u .get ("user_id","نامشخص")
        phone =u .get ("phone","نامشخص")
        fname =u .get ("first_name","ناشناس")
        uname =f"@{u .get ('username')}"if u .get ("username")else "ندارد"

        text +=f"**نام:** {fname }\n"
        text +=f"**شماره:** `{phone }`\n"
        text +=f"**آیدی:** `{uid }`\n"
        text +=f"**یوزرنیم:** {uname }\n"
        text +=f"وضعیت: **متصل**\n"
        text +=f"─────────────\n"

        buttons .append ([InlineKeyboardButton (f"حذف و خاموش  ·  {fname [:12 ]}",callback_data =f"kick_user_{uid }")])

    nav =[]
    if page >0 :
        nav .append (InlineKeyboardButton ("↶ قبلی",callback_data =f"users_page_{page -1 }"))
    nav .append (InlineKeyboardButton (f"{page +1 }/{pages }",callback_data ="none"))
    if page <pages -1 :
        nav .append (InlineKeyboardButton ("بعدی ↷",callback_data =f"users_page_{page +1 }"))

    if nav :buttons .append (nav )
    buttons .append ([InlineKeyboardButton ("✕ بستن",callback_data ="close_admin")])
    return text ,InlineKeyboardMarkup (buttons )

def generate_global_fjoin_markup ():
    is_active =data_manager .data .get ("global_fjoin_active",False )
    chats =data_manager .data .get ("global_fjoin_chats",[])

    text ="**عضویت اجباری سراسری:**\n\n"
    text +=f"وضعیت: **{'روشن'if is_active else 'خاموش'}**\n"
    text +="تعداد کانال‌ها: **{}**\n\n".format (len (chats ))
    text +="وقتی روشنه، هر کاربر قبل از استفاده از ربات باید عضو کانال‌ها بشه."

    buttons =[]
    if is_active :
        buttons .append ([InlineKeyboardButton ("خاموش کردن",callback_data ="gfjoin_toggle")])
    else :
        buttons .append ([InlineKeyboardButton ("روشن کردن",callback_data ="gfjoin_toggle")])

    buttons .append ([InlineKeyboardButton ("افزودن کانال/گروه",callback_data ="gfjoin_add")])
    buttons .append ([InlineKeyboardButton ("لیست و حذف",callback_data ="gfjoin_list")])
    buttons .append ([InlineKeyboardButton ("✕ بستن",callback_data ="close_admin")])

    return text ,InlineKeyboardMarkup (buttons )

def generate_global_bot_status_markup ():
    is_active =data_manager .data .get ("global_bot_status",True )

    text ="**کنترل سراسری سلف‌ها:**\n\n"
    text +="تمام سلف‌های کاربران رو با یک کلیک روشن یا خاموش کن.\n\n"
    text +=f"وضعیت سرور: **{'روشن — سلف‌ها فعالن'if is_active else 'خاموش — همه سلف‌ها متوقف شدن'}**"

    buttons =[]
    if is_active :
        buttons .append ([InlineKeyboardButton ("خاموش کردن همه",callback_data ="gbot_status_toggle")])
    else :
        buttons .append ([InlineKeyboardButton ("روشن کردن همه",callback_data ="gbot_status_toggle")])

    buttons .append ([InlineKeyboardButton ("✕ بستن",callback_data ="close_admin")])

    return text ,InlineKeyboardMarkup (buttons )

async def _ui_edit_caption (client ,inline_id ,text ,markup_json ,markup ):
    res =await bot_api_request ("editMessageText",{
    "inline_message_id":inline_id ,"text":text ,"parse_mode":"Markdown",
    "reply_markup":markup_json },timeout =4.0 )
    if res .get ("ok"):
        return True
    if int ((res .get ("parameters")or {}).get ("retry_after",0 ))>0 :
        return False
    try :
        await client .edit_inline_text (inline_id ,text ,reply_markup =markup )
        return True
    except Exception :
        return False

HELP_HOME_TEXT ="""
**𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙**  ·  مرکز راهنما
──────────────────

یک دسته را از منوی زیر انتخاب کنید.
""".strip ()

HELP_SECTIONS ={
"main":{
"title":"دستورات اصلی",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  CORE
━━━━━━━━━━━━━━━━━━

`پنل`  —  باز کردن پنل کنترل
`راهنما`  —  نمایش مرکز راهنما
`ping`  —  تست سرعت پاسخ
`ساعت`  —  ساعت تهران و تاریخ کامل
`تاریخ`  —  شمسی · میلادی · قمری
`سلف خاموش`  —  غیرفعال‌سازی سلف
`سلف روشن`  —  فعال‌سازی مجدد
""".strip ()
},
"wallet":{
"title":"کیف پول",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  WALLET
━━━━━━━━━━━━━━━━━━

`تنظیم ولت تتر [آدرس]`
`تنظیم ولت گرام [آدرس]`
`تنظیم ولت ترون [آدرس]`

`ولت تتر`  ·  `ولت گرام`  ·  `ولت ترون`
`لیست ولت`  —  نمایش همه

`حذف ولت تتر`  ·  `گرام`  ·  `ترون`
`حذف لیست ولت`  —  پاکسازی کامل
""".strip ()
},
"backup":{
"title":"پشتیبان‌گیری",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  BACKUP
━━━━━━━━━━━━━━━━━━

`بکاپ`  —  فایل HTML از ۲۰۰۰ پیام آخر
`بکاپ کل`  —  ۱۰ چت خصوصی اخیر

نمایش شبیه چت · نام و ساعت
متن، عکس، ویدیو، گیف، ویس، فایل، استیکر، لوکیشن
""".strip ()
},
"datetime":{
"title":"تاریخ و ساعت",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  DATE / TIME
━━━━━━━━━━━━━━━━━━

`ساعت`  —  ساعت تهران و روز هفته
`تاریخ`  —  شمسی · میلادی · قمری
""".strip ()
},
"panel":{
"title":"پنل کنترل",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  PANEL
━━━━━━━━━━━━━━━━━━

`پنل`  —  مرکز کنترل دکمه‌ای

**پروفایل**  ساعت، استایل نام، بیو، تقویم
**متن**  بولد، اسپویلر، نقل‌قول، زیرخط، تدریجی
**فیلتر**  فیلتر کلمات ورودی پیوی
**سیستم**  منشی، سین خودکار، ذخیره، هشدار تگ
**لیست‌ها**  پاسخ دشمن، دوست، کراش
**قفل**  قفل کامل و جداگانه هر مدیا
**ترجمه**  ترجمه خودکار خروجی
""".strip ()
},
"group":{
"title":"مدیریت گروه",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  GROUP
━━━━━━━━━━━━━━━━━━

`تگ`  —  تگ اعضای دارای یوزرنیم
`تگ ادمین ها`  —  تگ مدیران گروه
`حذف [عدد]`  —  حذف پیام‌های اخیر
`حذف همه`  —  حذف انبوه
`اسپم [متن] [تعداد]`  —  ارسال تکراری
`فلود [متن] [تعداد]`  —  چندخطی تکراری
`آیدی`  —  مشخصات کاربر
`سشن`  —  سشن به Saved
""".strip ()
},
"reply":{
"title":"ابزار ریپلای",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  REPLY
━━━━━━━━━━━━━━━━━━

`دانلود`  —  دانلود مدیا به ذخیره‌شده‌ها
`ذخیره`  —  ذخیره متن یا مدیا
`استیکر`  —  ساخت استیکر
`تکرار [عدد]`  —  کپی پیام (حداکثر ۲۰)
`بن`  —  بن کاربر در گروه
`پین`  ·  `آن پین`
`بلاک`  ·  `حذف بلاک`
`تنظیم سکوت`  ·  `حذف سکوت`
""".strip ()
},
"react":{
"title":"ری‌اکشن",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  REACTION
━━━━━━━━━━━━━━━━━━

`ریاکت [ایموجی]`  —  ثبت ری‌اکشن خودکار
`حذف ریاکت`  —  حذف ری‌اکشن کاربر
`لیست ریاکت`  —  نمایش لیست
`ریاکت پاکسازی`  —  پاکسازی کامل
""".strip ()
},
"profile":{
"title":"پروفایل",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  PROFILE
━━━━━━━━━━━━━━━━━━

`تنظیم نام اکانت [نام]`
`تنظیم نام خانوادگی [نام]`
`تنظیم عکس`  —  با ریپلای

`حذف عکس پروفایل`  —  آخرین عکس
`حذف تمام عکس پروفایل`  —  همه

`کپی روشن`  —  کپی پروفایل ریپلای‌شده
`کپی خاموش`  —  بازگردانی
""".strip ()
},
"create":{
"title":"ساخت و حذف",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  CREATE
━━━━━━━━━━━━━━━━━━

`ساخت گروه [اسم]`
`ساخت کانال [اسم]`
`حذف گروه [اسم]`  —  مالک بودن الزامی
`حذف کانال [اسم]`  —  مالک بودن الزامی

**پاکسازی عضویت‌ها**
`حذف تمام گروه ها`  —  خروج از همهٔ گروه‌های غیرملکی
`حذف تمام کانال ها`  —  خروج از همهٔ کانال‌های غیرملکی
`حذف همه ربات ها`  —  مسدودکردن ربات‌ها و حذف گفت‌وگوی آن‌ها
`توقف پاکسازی`  —  توقف عملیات جاری

""".strip ()
},
"lists":{
"title":"لیست‌ها",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  LISTS
━━━━━━━━━━━━━━━━━━

**افزودن/حذف تارگت** (با ریپلای روی پیام کاربر)
`تنظیم دشمن`  ·  `حذف دشمن`
`تنظیم دوست`  ·  `حذف دوست`
`تنظیم کراش`  ·  `حذف کراش`

**نمایش و پاکسازی افراد ثبت‌شده**
`لیست افراد دشمن`  ·  `لیست افراد دوست`  ·  `لیست افراد کراش`
`پاکسازی لیست دشمن`
`پاکسازی لیست دوست`
`پاکسازی لیست کراش`

**متن‌های پاسخ خودکار** (دشمن/دوست/کراش)
`لیست دشمن`  ·  `لیست دوست`  ·  `لیست کراش`  —  نمایش متن‌ها
`تنظیم متن دشمن [متن]`  ·  `تنظیم متن دوست [متن]`  ·  `تنظیم متن کراش [متن]`
`لیست متن دشمن`  ·  `لیست متن دوست`  ·  `لیست متن کراش`
`حذف متن دشمن [شماره]`  ·  `حذف متن دوست [شماره]`  ·  `حذف متن کراش [شماره]`

**فیلتر کلمات**
`تنظیم فیلتر کلمات [متن]`
`لیست فیلتر کلمات`
`حذف فیلتر کلمات [عدد]`
`حذف لیست فیلتر کلمات`

""".strip ()
},
"wordfilter":{
"title":"فیلتر کلمات",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  WORD FILTER
━━━━━━━━━━━━━━━━━━

`تنظیم فیلتر کلمات [متن]`
`لیست فیلتر کلمات`
`حذف فیلتر کلمات [عدد]`
`حذف لیست فیلتر کلمات`

""".strip ()
},
"secretary":{
"title":"منشی خودکار",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  SECRETARY
━━━━━━━━━━━━━━━━━━

`تنظیم منشی [متن]`  —  پاسخ خودکار ثابت

""".strip ()
},
"fjoin":{
"title":"عضویت اجباری",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  FORCED JOIN
━━━━━━━━━━━━━━━━━━

`تنظیم عضویت اجباری @username`
`حذف عضویت اجباری @username`
`لیست عضویت اجباری`
""".strip ()
},
"privatechan":{
"title":"سیو کانال خصوصی",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  PRIVATE CHANNEL SAVE
━━━━━━━━━━━━━━━━━━

`سیو کانال خصوصی`

""".strip ()
},
"media":{
"title":"رسانه و جستجو",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  MEDIA
━━━━━━━━━━━━━━━━━━

`عکس [متن]`  —  جستجو و ارسال تصویر
`سرچ [موضوع]`  —  جستجو و خلاصه متنی
`ترجمه`  —  ترجمه پیام ریپلای‌شده
`استیکر`  —  ساخت استیکر
`گیف`  —  تبدیل ویدیو به گیف
""".strip ()
},
"cheat":{
"title":"بازی و سرگرمی",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  GAME
━━━━━━━━━━━━━━━━━━

`تاس [1-6]`  —  تاس تا رسیدن به عدد
`دارت`
`فوتبال`
`بولینگ`
`بسکتبال`

""".strip ()
},
"fun":{
"title":"فان و افکت",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  FUN
━━━━━━━━━━━━━━━━━━

`قلب`  —  لودینگ قلبی ۰ تا ۱۰۰
`ماتریکس`  —  افکت بارش کد
`لاو`  —  قلب‌های رنگی متوالی
""".strip ()
},
"security":{
"title":"امنیت پیوی",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  SECURITY
━━━━━━━━━━━━━━━━━━

**ضد دیلیت**  ذخیرهٔ پیام حذف‌شده
**ضد ادیت**  ثبت نسخهٔ قبلی پیام

فقط در پیوی فعال است. از پنل روشن می‌شود.
""".strip ()
},
"crypto":{
"title":"رمزنگاری",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  CRYPTO
━━━━━━━━━━━━━━━━━━

`رمز [متن]`  —  رمزنگاری متن
`رمز`  —  رمزنگاری پیام ریپلای‌شده
`رمزگشایی`  —  ریپلای روی متن رمزشده

""".strip ()
},
"timed":{
"title":"ابزار زمان‌دار",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  TIMED
━━━━━━━━━━━━━━━━━━

`پاک شونده [زمان]`  —  حذف پیام پس از زمان
`ارسال [زمان] بعد [متن]`  —  ارسال زمان‌دار
`سکوت [زمان]`  —  سکوت موقت (ریپلای)
`اکشن`  —  پنل اکشن سریع (ریپلای)

نمونه زمان:  `10 دقیقه`  ·  `2 ساعت`
""".strip ()
},
"firstcomment":{
"title":"کامنت اول",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  FIRST COMMENT
━━━━━━━━━━━━━━━━━━

`تنظیم متن کامنت اول [متن]`
`کامنت`  —  فعال‌سازی در گروه دیسکاشن
`لیست کامنت اول`
`حذف لیست کامنت اول`

""".strip ()
},
"nsfw":{
"title":"+۱۸",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  NSFW
━━━━━━━━━━━━━━━━━━

`boob`  ·  `butt`  —  تصویر
`lewd`  —  گیف
`hentai`  —  تصویر انیمه
""".strip ()
},
"cleanexit":{
"title":"پاکسازی و خروج",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  CLEAN EXIT
━━━━━━━━━━━━━━━━━━

`ترک`  —  در گروه: حذف پیام‌های خودت و خروج؛ در پیوی: پاکسازی دوطرفه
`ترک گروه`  —  حذف پیام‌های خودت در گروه و خروج
`ترک پیوی`  —  پاکسازی کامل پیوی به‌صورت دوطرفه
`حذف پیام های امروز`  —  حذف پیام‌های امروز خودت در چت فعلی
`حذف پیام های هفته`  —  حذف پیام‌های ۷ روز اخیر خودت در چت فعلی

""".strip ()
},
"tabchi":{
"title":"تبچی و تبلیغات",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  TABCHI
━━━━━━━━━━━━━━━━━━

`وضعیت تبچی`  —  نمایش وضعیت بنر، تایمر و ارسال‌ها
`تنظیم بنر [متن]`  —  تنظیم بنر متنی (یا ریپلای روی رسانه)
`حذف بنر`  —  پاک کردن بنر تبلیغاتی
`تنظیم تایمر [زمان]`  —  فاصله زمانی ارسال، از ۱۰ تا ۱۵۰۰ ثانیه (مثال: تنظیم تایمر 60)
`بنر پیوی کل`  —  ارسال همگانی پیام ریپلای‌شده به کل پیوی‌ها (یک‌بار)
`تکرار [زمان]`  —  تکرار پیام در همان چت، از ۵ تا ۱۰۰۰ ثانیه (با ریپلای، مثال: تکرار 10 ثانیه)
`تکرار خاموش`  —  توقف تکرار پیام در چت فعلی

""".strip ()
},

"pemoji":{
"title":"ایموجی پرمیوم",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  PREMIUM EMOJI
━━━━━━━━━━━━━━━━━━

`تنظیم ایموجی ❤️`  —  ریپلای روی ایموجی پرمیوم؛ تنظیم قبلی جایگزین می‌شه
`تنظیم ایموجی ❤️ لینک پک`  —  صفحه‌ی انتخاب؛ ریپلای عدد روی همون پیام
`لیست ایموجی`  —  نمایش لیست با ایموجی پرمیوم (via @bot)
`حذف ایموجی 1`  —  حذف با شماره یا خود ایموجی
`حذف لیست ایموجی پرمیوم`  —  پاکسازی کامل
کلید پنل «ایموجی پرمیوم»  —  روشن: ارسال خودکار پرمیوم؛ خاموش: عادی
""".strip ()
},
"logo":{
"title":"لوگو",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  LOGO STUDIO
━━━━━━━━━━━━━━━━━━

`لوگو amir 10`  —  ساخت لوگو با طرح شماره 10
`لوگو amir`  —  طرح تصادفی
طرح‌ها 1 تا 50  —  دارک، وایت، نئون، کروم، امضا
متن فارسی و انگلیسی  —  چند کلمه هم قبوله
""".strip ()
},
"rate":{
"title":"نرخ ارز",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  LIVE RATE
━━━━━━━━━━━━━━━━━━

`نرخ`  —  تابلو زنده دلار، یورو، طلا، سکه، تتر
`دلار`  —  قیمت لحظه‌ای یک دلار به تومان
`دلار 1.6`  —  قیمت 1.6 دلار
`طلا 1.5`  —  قیمت 1.5 گرم طلای 18 عیار
سکه، نیم، ربع، مثقال، انس، نقره، طلا 24
یورو، پوند، درهم، لیر، تتر، بیتکوین، اتریوم، ترون
""".strip ()
},
"ai":{
"title":"هوش مصنوعی",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  AI CHAT
━━━━━━━━━━━━━━━━━━

`هوش پایتخت ژاپن کجاست`  —  پرسیدن سوال
`هوش` روی پیام ریپلای  —  جواب درباره همان متن
`هوش خلاصه کن` + ریپلای  —  خلاصه، ترجمه، بازنویسی
`هوش پاک`  —  پاک کردن حافظه گفتگو

گفتگو ادامه‌دار است و چهار پیام آخر را به یاد دارد
بدون محدودیت و بدون نیاز به اشتراک
""".strip ()
},
"music":{
"title":"آهنگ",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  MUSIC FINDER
━━━━━━━━━━━━━━━━━━

`آهنگ گوزن سورنا`  —  پیدا کردن و فرستادن فایل آهنگ
`آهنگ Blinding Lights`  —  فارسی و خارجی
روی پیام ریپلای کنی، آهنگ هم ریپلای می‌شود
""".strip ()
},
"avatar":{
"title":"آواتار",
"text":"""
✦ **𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙** ✦  ·  LIVE AVATAR
━━━━━━━━━━━━━━━━━━

`آواتار`  —  پیش‌نمایش بدون تغییر پروفایل
`آواتار طرح 3`  —  انتخاب طرح 1 تا 8
`آواتار متن amir`  —  متن زیر ساعت
روشن و خاموش کردن از پنل  —  «آواتار زنده»
وقتی روشنه هر 10 دقیقه ساعت پروفایل آپدیت می‌شود
""".strip ()
},
}

HELP_BUTTON_GROUPS =[
("✦","دستورات پایه",[
("اصلی","main"),("پنل کنترل","panel"),("تاریخ و ساعت","datetime"),
]),
("♜","مدیریت گروه",[
("گروه","group"),("ریپلای","reply"),("ری‌اکشن","react"),("پاکسازی خروج","cleanexit"),
]),
("☒","امنیت و حریم خصوصی",[
("امنیت پیوی","security"),("رمزنگاری","crypto"),("فیلتر کلمات","wordfilter"),
]),
("❖","شخصی‌سازی",[
("پروفایل","profile"),("ساخت / حذف","create"),("لیست‌ها","lists"),
]),
("⟡","خودکارسازی",[
("منشی","secretary"),("زمان‌دار","timed"),("کامنت اول","firstcomment"),("تبچی","tabchi"),
]),
("◈","متفرقه",[
("رسانه","media"),("سیو کانال","privatechan"),("کیف پول","wallet"),("بکاپ","backup"),("ایموجی پرمیوم","pemoji"),("لوگو","logo"),("آواتار","avatar"),("آهنگ","music"),("نرخ ارز","rate"),("هوش مصنوعی","ai"),
]),
("♆","سرگرمی",[
("بازی","cheat"),("فان","fun"),("عضویت اجباری","fjoin"),
]),
("✧","محتوای بزرگسال",[
("+۱۸","nsfw"),
]),
]

def _help_home_rows ():
    rows =[]
    pairs =[(f"{sym }  {title }",f"grp{gi }")for gi ,(sym ,title ,_it )in enumerate (HELP_BUTTON_GROUPS )]
    for i in range (0 ,len (pairs ),2 ):
        rows .append (pairs [i :i +2 ])
    return rows

def _help_group_of (key ):
    for gi ,(_s ,_t ,items )in enumerate (HELP_BUTTON_GROUPS ):
        for _lb ,ky in items :
            if ky ==key :
                return gi
    return -1

def _help_group_rows (gi ):
    try :
        sym ,title ,items =HELP_BUTTON_GROUPS [gi ]
    except Exception :
        return []
    rows =[]
    for i in range (0 ,len (items ),2 ):
        rows .append (items [i :i +2 ])
    return rows

def get_help_group_text (gi ):
    try :
        sym ,title ,items =HELP_BUTTON_GROUPS [gi ]
    except Exception :
        return HELP_HOME_TEXT
    names =" · ".join (lb for lb ,_k in items )
    return (f"**𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙**  ·  {title }\n"
    "──────────────────\n\n"
    f"{sym } {len (items )} بخش\n"
    f"{names }\n\n"
    "یکی را انتخاب کنید.")

def generate_help_group_markup (uid ,gi ):
    rows =[[InlineKeyboardButton (lb ,callback_data =f"help_{ky }_{uid }")for lb ,ky in row ]
    for row in _help_group_rows (gi )]
    rows .append ([InlineKeyboardButton ("بازگشت",callback_data =f"help_home_{uid }"),
    InlineKeyboardButton ("بستن",callback_data =f"help_close_{uid }")])
    return InlineKeyboardMarkup (rows )

def generate_help_group_markup_json (uid ,gi ):
    rows =[]
    n =0
    for row in _help_group_rows (gi ):
        out =[]
        for lb ,ky in row :
            _b ={"text":lb ,"callback_data":f"help_{ky }_{uid }"}
            if HELP_COLOR_STATUS .get (uid ,True ):
                _b ["style"]="success"if n %2 ==0 else "primary"
            out .append (_b )
            n +=1
        rows .append (out )
    _st ="danger"if HELP_COLOR_STATUS .get (uid ,True )else None
    _r =[{"text":"◂ بازگشت","callback_data":f"help_home_{uid }"},
    {"text":"✕ بستن","callback_data":f"help_close_{uid }"}]
    if _st :
        for _b in _r :
            _b ["style"]=_st
    rows .append (_r )
    return {"inline_keyboard":rows }

def generate_help_home_markup (uid ):
    rows =[]
    for row in _help_home_rows ():
        rows .append ([
        InlineKeyboardButton (label ,callback_data =("help_none"if key =="none"else f"help_{key }_{uid }"))
        for label ,key in row 
        ])
    rows .append ([InlineKeyboardButton ("بستن",callback_data =f"help_close_{uid }")])
    return InlineKeyboardMarkup (rows )

def generate_help_home_markup_json (uid ):
    rows =[]
    n =0
    for row in _help_home_rows ():
        out =[]
        for label ,key in row :
            if key =="none":
                out .append ({"text":label ,"callback_data":"help_none"})
                continue
            _b ={"text":label ,"callback_data":f"help_{key }_{uid }"}
            if HELP_COLOR_STATUS .get (uid ,True ):
                _b ["style"]="success"if n %2 ==0 else "primary"
            out .append (_b )
            n +=1
        rows .append (out )
    _c ={"text":"✕ بستن","callback_data":f"help_close_{uid }"}
    if HELP_COLOR_STATUS .get (uid ,True ):
        _c ["style"]="danger"
    rows .append ([_c ])
    return {"inline_keyboard":rows }

def generate_help_section_markup (uid ,key =""):
    gi =_help_group_of (key )
    back =f"help_grp{gi }_{uid }"if gi >=0 else f"help_home_{uid }"
    return InlineKeyboardMarkup ([
    [InlineKeyboardButton ("بازگشت",callback_data =back ),
    InlineKeyboardButton ("بستن",callback_data =f"help_close_{uid }")]
    ])

def generate_help_section_markup_json (uid ,key =""):
    gi =_help_group_of (key )
    back =f"help_grp{gi }_{uid }"if gi >=0 else f"help_home_{uid }"
    _r =[{"text":"◂ بازگشت","callback_data":back },
    {"text":"✕ بستن","callback_data":f"help_close_{uid }"}]
    if HELP_COLOR_STATUS .get (uid ,True ):
        for _b in _r :
            _b ["style"]="danger"
    return {"inline_keyboard":[_r ]}

def get_help_section_text (key ):
    section =HELP_SECTIONS .get (key )
    if not section :
        return HELP_HOME_TEXT 
    return section ["text"]

@manager_bot .on_message (filters .private &~filters .me ,group =-5 )
async def manager_global_fjoin_check (client ,message ):
    if not message .from_user or getattr (message .from_user ,"is_bot",False )or message .from_user .id ==777000 :return 
    uid =message .from_user .id 
    if uid in data_manager .get_admins ():return 

    is_active =data_manager .data .get ("global_fjoin_active",False )
    chats =data_manager .data .get ("global_fjoin_chats",[])
    if not is_active or not chats :return 

    not_joined =[]
    for chat in chats :
        try :
            member =await client .get_chat_member (chat ,uid )
            if member .status in [ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ]:
                not_joined .append (chat )
        except Exception :
            not_joined .append (chat )

    if not_joined :
        buttons =[]
        for idx ,chat in enumerate (chats ,1 ):
            chat_url =f"https://t.me/{chat .lstrip ('@')}"if isinstance (chat ,str )and chat .startswith ("@")else f"https://t.me/c/{str (chat ).replace ('-100','')}/1"
            buttons .append ([InlineKeyboardButton (f"عضویت در کانال/گروه {idx }",url =chat_url )])

        buttons .append ([InlineKeyboardButton ("عضو شدم",callback_data =f"chk_manager_join_{uid }")])

        await message .reply_text (
        "**برای استفاده از این ربات، ابتدا باید در کانال یا گروه زیر عضو شوید:**\n\n"
        "پس از عضویت، روی دکمه «عضو شدم» بزنید تا امکان استفاده از ربات براتون فعال بشه.",
        reply_markup =InlineKeyboardMarkup (buttons )
        )
        raise StopPropagation 

@manager_bot .on_inline_query ()
async def inline_panel_handler (client ,query ):
    uid =query .from_user .id 
    if _activation_wait_left (uid )>0 :
        return await query .answer ([],cache_time =0 ,is_personal =True )
    q_text =query .query .strip ()

    if q_text =="panel"or q_text .startswith ("panel_"):
        target_uid =uid 
        if q_text .startswith ("panel_"):
            try :
                requested_uid =int (q_text .split ("_",1 )[1 ])
            except Exception :
                requested_uid =uid 
            if uid ==ROOT_ADMIN :
                target_uid =requested_uid 

        if _activation_wait_left (target_uid )>0 :
            return await query .answer ([],cache_time =0 ,is_personal =True )
        bot_status_str ="ONLINE"if target_uid in ACTIVE_BOTS else "OFFLINE"
        if not data_manager .data .get ("global_bot_status",True ):
            bot_status_str ="GLOBAL OFF"

        panel_text =_panel_caption (target_uid )

        _res_item ={"type":"article","id":str (uuid .uuid4 ()),"title":"DARKSELF PANEL",
        "input_message_content":{"message_text":panel_text ,"parse_mode":"Markdown"},
        "reply_markup":generate_panel_markup_json (target_uid )}
        res =await bot_api_request ("answerInlineQuery",{
        "inline_query_id":query .id ,
        "cache_time":0 ,
        "is_personal":True ,
        "results":[_res_item ]
        },timeout =4.0 )
        if res .get ("ok"):
            return 

        result =InlineQueryResultArticle (
        id =str (uuid .uuid4 ()),
        title ="DARKSELF PANEL",
        input_message_content =InputTextMessageContent (panel_text ),
        reply_markup =generate_panel_markup (target_uid )
        )
        await query .answer ([result ],cache_time =0 )

    elif q_text =="help"or q_text .startswith ("help_"):
        target_uid =uid 
        if q_text .startswith ("help_"):
            try :
                requested_uid =int (q_text .split ("_",1 )[1 ])
            except Exception :
                requested_uid =uid 
            if uid ==ROOT_ADMIN :
                target_uid =requested_uid 

        _hitem ={"type":"article","id":str (uuid .uuid4 ()),"title":"DARKSELF COMMAND CENTER",
        "description":"Professional inline command guide",
        "input_message_content":{"message_text":HELP_HOME_TEXT ,"parse_mode":"Markdown"},
        "reply_markup":generate_help_home_markup_json (target_uid )}
        res =await bot_api_request ("answerInlineQuery",{
        "inline_query_id":query .id ,
        "cache_time":0 ,
        "is_personal":True ,
        "results":[_hitem ]
        },timeout =4.0 )
        if res .get ("ok"):
            return 

        result =InlineQueryResultArticle (
        id =str (uuid .uuid4 ()),
        title ="DARKSELF COMMAND CENTER",
        input_message_content =InputTextMessageContent (HELP_HOME_TEXT ),
        reply_markup =generate_help_home_markup (target_uid )
        )
        await query .answer ([result ],cache_time =0 ,is_personal =True )

    elif q_text =="privsave"or q_text .startswith ("privsave_"):
        target_uid =uid 
        if q_text .startswith ("privsave_"):
            try :
                requested_uid =int (q_text .split ("_",1 )[1 ])
            except Exception :
                requested_uid =uid 
            if uid ==requested_uid or uid ==ROOT_ADMIN :
                target_uid =requested_uid 
        channels =await _get_private_channel_dialogs (target_uid ,limit =30 )
        page_text =_private_channel_home_text (target_uid ,len (channels ))
        markup_json =_private_channel_home_markup_json (target_uid ,channels )
        res =await bot_api_request ("answerInlineQuery",{
        "inline_query_id":query .id ,
        "cache_time":0 ,
        "is_personal":True ,
        "results":[{
        "type":"article",
        "id":str (uuid .uuid4 ()),
        "title":"سیو کانال خصوصی",
        "description":"فقط کانال‌های خصوصی ضد فوروارد",
        "input_message_content":{"message_text":page_text },
        "reply_markup":markup_json 
        }]
        },timeout =5.0 )
        if res .get ("ok"):
            return 
        result =InlineQueryResultArticle (
        id =str (uuid .uuid4 ()),
        title ="سیو کانال خصوصی",
        input_message_content =InputTextMessageContent (page_text ),
        reply_markup =InlineKeyboardMarkup ([
        [InlineKeyboardButton (btn ["text"],callback_data =btn ["callback_data"])for btn in row ]
        for row in markup_json .get ("inline_keyboard",[])
        ])
        )
        return await query .answer ([result ],cache_time =0 ,is_personal =True )

    elif q_text =="pemolist"or q_text .startswith ("pemopick:")or _pemoji_query_match (uid ,q_text ):
        await pemoji_inline_answer (client ,query ,uid ,q_text )
        return

    elif q_text .startswith ("action_"):
        parts =q_text .split ("_",3 )
        if len (parts )>=4 :
            try :
                _ ,owner_uid_s ,chat_id_s ,target_id_s =parts 
                owner_uid =int (owner_uid_s )
                chat_id =int (chat_id_s )
                target_id =int (target_id_s )
                if uid !=owner_uid and uid !=ROOT_ADMIN :
                    return await query .answer ([],cache_time =0 ,is_personal =True )
                result =InlineQueryResultArticle (
                id =str (uuid .uuid4 ()),
                title ="DARKSELF ACTION PANEL",
                description ="Quick target actions",
                input_message_content =InputTextMessageContent (build_action_panel_text (owner_uid ,chat_id ,target_id )),
                reply_markup =build_action_panel_markup (owner_uid ,chat_id ,target_id )
                )
                return await query .answer ([result ],cache_time =0 ,is_personal =True )
            except Exception :
                return await query .answer ([],cache_time =0 ,is_personal =True )

    elif q_text .startswith ("fjoin_"):
        parts =q_text .split ("_")
        if len (parts )>=3 :
            self_bot_id =int (parts [1 ])
            sender_id =int (parts [2 ])

            chats =FORCED_JOIN_CHATS .get (self_bot_id ,[])

            buttons =[]
            for idx ,chat in enumerate (chats ,1 ):
                chat_url =f"https://t.me/{chat .lstrip ('@')}"if isinstance (chat ,str )and chat .startswith ("@")else f"https://t.me/c/{str (chat ).replace ('-100','')}/1"
                buttons .append ([InlineKeyboardButton (f"عضویت در کانال/گروه {idx }",url =chat_url )])

            buttons .append ([InlineKeyboardButton ("عضو شدم",callback_data =f"chkjoin_{self_bot_id }_{sender_id }")])

            result =InlineQueryResultArticle (
            id =str (uuid .uuid4 ()),
            title ="عضویت اجباری",
            input_message_content =InputTextMessageContent (
            "**برای ارسال پیام به این کاربر، ابتدا باید در کانال یا گروه زیر عضو شوید:**\n\n"
            "پس از عضویت، روی دکمه «عضو شدم» بزنید تا امکان ارسال پیام براتون فعال بشه."
            ),
            reply_markup =InlineKeyboardMarkup (buttons )
            )
            await query .answer ([result ],cache_time =0 )

@manager_bot .on_callback_query ()
async def callback_panel_handler (client ,callback ):
    if (callback .data or "").startswith ("mm:"):
        return await main_menu_callback (client ,callback )
    if (callback .data or "").startswith ("pemopg:"):
        return await pemoji_pick_callback (client ,callback )
    if (callback .data or "")=="pemnoop":
        try :
            return await callback .answer ()
        except Exception :
            return
    if (callback .data or "").startswith ("adminlogs_"):
        try :
            await callback .answer ()
            if not _admin_log_access (callback .from_user ,getattr (callback .message ,"chat",None )):
                return 
            if callback .data =="adminlogs_close":
                await callback .message .delete ()
                return 
            match =re .fullmatch (r"adminlogs_page_(\d{1,4})",callback .data )
            if match :
                await _show_admin_log_page (callback .message ,page =int (match .group (1 )),edit =True )
        except MessageNotModified :
            pass 
        except Exception as exc :
            logger .warning ("Admin log callback failed: %s",type (exc ).__name__ )
        return 
    data =callback .data .split ("_")
    if data [0 ]=="none":return await callback .answer ()
    if callback .data =="help_none":return await callback .answer ()

    if data [0 ]in ("privch","privcnt","privback","privclose"):
        try :
            owner_uid =int (data [1 ])
        except Exception :
            return await callback .answer ("داده نامعتبر.",show_alert =True )
        if callback .from_user .id !=owner_uid and callback .from_user .id !=ROOT_ADMIN :
            return await callback .answer ("دسترسی غیرمجاز.",show_alert =True )
        if data [0 ]=="privclose":
            await _edit_private_inline_page (callback ,"صفحه سیو کانال خصوصی بسته شد.",None )
            return await callback .answer ()
        if data [0 ]=="privback":
            channels =await _get_private_channel_dialogs (owner_uid ,limit =30 )
            await _edit_private_inline_page (callback ,_private_channel_home_text (owner_uid ,len (channels )),_private_channel_home_markup_json (owner_uid ,channels ))
            return await callback .answer ()
        if data [0 ]=="privch":
            try :
                chat_id =int (data [2 ])
            except Exception :
                return await callback .answer ("کانال نامعتبر.",show_alert =True )
            title =str (chat_id )
            try :
                cache =data_manager .get_user_data (owner_uid ).get ("private_channel_cache")or []
                for item in cache :
                    if int (item .get ("id"))==chat_id :
                        title =str (item .get ("title")or chat_id )
                        break 
            except Exception :
                pass 
            pair =ACTIVE_BOTS .get (owner_uid )
            if pair :
                try :
                    ch =await pair [0 ].get_chat (chat_id )
                    title =getattr (ch ,"title",None )or title 
                except Exception :
                    pass 
            await _edit_private_inline_page (callback ,_private_channel_count_text (owner_uid ,chat_id ,title ),_private_channel_count_markup_json (owner_uid ,chat_id ))
            return await callback .answer ()
        if data [0 ]=="privcnt":
            try :
                chat_id =int (data [2 ]);cnt =max (1 ,min (20 ,int (data [3 ])))
            except Exception :
                return await callback .answer ("تعداد نامعتبر.",show_alert =True )
            await callback .answer ("شروع ذخیره‌سازی...",show_alert =False )
            if owner_uid not in ACTIVE_BOTS :
                job_id =_queue_private_channel_save_job (owner_uid ,chat_id ,cnt )
                await _edit_private_inline_page (
                callback ,
                f"درخواست سیو کانال خصوصی ثبت شد.\n\nتعداد: {cnt }\nکد پیگیری: {job_id }\nنتیجه داخل Saved Messages ارسال می‌شود.",
                None 
                )
                return 
            await _edit_private_inline_page (callback ,f"در حال ذخیره {cnt } پست آخر کانال خصوصی در Saved Messages...",None )
            ok ,failed =await _copy_private_channel_posts_to_saved (owner_uid ,chat_id ,cnt )
            await _edit_private_inline_page (callback ,f"سیو کانال خصوصی تمام شد.\n\nموفق: {ok }\nناموفق: {failed }",None )
            return 

    if data [0 ]=="slflimit":
        if callback .from_user .id !=ROOT_ADMIN :
            return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        kind =data [1 ]if len (data )>1 else ""
        if kind =="off":
            data_manager .set_self_limit (0 )
            LOGIN_STATES .pop (callback .from_user .id ,None )
            try :
                await callback .message .edit_text (_self_limit_text (),reply_markup =_self_limit_markup ())
            except Exception :
                pass 
            return await callback .answer ("لیمیت برداشته شد. حالا نامحدوده.")
        if kind =="set":
            LOGIN_STATES [callback .from_user .id ]={"step":"awaiting_self_limit"}
            await callback .message .reply_text (
            "**تعداد دلخواه**\n\n"
            "عدد مورد نظرت رو بفرست؛ یعنی حداکثر چند نفر بتونن سلف فعال کنن.\n"
            "مثال: `100`\n\n"
            "برای لغو `لغو` را بفرست.",
            reply_markup =ReplyKeyboardMarkup ([[KeyboardButton ("لغو")]],resize_keyboard =True )
            )
            return await callback .answer ()
        return await callback .answer ()

    if data [0 ]=="act":
        try :
            action =data [1 ]
            owner_uid =int (data [2 ])
            chat_id =int (data [3 ])
            target_id =int (data [4 ])
        except Exception :
            return await callback .answer ("داده پنل نامعتبر است.",show_alert =True )
        if callback .from_user .id !=owner_uid and callback .from_user .id !=ROOT_ADMIN :
            return await callback .answer ("این پنل برای شما نیست.",show_alert =True )
        if action =="close":
            INLINE_IDLE_STATE .get ("action",{}).pop (owner_uid ,None )
            try :
                if callback .inline_message_id :
                    await bot_api_request ("editMessageText",{"inline_message_id":callback .inline_message_id ,"text":"<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>پنل اکشن بسته شد.</b>","parse_mode":"HTML"},timeout =5.0 )
                else :
                    await callback .message .delete ()
            except Exception :
                pass 
            return await callback .answer ()

        client_bot =ACTIVE_BOTS .get (owner_uid ,[None ])[0 ]
        changed =False 
        try :
            if action =="mute":
                s =MUTED_USERS .setdefault (owner_uid ,set ())
                key =(target_id ,chat_id )
                if key in s :
                    s .remove (key )
                    MUTED_UNTIL .get (owner_uid ,{}).pop (key ,None )
                    changed =True 
                    answer ="سکوت خاموش شد."
                else :
                    s .add (key )
                    changed =True 
                    answer ="سکوت روشن شد."
                timed =[[k [0 ],k [1 ],v ]for k ,v in MUTED_UNTIL .get (owner_uid ,{}).items ()if v >time .time ()]
                data_manager .update_user_data (owner_uid ,{"muted":[list (x )for x in s ],"timed_muted":timed })
                _commit_and_broadcast_shards ("action-mute")

            elif action =="block":
                b =BLOCKED_USERS .setdefault (owner_uid ,set ())
                if target_id in b :
                    if client_bot :
                        try :await client_bot .unblock_user (target_id )
                        except Exception :pass 
                    b .remove (target_id )
                    answer ="بلاک خاموش شد."
                else :
                    if client_bot :
                        try :await client_bot .block_user (target_id )
                        except Exception :pass 
                    b .add (target_id )
                    answer ="بلاک روشن شد."
                data_manager .update_user_data (owner_uid ,{"blocked_users":list (b )})
                _commit_and_broadcast_shards ("action-block")
                changed =True 

            elif action in ("enemy","friend","crash"):
                store_map ={"enemy":ENEMY_LIST ,"friend":FRIEND_LIST ,"crash":CRASH_LIST }
                data_key ={"enemy":"enemy_list","friend":"friend_list","crash":"crash_list"}[action ]
                active_key ={"enemy":"enemy_active","friend":"friend_active","crash":"crash_active"}[action ]
                title ={"enemy":"دشمن","friend":"دوست","crash":"کراش"}[action ]
                active_map ={"enemy":ENEMY_ACTIVE ,"friend":FRIEND_ACTIVE ,"crash":CRASH_ACTIVE }
                store =store_map [action ].setdefault (owner_uid ,set ())
                current_key ,current_title =get_target_category (owner_uid ,target_id )
                if target_id in store :
                    store .remove (target_id )
                    answer =f"{title } خاموش شد."
                else :
                    if current_key and current_key !=action :
                        return await callback .answer (f"شما یک تارگت را از قبل فعال کردید: {current_title }",show_alert =True )
                    store .add (target_id )
                    active_map [action ][owner_uid ]=True 
                    answer =f"{title } روشن شد."
                data_manager .update_user_data (owner_uid ,{data_key :list (store ),"settings":{active_key :active_map [action ].get (owner_uid ,False )}})
                _commit_and_broadcast_shards (f"action-{action }")
                changed =True 
            else :
                return await callback .answer ("عملیات نامعتبر است.",show_alert =True )

            if changed :
                markup_json =build_action_panel_markup_json (owner_uid ,chat_id ,target_id )
                markup =build_action_panel_markup (owner_uid ,chat_id ,target_id )
                try :
                    if callback .inline_message_id :
                        res =await bot_api_request ("editMessageReplyMarkup",{"inline_message_id":callback .inline_message_id ,"reply_markup":markup_json },timeout =2.0 )
                        if not res .get ("ok"):
                            await client .edit_inline_reply_markup (callback .inline_message_id ,reply_markup =markup )
                    else :
                        await callback .edit_message_reply_markup (reply_markup =markup )
                except Exception :
                    pass 
                asyncio .create_task (schedule_inline_auto_close (
                "action",owner_uid ,
                inline_message_id =callback .inline_message_id ,
                message =None if callback .inline_message_id else callback .message 
                ))
                return await callback .answer (answer )
        except Exception :
            return await callback .answer ("خطا در اجرای اکشن.",show_alert =True )

    if data [0 ]=="help":
        action =data [1 ]if len (data )>1 else "home"
        try :
            owner_uid =int (data [-1 ])
        except Exception :
            owner_uid =callback .from_user .id 

        if callback .from_user .id !=owner_uid and callback .from_user .id !=ROOT_ADMIN :
            return await callback .answer ("این راهنما مربوط به شما نیست.",show_alert =True )

        if action =="close":
            INLINE_IDLE_STATE .get ("help",{}).pop (owner_uid ,None )
            try :
                if callback .inline_message_id :
                    res =await bot_api_request ("editMessageText",{
                    "inline_message_id":callback .inline_message_id ,
                    "text":"<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>راهنما بسته شد.</b>",
                    "parse_mode":"HTML"
                    },timeout =5.0 )
                    if not res .get ("ok"):
                        try:
                            await client .edit_inline_text (callback .inline_message_id ,"<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>راهنما بسته شد.</b>",parse_mode ="html")
                        except Exception:
                            try:
                                await manager_bot.edit_inline_text(callback.inline_message_id, "<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>راهنما بسته شد.</b>", parse_mode="html")
                            except Exception:
                                pass
                else :
                    await callback .message .delete ()
            except Exception :
                pass 
            return await callback .answer ()

        if action =="home":
            text =HELP_HOME_TEXT 
            markup_json =generate_help_home_markup_json (owner_uid )
            markup =generate_help_home_markup (owner_uid )
        elif action .startswith ("grp"):
            try :
                _gi =int (action [3 :])
            except Exception :
                _gi =0
            text =get_help_group_text (_gi )
            markup_json =generate_help_group_markup_json (owner_uid ,_gi )
            markup =generate_help_group_markup (owner_uid ,_gi )
        else :
            text =get_help_section_text (action )
            markup_json =generate_help_section_markup_json (owner_uid ,action )
            markup =generate_help_section_markup (owner_uid ,action )

        try :
            if callback .inline_message_id :
                await _ui_edit_caption (client ,callback .inline_message_id ,text ,markup_json ,markup )
            else :
                try :
                    await callback .message .edit_caption (text ,reply_markup =markup )
                except Exception :
                    await callback .message .edit_text (text ,reply_markup =markup )
        except Exception :
            pass 
        asyncio .create_task (schedule_inline_auto_close (
        "help",owner_uid ,
        inline_message_id =callback .inline_message_id ,
        message =None if callback .inline_message_id else callback .message 
        ))
        return await callback .answer ()

    if data [0 ]=="srvcfg":
        if callback .from_user .id not in data_manager .get_admins ():
            return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        action =data [1 ]if len (data )>1 else ""

        def _base_status_text ():
            total_users =len (data_manager .get_all_users ())
            active =len (ACTIVE_BOTS )
            status_str ="روشن"if data_manager .data .get ("global_bot_status",True )else "خاموش"
            t =f"**وضعیت سرور:**\n\n"
            t +=f"وضعیت کل سلف‌ها: **{status_str }**\n"
            t +=f"کاربران ثبت‌شده: `{total_users }`\n"
            t +=f"سلف‌های فعال: `{active }`\n"
            t +=f"زمان سرور: `{datetime .now (TEHRAN_TIMEZONE ).strftime ('%Y-%m-%d %H:%M:%S')}`\n\n"
            t +=get_server_stats_text ()
            return t 

        if action =="close":
            try :await callback .message .delete ()
            except Exception :pass 
            return await callback .answer ()

        if action =="back":
            try :
                await callback .message .edit_text (_base_status_text (),reply_markup =build_server_status_markup ())
            except Exception :pass 
            return await callback .answer ()

        if action =="menu":
            try :
                await callback .message .edit_text (
                "**تنظیم سرور**\n\nکدوم منبع رو می‌خوای محدود کنی؟",
                reply_markup =build_server_config_menu_markup ()
                )
            except Exception :pass 
            return await callback .answer ()

        if action =="pick"and len (data )>2 and data [2 ]=="cpu":
            try :
                await callback .message .edit_text (
                f"**محدودیت CPU**\n\nچند هسته از {_SERVER_CPU_COUNT } هسته سرور در اختیار ربات باشه؟",
                reply_markup =build_server_cpu_options_markup ()
                )
            except Exception :pass 
            return await callback .answer ()

        if action =="pick"and len (data )>2 and data [2 ]=="ram":
            try :
                await callback .message .edit_text (
                "**محدودیت RAM**\n\nحداکثر چند گیگابایت رم در اختیار ربات باشه؟",
                reply_markup =build_server_ram_options_markup ()
                )
            except Exception :pass 
            return await callback .answer ()

        if action =="setcpu"and len (data )>2 :
            try :
                n =int (data [2 ])
            except Exception :
                return await callback .answer ("مقدار نامعتبر.",show_alert =True )
            data_manager .set_server_limit ("cpu",n )
            try :
                apply_server_limits ()
            except Exception as e :
                logger .warning (f"apply_server_limits error: {e }")

            try :
                _shard_signal_reload ()
            except Exception :
                pass 
            try :
                await callback .message .edit_text (
                f"**محدودیت CPU**\n\nچند هسته از {_SERVER_CPU_COUNT } هسته سرور در اختیار ربات باشه؟",
                reply_markup =build_server_cpu_options_markup ()
                )
            except Exception :pass 
            if n >=2 and not os .environ .get ("DARKSELF_NO_SHARD","0")=="1":
                return await callback .answer (
                f"⚡ شاردینگ فعال: {n } ورکر روی {n } هسته موازی. سشن‌ها در حال بازتوزیع هستند...",
                show_alert =True 
                )
            return await callback .answer (f"محدودیت CPU روی {n if n else 'آزاد'} تنظیم شد.",show_alert =True )

        if action =="setram"and len (data )>2 :
            try :
                n =int (data [2 ])
            except Exception :
                return await callback .answer ("مقدار نامعتبر.",show_alert =True )
            data_manager .set_server_limit ("ram_gb",n )
            try :
                apply_server_limits ()
            except Exception as e :
                logger .warning (f"apply_server_limits error: {e }")
            try :
                _shard_signal_reload ()
            except Exception :
                pass 
            try :
                await callback .message .edit_text (
                "**محدودیت RAM**\n\nحداکثر چند گیگابایت رم در اختیار ربات باشه؟",
                reply_markup =build_server_ram_options_markup ()
                )
            except Exception :pass 
            return await callback .answer (f"محدودیت RAM روی {(str (n )+' GB')if n else 'آزاد'} تنظیم شد.",show_alert =True )

        return await callback .answer ()

    if data [0 ]=="add"and data [1 ]=="admin":
        if callback .from_user .id !=ROOT_ADMIN :return await callback .answer ("دسترسی غیرمجاز.",show_alert =True )
        LOGIN_STATES [callback .from_user .id ]={"step":"awaiting_admin_id"}
        await callback .message .edit_text ("**آیدی عددی ادمین جدید رو وارد کن:**")
        return 

    if data [0 ]=="del"and data [1 ]=="admin":
        if callback .from_user .id !=ROOT_ADMIN :return await callback .answer ("دسترسی غیرمجاز.",show_alert =True )
        adm_id =int (data [2 ])
        if adm_id ==ROOT_ADMIN :return await callback .answer ("ادمین اصلی قابل حذف نیست.",show_alert =True )
        if data_manager .remove_admin (adm_id ):
            await callback .answer (f"ادمین {adm_id } حذف شد.",show_alert =True )
            try :
                text ,markup =generate_admins_markup ()
                await callback .message .edit_text (text ,reply_markup =markup )
            except Exception :pass 
        return 

    if data [0 ]=="users"and data [1 ]=="page":
        if callback .from_user .id not in data_manager .get_admins ():return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        try :
            text ,markup =generate_users_markup (int (data [2 ]))
            await callback .message .edit_text (text ,reply_markup =markup )
        except Exception :pass 
        return 

    if data [0 ]=="kick"and data [1 ]=="user":
        if callback .from_user .id not in data_manager .get_admins ():return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        target_uid =int (data [2 ])
        await stop_user_bot (target_uid )
        data_manager .delete_user_full (target_uid )
        limit ,used ,free =data_manager .self_limit_status ()
        if limit :
            await callback .answer (f"کاربر حذف شد. یک جا آزاد شد.\nپر شده: {used } از {limit }",show_alert =True )
        else :
            await callback .answer ("کاربر از سیستم حذف شد.",show_alert =True )
        try :
            text ,markup =generate_users_markup (0 )
            await callback .message .edit_text (text ,reply_markup =markup )
        except Exception :pass 
        return 

    if data [0 ]=="close"and len (data )==2 and data [1 ]=="admin":
        await callback .message .delete ()
        return 

    if data [0 ]=="wipe"and len (data )>=2 and data [1 ]=="db":
        if callback .from_user .id !=ROOT_ADMIN :
            return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        await callback .answer ("در حال حذف کامل دیتابیس...",show_alert =True )
        try :
            await callback .message .edit_text ("**در حال خاموش کردن تمام سلف‌ها و پاکسازی دیتابیس...**")
        except Exception :
            pass 

        stop_tasks =[]
        for uid ,(c ,ts )in list (ACTIVE_BOTS .items ()):
            for t in ts :
                try :t .cancel ()
                except Exception :pass 
            stop_tasks .append (c .stop ())
        if stop_tasks :
            try :
                await asyncio .wait_for (asyncio .gather (*stop_tasks ,return_exceptions =True ),timeout =8.0 )
            except Exception :
                pass 
        ACTIVE_BOTS .clear ()
        STARTING_BOTS .clear ()

        try :
            data_manager .wipe_all_data ()
        except Exception as e :
            try :
                await callback .message .edit_text (f"**حذف دیتابیس ناموفق بود.**\n`{str (e )[:150 ]}`")
            except Exception :
                pass 
            return 

        load_all_states ()
        gc .collect ()

        try :
            await callback .message .edit_text (
            "**دیتابیس کاملاً پاک شد.**\n\n"
            "همه کاربران، سشن‌ها و تنظیمات حذف شدند و تمام سلف‌ها خاموش شدند.\n"
            "حالا می‌تونی از دکمه «بازیابی دیتابیس» بکاپ سالم رو جایگزین کنی."
            )
        except Exception :
            pass 
        return 

    if data [0 ]=="gfjoin"and data [1 ]=="toggle":
        if callback .from_user .id !=ROOT_ADMIN :return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        is_act =data_manager .data .get ("global_fjoin_active",False )
        data_manager .data ["global_fjoin_active"]=not is_act 
        data_manager .save_data ()
        text ,markup =generate_global_fjoin_markup ()
        await callback .message .edit_text (text ,reply_markup =markup )
        return 

    if data [0 ]=="gfjoin"and data [1 ]=="add":
        if callback .from_user .id !=ROOT_ADMIN :return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        LOGIN_STATES [callback .from_user .id ]={"step":"awaiting_global_fjoin"}
        await callback .message .edit_text ("**آیدی کانال یا گروه رو با @ ارسال کن** (مثل `@test`):")
        return 

    if data [0 ]=="gfjoin"and data [1 ]=="list":
        if callback .from_user .id !=ROOT_ADMIN :return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        chats =data_manager .data .get ("global_fjoin_chats",[])
        if not chats :
            return await callback .answer ("لیست خالیه.",show_alert =True )
        buttons =[]
        for c in chats :
            buttons .append ([InlineKeyboardButton (f"حذف  ·  {c }",callback_data =f"gfjoin_del_{c }")])
        buttons .append ([InlineKeyboardButton ("↶ بازگشت",callback_data ="gfjoin_back")])
        await callback .message .edit_text ("**لیست کانال‌های عضویت اجباری سراسری:**",reply_markup =InlineKeyboardMarkup (buttons ))
        return 

    if data [0 ]=="gfjoin"and data [1 ]=="back":
        text ,markup =generate_global_fjoin_markup ()
        await callback .message .edit_text (text ,reply_markup =markup )
        return 

    if data [0 ]=="gfjoin"and data [1 ]=="del":
        if callback .from_user .id !=ROOT_ADMIN :return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        chat_to_del =callback .data .replace ("gfjoin_del_","")
        chats =data_manager .data .get ("global_fjoin_chats",[])
        if chat_to_del in chats :
            chats .remove (chat_to_del )
            data_manager .data ["global_fjoin_chats"]=chats 
            data_manager .save_data ()
            await callback .answer (f"{chat_to_del } حذف شد.",show_alert =True )
        text ,markup =generate_global_fjoin_markup ()
        await callback .message .edit_text (text ,reply_markup =markup )
        return 

    if data [0 ]=="gbot"and data [1 ]=="status"and data [2 ]=="toggle":
        if callback .from_user .id !=ROOT_ADMIN :return await callback .answer ("دسترسی غیرمجاز!",show_alert =True )
        is_act =data_manager .data .get ("global_bot_status",True )
        new_status =not is_act 
        data_manager .data ["global_bot_status"]=new_status 
        data_manager .save_data ()

        if not new_status :
            await callback .answer ("در حال خاموش کردن تمامی سلف‌ها...",show_alert =True )
            async def safe_stop (c ,ts ):
                for t in ts :
                    try :t .cancel ()
                    except Exception :pass 
                try :await c .stop ()
                except Exception :pass 
            stop_tasks =[safe_stop (c ,ts )for u ,(c ,ts )in list (ACTIVE_BOTS .items ())]
            if stop_tasks :await asyncio .gather (*stop_tasks ,return_exceptions =True )
            ACTIVE_BOTS .clear ()
            gc .collect ()
        else :
            await callback .answer ("در حال روشن کردن تمامی سلف‌ها...",show_alert =True )
            for phone ,s_data in list (data_manager .get_all_sessions ()):
                uid =s_data ["user_id"]
                asyncio .create_task (start_bot_instance (s_data ["string"],phone ,uid ,'stylized'))
                await asyncio .sleep (0.12 )

        text ,markup =generate_global_bot_status_markup ()
        await callback .message .edit_text (text ,reply_markup =markup )
        return 

    if data [0 ]=="chk"and data [1 ]=="manager"and data [2 ]=="join":
        sender_id =int (data [3 ])
        if callback .from_user .id !=sender_id :
            return await callback .answer ("این دکمه متعلق به شما نیست.",show_alert =True )

        chats =data_manager .data .get ("global_fjoin_chats",[])
        not_joined =[]
        for chat in chats :
            try :
                member =await manager_bot .get_chat_member (chat ,sender_id )
                if member .status in [ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ]:
                    not_joined .append (chat )
            except Exception :
                not_joined .append (chat )

        if not_joined :
            return await callback .answer ("هنوز عضو نشدی.",show_alert =True )
        else :
            try :await callback .message .delete ()
            except Exception :pass 
            return await callback .answer ("عضویت تایید شد! حالا می‌تونی استفاده کنی.",show_alert =True )

    if data [0 ]=="chkjoin":
        self_bot_id =int (data [1 ])
        sender_id =int (data [2 ])

        if callback .from_user .id !=sender_id :
            return await callback .answer ("این دکمه متعلق به شما نیست.",show_alert =True )

        chats =FORCED_JOIN_CHATS .get (self_bot_id ,[])
        not_joined =[]

        for chat in chats :
            try :
                member =await manager_bot .get_chat_member (chat ,sender_id )
                if member .status in [ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ]:
                    not_joined .append (chat )
            except Exception :
                client_bot =ACTIVE_BOTS .get (self_bot_id ,[None ])[0 ]
                if client_bot :
                    try :
                        member =await client_bot .get_chat_member (chat ,sender_id )
                        if member .status in [ChatMemberStatus .LEFT ,ChatMemberStatus .BANNED ]:
                            not_joined .append (chat )
                    except Exception :
                        not_joined .append (chat )
                else :
                    not_joined .append (chat )

        if not_joined :
            return await callback .answer ("هنوز عضو نشدی.",show_alert =True )
        else :
            _set_fjoin_cache (self_bot_id ,sender_id ,tuple (chats ),True )
            try :await callback .message .delete ()
            except Exception :
                try :await callback .edit_message_text ("**عضویت تایید شد.** حالا امکان چت داری.")
                except Exception :pass 
            return await callback .answer ("عضویت تایید شد! حالا می‌تونی به این کاربر پیام بدی.",show_alert =True )

    action ,target_user_id ="_".join (data [:-1 ]),int (data [-1 ])

    is_root_controller =callback .from_user .id ==ROOT_ADMIN 
    if callback .from_user .id !=target_user_id and not is_root_controller :
        return await callback .answer ("دسترسی غیرمجاز.",show_alert =True )

    wait_left =_activation_wait_left (target_user_id )
    if action !="close"and wait_left >0 :
        return await callback .answer (f"فعال‌سازی در انتظار است؛ {math .ceil (wait_left )} ثانیه باقی مانده.",show_alert =True )
    if action !="close"and not is_root_controller :
        if not await check_global_fjoin_for_user (target_user_id ,callback ):
            return 

    s_up ={}
    if action =="tg_clock":
        s_up ["clock"]=CLOCK_STATUS [target_user_id ]=not CLOCK_STATUS .get (target_user_id ,False )
        s_up ["clock_manual"]=True 
        client_bot =ACTIVE_BOTS .get (target_user_id ,[None ])[0 ]
        if s_up ["clock"]:
            if client_bot :asyncio .create_task (perform_clock_update_now (client_bot ,target_user_id ))
        else :
            if client_bot :
                try :
                    me =await client_bot .get_me ()
                    current_last =me .last_name or ""
                    clean =re .sub (r'(?:\s*'+CLOCK_CHARS_REGEX_CLASS +r'+)+$','',current_last ).strip ()
                    if clean !=current_last :await client_bot .update_profile (last_name =clean )
                except Exception :pass 

    elif action =="tg_pcolor":
        s_up ["panel_color"]=PANEL_COLOR_STATUS [target_user_id ]=not PANEL_COLOR_STATUS .get (target_user_id ,True )

    elif action =="tg_hcolor":
        s_up ["help_color"]=HELP_COLOR_STATUS [target_user_id ]=not HELP_COLOR_STATUS .get (target_user_id ,True )

    elif action .startswith ("pt_"):
        PANEL_TAB [target_user_id ]=action [3 :]

    elif action =="tg_avatar":
        s_up ["avatar"]=AVATAR_STATUS [target_user_id ]=not AVATAR_STATUS .get (target_user_id ,False )
        client_bot =ACTIVE_BOTS .get (target_user_id ,[None ])[0 ]
        if client_bot :
            if s_up ["avatar"]:
                AVATAR_STAMP .pop (target_user_id ,None )
                asyncio .create_task (_av_apply (client_bot ,target_user_id ))
            else :
                asyncio .create_task (_av_clear (client_bot ,target_user_id ))

    elif action =="cyc_font":
        cur =USER_FONT_CHOICES .get (target_user_id ,'stylized')
        if cur not in FONT_KEYS_ORDER :cur ='stylized'
        new_f =FONT_KEYS_ORDER [(FONT_KEYS_ORDER .index (cur )+1 )%len (FONT_KEYS_ORDER )]
        s_up ["font"]=USER_FONT_CHOICES [target_user_id ]=new_f 

        if CLOCK_STATUS .get (target_user_id ,False )and target_user_id in ACTIVE_BOTS :
            asyncio .create_task (perform_clock_update_now (ACTIVE_BOTS [target_user_id ][0 ],target_user_id ))

    elif action =="tg_bioclock":
        s_up ["bio_clock"]=BIO_CLOCK_STATUS [target_user_id ]=not BIO_CLOCK_STATUS .get (target_user_id ,False )
        if target_user_id in ACTIVE_BOTS :
            asyncio .create_task (perform_bio_update_now (ACTIVE_BOTS [target_user_id ][0 ],target_user_id ))

    elif action =="tg_biodate":
        s_up ["bio_date"]=BIO_DATE_STATUS [target_user_id ]=not BIO_DATE_STATUS .get (target_user_id ,False )
        if target_user_id in ACTIVE_BOTS :
            asyncio .create_task (perform_bio_update_now (ACTIVE_BOTS [target_user_id ][0 ],target_user_id ))

    elif action =="tg_biodatetype":
        curr =BIO_DATE_TYPE .get (target_user_id ,"jalali")
        new_type ="gregorian"if curr =="jalali"else "jalali"
        s_up ["bio_date_type"]=BIO_DATE_TYPE [target_user_id ]=new_type 
        if target_user_id in ACTIVE_BOTS :
            asyncio .create_task (perform_bio_update_now (ACTIVE_BOTS [target_user_id ][0 ],target_user_id ))

    elif action =="cyc_biofont":
        cur =BIO_FONT_CHOICE .get (target_user_id ,'stylized')
        if cur not in FONT_KEYS_ORDER :cur ='stylized'
        new_f =FONT_KEYS_ORDER [(FONT_KEYS_ORDER .index (cur )+1 )%len (FONT_KEYS_ORDER )]
        s_up ["bio_font"]=BIO_FONT_CHOICE [target_user_id ]=new_f 
        if target_user_id in ACTIVE_BOTS :
            asyncio .create_task (perform_bio_update_now (ACTIVE_BOTS [target_user_id ][0 ],target_user_id ))

    elif action =="tg_bold":
        new_b =not BOLD_MODE_STATUS .get (target_user_id ,False )
        BOLD_MODE_STATUS [target_user_id ]=new_b ;s_up ["bold"]=new_b 
        if new_b :
            SPOILER_MODE_STATUS [target_user_id ]=False ;CODE_MODE_STATUS [target_user_id ]=False ;UNDERLINE_MODE_STATUS [target_user_id ]=False ;GRADUAL_MODE_STATUS [target_user_id ]=False 
            s_up ["spoiler"]=False ;s_up ["code"]=False ;s_up ["underline"]=False ;s_up ["gradual"]=False 
    elif action =="tg_spoil":
        new_s =not SPOILER_MODE_STATUS .get (target_user_id ,False )
        SPOILER_MODE_STATUS [target_user_id ]=new_s ;s_up ["spoiler"]=new_s 
        if new_s :
            BOLD_MODE_STATUS [target_user_id ]=False ;CODE_MODE_STATUS [target_user_id ]=False ;UNDERLINE_MODE_STATUS [target_user_id ]=False ;GRADUAL_MODE_STATUS [target_user_id ]=False 
            s_up ["bold"]=False ;s_up ["code"]=False ;s_up ["underline"]=False ;s_up ["gradual"]=False 
    elif action =="tg_code":
        new_c =not CODE_MODE_STATUS .get (target_user_id ,False )
        CODE_MODE_STATUS [target_user_id ]=new_c ;s_up ["code"]=new_c 
        if new_c :
            BOLD_MODE_STATUS [target_user_id ]=False ;SPOILER_MODE_STATUS [target_user_id ]=False ;UNDERLINE_MODE_STATUS [target_user_id ]=False ;GRADUAL_MODE_STATUS [target_user_id ]=False 
            s_up ["bold"]=False ;s_up ["spoiler"]=False ;s_up ["underline"]=False ;s_up ["gradual"]=False 
    elif action =="tg_under":
        new_u =not UNDERLINE_MODE_STATUS .get (target_user_id ,False )
        UNDERLINE_MODE_STATUS [target_user_id ]=new_u ;s_up ["underline"]=new_u 
        if new_u :
            BOLD_MODE_STATUS [target_user_id ]=False ;SPOILER_MODE_STATUS [target_user_id ]=False ;CODE_MODE_STATUS [target_user_id ]=False ;GRADUAL_MODE_STATUS [target_user_id ]=False 
            s_up ["bold"]=False ;s_up ["spoiler"]=False ;s_up ["code"]=False ;s_up ["gradual"]=False 
    elif action =="tg_pemoji":
        s_up ["pemoji"]=PEMOJI_STATUS [target_user_id ]=not PEMOJI_STATUS .get (target_user_id ,False )

    elif action =="tg_tagalert":
        s_up ["tag_alert"]=TAG_ALERT_STATUS [target_user_id ]=not TAG_ALERT_STATUS .get (target_user_id ,False )

    elif action =="tg_dotcmd":
        s_up ["dot_commands"]=DOT_COMMANDS_STATUS [target_user_id ]=not DOT_COMMANDS_STATUS .get (target_user_id ,False )

    elif action =="tg_wordfilter":
        s_up ["filter_words_active"]=FILTER_WORDS_ACTIVE [target_user_id ]=not FILTER_WORDS_ACTIVE .get (target_user_id ,False )

    elif action =="tg_antidel":
        s_up ["anti_delete"]=ANTI_DELETE_STATUS [target_user_id ]=not ANTI_DELETE_STATUS .get (target_user_id ,False )

    elif action =="tg_antiedit":
        s_up ["anti_edit"]=ANTI_EDIT_STATUS [target_user_id ]=not ANTI_EDIT_STATUS .get (target_user_id ,False )

    elif action =="tg_selfdestruct":
        s_up ["self_destruct"]=SELF_DESTRUCT_STATUS [target_user_id ]=not SELF_DESTRUCT_STATUS .get (target_user_id ,False )

    elif action =="tg_gradual":
        new_g =not GRADUAL_MODE_STATUS .get (target_user_id ,False )
        GRADUAL_MODE_STATUS [target_user_id ]=new_g ;s_up ["gradual"]=new_g 
        if new_g :
            BOLD_MODE_STATUS [target_user_id ]=False ;SPOILER_MODE_STATUS [target_user_id ]=False ;CODE_MODE_STATUS [target_user_id ]=False ;UNDERLINE_MODE_STATUS [target_user_id ]=False 
            s_up ["bold"]=False ;s_up ["spoiler"]=False ;s_up ["code"]=False ;s_up ["underline"]=False 

    elif action =="tg_sec":
        s_up ["secretary"]=SECRETARY_MODE_STATUS [target_user_id ]=not SECRETARY_MODE_STATUS .get (target_user_id ,False )
        if s_up ["secretary"]:

            USERS_REPLIED_IN_SECRETARY [target_user_id ]=set ()
            data_manager .update_user_data (target_user_id ,{"replied_users":[]})

    elif action =="tg_firstcomment":
        if not FIRST_COMMENT_TEXT .get (target_user_id ,"").strip ():
            return await callback .answer ("اول متن کامنت اول را با دستور «تنظیم متن کامنت اول ...» تنظیم کنید.",show_alert =True )
        FIRST_COMMENT_STATUS [target_user_id ]=not FIRST_COMMENT_STATUS .get (target_user_id ,False )
        s_up ["first_comment"]=FIRST_COMMENT_STATUS [target_user_id ]

    elif action =="tg_seen":s_up ["auto_seen"]=AUTO_SEEN_STATUS [target_user_id ]=not AUTO_SEEN_STATUS .get (target_user_id ,False )

    elif action =="tg_tabpv":
        if not TABCHI_BANNER .get (target_user_id )and not TABCHI_BANNER_MEDIA .get (target_user_id ):
            return await callback .answer ("ابتدا بنر تبلیغاتی را با دستور «تنظیم بنر [متن]» (یا ریپلای روی رسانه) تنظیم کنید.",show_alert =True )
        s_up ["tabchi_pv"]=TABCHI_PV_STATUS [target_user_id ]=not TABCHI_PV_STATUS .get (target_user_id ,False )
        if s_up ["tabchi_pv"]:TABCHI_PV_COUNT [target_user_id ]=0 
        ensure_tabchi_loops_running (target_user_id )
    elif action =="tg_tabgp":
        if not TABCHI_BANNER .get (target_user_id )and not TABCHI_BANNER_MEDIA .get (target_user_id ):
            return await callback .answer ("ابتدا بنر تبلیغاتی را با دستور «تنظیم بنر [متن]» (یا ریپلای روی رسانه) تنظیم کنید.",show_alert =True )
        s_up ["tabchi_gp"]=TABCHI_GP_STATUS [target_user_id ]=not TABCHI_GP_STATUS .get (target_user_id ,False )
        if s_up ["tabchi_gp"]:TABCHI_GP_COUNT [target_user_id ]=0 
        ensure_tabchi_loops_running (target_user_id )
    elif action =="tg_tabsmart":
        if not TABCHI_BANNER .get (target_user_id )and not TABCHI_BANNER_MEDIA .get (target_user_id ):
            return await callback .answer ("ابتدا بنر تبلیغاتی را با دستور «تنظیم بنر [متن]» (یا ریپلای روی رسانه) تنظیم کنید.",show_alert =True )
        s_up ["tabchi_smart"]=TABCHI_SMART_STATUS [target_user_id ]=not TABCHI_SMART_STATUS .get (target_user_id ,False )
        if s_up ["tabchi_smart"]:TABCHI_PV_COUNT [target_user_id ]=0 ;TABCHI_GP_COUNT [target_user_id ]=0 
        ensure_tabchi_loops_running (target_user_id )
    elif action =="tg_tabspd":
        cur =TABCHI_SPEED .get (target_user_id ,"medium")
        new_spd ="fast"if cur =="medium"else "slow"if cur =="fast"else "medium"
        s_up ["tabchi_speed"]=TABCHI_SPEED [target_user_id ]=new_spd 
        ensure_tabchi_loops_running (target_user_id )
        try :await callback .answer (f"سرعت تبچی روی {new_spd } تنظیم شد.")
        except Exception :pass 

    elif action =="tg_cleanhelp":
        return await callback .answer (
        "پاکسازی و خروج:\n"
        "ترک / ترک گروه: حذف پیام‌های خودت در گروه و خروج\n"
        "ترک پیوی: پاکسازی کامل پیوی به‌صورت دوطرفه\n"
        "حذف پیام های امروز\n"
        "حذف پیام های هفته",
        show_alert =True 
        )

    elif action =="tg_fjoin":
        chats =FORCED_JOIN_CHATS .get (target_user_id ,[])
        if not chats :
            return await callback .answer ("ابتدا باید حداقل یک کانال یا گروه با دستور\n«تنظیم عضویت اجباری @یوزرنیم» ثبت کنید!",show_alert =True )

        FORCED_JOIN_ACTIVE [target_user_id ]=not FORCED_JOIN_ACTIVE .get (target_user_id ,False )
        s_up ["forced_join_active"]=FORCED_JOIN_ACTIVE [target_user_id ]

    elif action in ("tg_type","tg_game","tg_actph","tg_actvo","tg_actgi"):
        action_map ={
        "tg_type":("typing",TYPING_MODE_STATUS ),
        "tg_game":("playing",PLAYING_MODE_STATUS ),
        "tg_actph":("upload_photo",UPLOAD_PHOTO_STATUS ),
        "tg_actvo":("record_voice",RECORD_VOICE_STATUS ),
        "tg_actgi":("watch_gif",WATCH_GIF_STATUS ),
        }
        sel_key ,sel_dict =action_map [action ]
        new_val =not sel_dict .get (target_user_id ,False )
        for a_key ,(s_key ,s_dict )in action_map .items ():
            s_dict [target_user_id ]=False 
            s_up [s_key ]=False 
        sel_dict [target_user_id ]=new_val 
        s_up [sel_key ]=new_val 

    elif action =="tg_autosv":s_up ["auto_save"]=AUTO_SAVE_VIEW_ONCE [target_user_id ]=not AUTO_SAVE_VIEW_ONCE .get (target_user_id ,False )

    elif action =="tg_enm":
        if not ENEMY_ACTIVE .get (target_user_id ,False )and not ENEMY_LIST .get (target_user_id ,set ()):
            try :
                await callback .answer (
                "اول باید یه نفر رو با ریپلای روی پیامش و دستور «تنظیم دشمن» (یا از پنل «اکشن») به لیست دشمن اضافه کنی، وگرنه روشن کردن این دکمه اثری نداره.",
                show_alert =True 
                )
            except Exception :pass 
            return 
        s_up ["enemy_active"]=ENEMY_ACTIVE [target_user_id ]=not ENEMY_ACTIVE .get (target_user_id ,False )

    elif action =="tg_frnd":
        if not FRIEND_ACTIVE .get (target_user_id ,False )and not FRIEND_LIST .get (target_user_id ,set ()):
            try :
                await callback .answer (
                "اول باید یه نفر رو با ریپلای روی پیامش و دستور «تنظیم دوست» (یا از پنل «اکشن») به لیست دوست اضافه کنی، وگرنه روشن کردن این دکمه اثری نداره.",
                show_alert =True 
                )
            except Exception :pass 
            return 
        s_up ["friend_active"]=FRIEND_ACTIVE [target_user_id ]=not FRIEND_ACTIVE .get (target_user_id ,False )

    elif action =="tg_crsh":
        if not CRASH_ACTIVE .get (target_user_id ,False )and not CRASH_LIST .get (target_user_id ,set ()):
            try :
                await callback .answer (
                "اول باید یه نفر رو با ریپلای روی پیامش و دستور «تنظیم کراش» (یا از پنل «اکشن») به لیست کراش اضافه کنی، وگرنه روشن کردن این دکمه اثری نداره.",
                show_alert =True 
                )
            except Exception :pass 
            return 
        s_up ["crash_active"]=CRASH_ACTIVE [target_user_id ]=not CRASH_ACTIVE .get (target_user_id ,False )

    elif action =="tg_pv":s_up ["pv_lock"]=PV_LOCK_STATUS [target_user_id ]=not PV_LOCK_STATUS .get (target_user_id ,False )
    elif action =="tg_pvph":s_up ["pv_photo"]=PV_PHOTO_LOCK [target_user_id ]=not PV_PHOTO_LOCK .get (target_user_id ,False )
    elif action =="tg_pvvi":s_up ["pv_video"]=PV_VIDEO_LOCK [target_user_id ]=not PV_VIDEO_LOCK .get (target_user_id ,False )
    elif action =="tg_pvgi":s_up ["pv_gif"]=PV_GIF_LOCK [target_user_id ]=not PV_GIF_LOCK .get (target_user_id ,False )
    elif action =="tg_pvvo":s_up ["pv_voice"]=PV_VOICE_LOCK [target_user_id ]=not PV_VOICE_LOCK .get (target_user_id ,False )
    elif action =="tg_pvmu":s_up ["pv_music"]=PV_MUSIC_LOCK [target_user_id ]=not PV_MUSIC_LOCK .get (target_user_id ,False )
    elif action =="tg_pvst":s_up ["pv_sticker"]=PV_STICKER_LOCK [target_user_id ]=not PV_STICKER_LOCK .get (target_user_id ,False )
    elif action =="tg_pvloc":s_up ["pv_loc"]=PV_LOC_LOCK [target_user_id ]=not PV_LOC_LOCK .get (target_user_id ,False )
    elif action =="tg_pvemo":s_up ["pv_emo"]=PV_EMO_LOCK [target_user_id ]=not PV_EMO_LOCK .get (target_user_id ,False )
    elif action =="tg_pvtxt":s_up ["pv_txt"]=PV_TXT_LOCK [target_user_id ]=not PV_TXT_LOCK .get (target_user_id ,False )

    elif action .startswith ("lang_"):
        l_code =action .split ("_")[1 ]
        t_lang_map ={"en":"en","ru":"ru","cn":"zh-CN","off":None }
        t_target =t_lang_map .get (l_code )
        if l_code =="off"or AUTO_TRANSLATE_TARGET .get (target_user_id )==t_target :
            s_up ["translate"]=AUTO_TRANSLATE_TARGET [target_user_id ]=None 
        else :
            s_up ["translate"]=AUTO_TRANSLATE_TARGET [target_user_id ]=t_target 

    elif action =="close":
        INLINE_IDLE_STATE .get ("panel",{}).pop (target_user_id ,None )
        try :
            if callback .inline_message_id :
                res =await bot_api_request ("editMessageText",{
                "inline_message_id":callback .inline_message_id ,
                "text":"<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>پنل بسته شد.</b>",
                "parse_mode":"HTML"
                },timeout =5.0 )
                if not res .get ("ok"):
                    try:
                        await client .edit_inline_text (callback .inline_message_id ,"<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>پنل بسته شد.</b>",parse_mode ="html")
                    except Exception:
                        try:
                            await manager_bot.edit_inline_text(callback.inline_message_id, "<blockquote>ᴅᴀʀᴋsᴇʟꜰ</blockquote>\n<b>پنل بسته شد.</b>", parse_mode="html")
                        except Exception:
                            pass
            else :
                await callback .message .delete ()
        except Exception :
            pass 
        try :await callback .answer ()
        except Exception :pass 
        return 

    if s_up :
        data_manager .update_user_data (target_user_id ,{"settings":s_up })
        _commit_and_broadcast_shards ("panel-settings")

    try :
        if callback .inline_message_id :
            if str (action ).startswith ("pt_"):
                res =await bot_api_request ("editMessageText",{
                "inline_message_id":callback .inline_message_id ,
                "text":_panel_caption (target_user_id ),
                "parse_mode":"Markdown",
                "reply_markup":generate_panel_markup_json (target_user_id )
                },timeout =5.0 )
            else :
                res =await bot_api_request ("editMessageReplyMarkup",{
                "inline_message_id":callback .inline_message_id ,
                "reply_markup":generate_panel_markup_json (target_user_id )
                },timeout =5.0 )
            if not res .get ("ok")and not int ((res .get ("parameters")or {}).get ("retry_after",0 )):
                await client .edit_inline_reply_markup (callback .inline_message_id ,reply_markup =generate_panel_markup (target_user_id ))
        else :
            await callback .edit_message_reply_markup (reply_markup =generate_panel_markup (target_user_id ))
    except Exception :pass 

    asyncio .create_task (schedule_inline_auto_close (
    "panel",target_user_id ,
    inline_message_id =callback .inline_message_id ,
    message =None if callback .inline_message_id else callback .message 
    ))
    try :await callback .answer ()
    except Exception :pass 

def validate_database_payload (data :dict ):
    if not isinstance (data ,dict ):
        return False ,"ساختار فایل باید JSON object باشد."
    if "users"not in data or not isinstance (data .get ("users"),dict ):
        return False ,"کلید users داخل فایل پیدا نشد یا معتبر نیست."
    if "sessions"not in data or not isinstance (data .get ("sessions"),dict ):

        data ["sessions"]={}
    if "admins"not in data or not isinstance (data .get ("admins"),list ):
        data ["admins"]=[ROOT_ADMIN ]
    if ROOT_ADMIN not in data ["admins"]:
        data ["admins"].append (ROOT_ADMIN )
    return True ,"OK"

async def restart_process_after_restore (delay :float =2.0 ):
    await asyncio .sleep (delay )
    try :
        data_manager .force_save_sync ()
    except Exception :
        pass 
    os .execv (sys .executable ,[sys .executable ]+sys .argv )

async def restore_database_from_document (message ):
    if not message .document :
        return await message .reply_text ("**فایل دیتابیس رو به صورت فایل ارسال کن.**\nنام: `bot_data.json`")

    file_name =getattr (message .document ,"file_name","")or "database.json"
    if not file_name .lower ().endswith (".json"):
        return await message .reply_text ("**فقط فایل JSON قابل قبوله.**")

    if getattr (message .document ,"file_size",0 )and message .document .file_size >50 *1024 *1024 :
        return await message .reply_text ("**حجم فایل بیش از حد مجازه.**")

    wait =await message .reply_text ("**در حال دانلود و بررسی...**")
    temp_path =None 
    try :
        temp_path =await message .download (file_name =f"/tmp/restore_db_{uuid .uuid4 ().hex }.json")
        with open (temp_path ,"r",encoding ="utf-8")as f :
            new_data =json .load (f )

        ok ,reason =validate_database_payload (new_data )
        if not ok :
            return await wait .edit_text (f"**فایل دیتابیس معتبر نیست:**\n`{reason }`")

        try :
            sessions =new_data .setdefault ("sessions",{})
            fixed =0 
            for uid_str ,udata in new_data .get ("users",{}).items ():
                if not isinstance (udata ,dict ):
                    continue 
                phone =str (udata .get ("phone")or "").strip ()
                session_string =udata .get ("session_string")or udata .get ("session")or ""
                try :
                    uid_val =int (udata .get ("user_id")or uid_str )
                except Exception :
                    continue 
                if phone and session_string and phone not in sessions :
                    sessions [phone ]={"string":_db_encrypt (session_string ),"user_id":uid_val }
                    if isinstance (udata .get ("session_string"),str )and udata ["session_string"]:
                        udata ["session_string"]=_db_encrypt (udata ["session_string"])
                    fixed +=1 

            for phone ,s_data in sessions .items ():
                if isinstance (s_data ,dict ):
                    val =s_data .get ("string","")
                    if val and not str (val ).startswith (_DB_ENC_PREFIX ):
                        s_data ["string"]=_db_encrypt (val )
                        fixed +=1 
        except Exception :
            fixed =0 

        users_count =len (new_data .get ("users",{}))
        sessions_count =len (new_data .get ("sessions",{}))
        if sessions_count <=0 :
            return await wait .edit_text ("**هیچ سشنی پیدا نشد.** بازیابی لغو شد.")

        ts =datetime .now (TEHRAN_TIMEZONE ).strftime ("%Y%m%d_%H%M%S")
        backup_path =f"{DATA_FILE }.before_restore_{ts }"
        try :
            if os .path .exists (DATA_FILE ):
                shutil .copy2 (DATA_FILE ,backup_path )
                _secure_file_permissions (backup_path )
        except Exception :
            pass 

        tmp_out =f"{DATA_FILE }.restore_tmp"
        with open (tmp_out ,"w",encoding ="utf-8")as f :
            json .dump (new_data ,f ,ensure_ascii =False ,separators =(",",":"))
        os .replace (tmp_out ,DATA_FILE )
        _secure_file_permissions (DATA_FILE )

        data_manager .data =new_data 
        data_manager ._needs_save =False 

        await wait .edit_text (
        "**دیتابیس جایگزین شد.**\n\n"
        f"کاربران: `{users_count }`\n"
        f"سشن‌ها: `{sessions_count }`\n"
        f"ترمیم‌شده: `{fixed }`\n\n"
        "ربات تا چند ثانیه دیگه ری‌استارت می‌شه."
        )
        asyncio .create_task (restart_process_after_restore (2.5 ))
    except Exception as e :
        try :
            await wait .edit_text (f"**بازیابی دیتابیس انجام نشد:**\n`{str (e )[:180 ]}`")
        except Exception :
            pass 
    finally :
        if temp_path and os .path .exists (temp_path ):
            try :os .remove (temp_path )
            except Exception :pass 

@manager_bot .on_message (filters .private &filters .reply &filters .text ,group =-60 )
async def manager_root_ban_reply_handler (client ,message ):
    if not message .from_user or int (message .from_user .id )!=ROOT_ADMIN :
        return 
    cmd =(message .text or "").strip ().strip (".").strip ().lower ().replace ("ي","ی").replace ("ك","ک")
    if cmd not in ("قفل","قفل باز"):
        return 
    if not message .reply_to_message or not message .reply_to_message .from_user :
        return await message .reply_text ("**روی پیام کاربر ریپلای کن.**")
    target_id =int (message .reply_to_message .from_user .id )
    if target_id ==ROOT_ADMIN :
        return await message .reply_text ("**ادمین اصلی قابل قفل شدن نیست.**")
    if cmd =="قفل":
        data_manager .ban_user (target_id )
        try :
            await stop_user_bot (target_id )
        except Exception :
            pass 
        return await message .reply_text (f"**قفل فعال شد.**\nکاربر: `{target_id }`")
    data_manager .unban_user (target_id )
    return await message .reply_text (f"**قفل کاربر `{target_id }` باز شد.**")

@manager_bot .on_message (filters .private ,group =-50 )
async def manager_banned_user_guard (client ,message ):
    if not message .from_user :
        return 
    uid =int (message .from_user .id )
    if uid ==ROOT_ADMIN :
        return 
    if data_manager .is_banned (uid ):
        try :
            await stop_user_bot (uid )
        except Exception :
            pass 
        await message .reply_text ("**دسترسی مسدود شده.**",reply_markup =ReplyKeyboardRemove ())
        raise StopPropagation 

def _admin_log_access (user ,chat ):
    if not user or not chat or chat .type !=ChatType .PRIVATE :
        return False 
    return chat .id ==user .id and (user .id ==ROOT_ADMIN or user .id in data_manager .get_admins ())

async def _show_admin_log_page (message ,page =0 ,edit =False ):
    records =await asyncio .to_thread (_read_recent_admin_logs )
    page_size =8 
    pages =max (1 ,(len (records )+page_size -1 )//page_size )
    page =max (0 ,min (int (page ),pages -1 ))
    body =["<b>لاگ</b>",f"<b>صفحهٔ {page +1 } از {pages }</b> · {len (records )} رویداد اخیر"]
    if page ==0 :
        active_module =sys .modules .get ("pyrogram")
        active_version =html .escape (str (getattr (active_module ,"__version__","unknown")))
        python_path =html .escape (str (sys .executable ))
        module_path =html .escape (str (getattr (active_module ,"__file__","unknown")))
        body .append (
        f"<b>محیط فعال ربات مدیریت</b>\n"
        f"<b>نسخهٔ کتابخانه:</b> <code>{active_version }</code>\n"
        f"<b>مسیر پایتون:</b> <code>{python_path }</code>\n"
        f"<b>مسیر کتابخانه:</b> <code>{module_path }</code>"
        )
    levels ={"INFO":"اطلاعات","WARNING":"هشدار","ERROR":"خطا","CRITICAL":"بحرانی"}
    if not records :
        body .append ("<b>هنوز رویدادی ثبت نشده است.</b>")
    for item in records [page *page_size :(page +1 )*page_size ]:
        stamp =datetime .fromtimestamp (item ["ts"],TEHRAN_TIMEZONE ).strftime ("%m-%d %H:%M:%S")
        level =levels .get (item ["level"],item ["level"])
        text =re .sub (r"\s+"," ",item ["text"]).strip ()
        
        encoded =text .encode ("utf-16-le",errors ="replace")
        text =encoded [:460 ].decode ("utf-16-le",errors ="ignore")+("…"if len (encoded )>460 else "")
        label =html .escape (f"{stamp } · {level } · {item ['source']}")
        body .append (f"<b>{label }</b>\n<code>{html .escape (text )}</code>")
    body .append ("<b>زمان تهران</b> · اطلاعات حساسِ قابل‌شناسایی پوشانده شده‌اند.")
    navigation =[]
    if page >0 :navigation .append (InlineKeyboardButton ("جدیدتر",callback_data =f"adminlogs_page_{page -1 }"))
    if page +1 <pages :navigation .append (InlineKeyboardButton ("قدیمی‌تر",callback_data =f"adminlogs_page_{page +1 }"))
    rows =[navigation ]if navigation else []
    rows .append ([
    InlineKeyboardButton ("به‌روزرسانی",callback_data =f"adminlogs_page_{page }"),
    InlineKeyboardButton ("آخرین رویدادها",callback_data ="adminlogs_page_0")
    ])
    rows .append ([InlineKeyboardButton ("بستن",callback_data ="adminlogs_close")])
    text ="\n\n".join (body )
    markup =InlineKeyboardMarkup (rows )
    if edit :
        await message .edit_text (text ,parse_mode =ParseMode .HTML ,reply_markup =markup )
    else :
        await message .reply_text (text ,parse_mode =ParseMode .HTML ,reply_markup =markup ,quote =False ,protect_content =True )

DEPLOY_WORDS = ("آپدیت", "اپدیت", "آپدیت کد", "نصب", "deploy", "update")
DEPLOY_MIN_BYTES = 50 * 1024

@manager_bot .on_message (filters .private &filters .document ,group =-20 )
async def admin_deploy_handler (client ,message ):
    sender =getattr (message ,"from_user",None )
    if not sender or sender .id !=ROOT_ADMIN :
        return
    doc =getattr (message ,"document",None )
    name =str (getattr (doc ,"file_name","")or "")
    if not name .lower ().endswith (".py"):
        return
    cap =" ".join ((getattr (message ,"caption",None )or "").split ()).lower ()
    if cap not in [w .lower ()for w in DEPLOY_WORDS ]:
        await message .reply_text (
        "✦ <b>𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙</b> ✦  ·  DEPLOY\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "برای جایگزینی کد، همین فایل را با کپشن <code>آپدیت</code> بفرست.",
        parse_mode =ParseMode .HTML )
        raise StopPropagation
    size =int (getattr (doc ,"file_size",0 )or 0 )
    if size <DEPLOY_MIN_BYTES :
        await message .reply_text ("**فایل خیلی کوچک است؛ احتمالاً سورس کامل نیست.**")
        raise StopPropagation
    note =await message .reply_text ("**◈ در حال بررسی فایل...**")
    live =os .path .abspath (__file__ )
    stamp =str (int (time .time ()))
    newp =os .path .join (tempfile .gettempdir (),f"deploy_{stamp }.py")
    backup =f"{live }.bak.{stamp }"
    try :
        await client .download_media (message ,file_name =newp )
    except Exception as exc :
        logger .warning ("deploy download failed: %s",type (exc ).__name__ )
        await note .edit_text ("**دانلود فایل ناموفق بود.**")
        raise StopPropagation
    try :
        chk =subprocess .run ([sys .executable ,"-m","py_compile",newp ],
        capture_output =True ,text =True ,timeout =120 )
    except Exception as exc :
        chk =None
        logger .warning ("deploy compile error: %s",type (exc ).__name__ )
    if chk is None or chk .returncode !=0 :
        err =((chk .stderr or chk .stdout )if chk else "timeout")or "unknown"
        err =err .strip ().splitlines ()[-1 ][:220 ]if err .strip ()else "unknown"
        try :
            os .remove (newp )
        except Exception :
            pass
        await note .edit_text (
        "✦ <b>𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙</b> ✦  ·  DEPLOY\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<b>◈ کد ایراد دارد، جایگزین نشد</b>\n\n"
        f"<code>{html .escape (err )}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✧ نسخه فعلی دست‌نخورده باقی ماند",parse_mode =ParseMode .HTML )
        raise StopPropagation
    try :
        lines =open (newp ,encoding ="utf-8").read ().count ("\n")+1
    except Exception :
        lines =0
    try :
        shutil .copyfile (live ,backup )
        shutil .copyfile (newp ,live )
        os .remove (newp )
    except Exception as exc :
        logger .warning ("deploy swap failed: %s: %s",type (exc ).__name__ ,str (exc )[:120 ])
        await note .edit_text ("**جایگزینی فایل ناموفق بود.**")
        raise StopPropagation
    guard =os .path .join (tempfile .gettempdir (),f"guard_{stamp }.sh")
    try :
        with open (guard ,"w",encoding ="utf-8")as fh :
            fh .write (
            "#!/bin/bash\n"
            "sleep 2\n"
            "bash /root/run_bot.sh\n"
            "sleep 75\n"
            "if ! pgrep -f '/root/[f]ilename.py' >/dev/null; then\n"
            f"  cp {live } {live }.failed.{stamp }\n"
            f"  cp {backup } {live }\n"
            "  bash /root/run_bot.sh\n"
            f"  curl -s -X POST 'https://api.telegram.org/bot{BOT_TOKEN }/sendMessage' "
            f"-d chat_id={ROOT_ADMIN } "
            "--data-urlencode 'text=◈ کد جدید بالا نیامد؛ نسخه قبلی برگردانده شد.' >/dev/null\n"
            "else\n"
            f"  curl -s -X POST 'https://api.telegram.org/bot{BOT_TOKEN }/sendMessage' "
            f"-d chat_id={ROOT_ADMIN } "
            "--data-urlencode 'text=◈ کد جدید با موفقیت اجرا شد.' >/dev/null\n"
            "fi\n")
        os .chmod (guard ,0o755 )
    except Exception as exc :
        logger .warning ("deploy guard write failed: %s",type (exc ).__name__ )
    await note .edit_text (
    "✦ <b>𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙</b> ✦  ·  DEPLOY\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "<b>◈ کد جایگزین شد</b>\n\n"
    f"◈ خط      <code>{lines :,}</code>\n"
    f"◈ حجم     <code>{size //1024 :,}</code> کیلوبایت\n"
    f"◈ بکاپ    <code>{os .path .basename (backup )}</code>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "✧ در حال ری‌استارت؛ نتیجه را همین‌جا می‌فرستم",parse_mode =ParseMode .HTML )
    logger .info ("deploy: new source installed (%d lines), restarting",lines )
    try :
        subprocess .Popen (["setsid","bash",guard ],stdout =subprocess .DEVNULL ,
        stderr =subprocess .DEVNULL ,start_new_session =True )
    except Exception as exc :
        logger .warning ("deploy guard start failed: %s",type (exc ).__name__ )
    raise StopPropagation

@manager_bot .on_message (filters .private &filters .regex (r"^(?:سورس|source|/source)$"),group =-20 )
async def admin_source_handler (client ,message ):
    sender =getattr (message ,"from_user",None )
    if not sender or sender .id !=ROOT_ADMIN :
        raise StopPropagation
    path =os .path .abspath (__file__ )
    try :
        raw =open (path ,encoding ="utf-8").read ()
    except Exception as exc :
        logger .warning ("source read failed: %s",type (exc ).__name__ )
        await message .reply_text ("**خواندن سورس ناموفق بود.**")
        raise StopPropagation
    lines =raw .count ("\n")+1
    size =len (raw .encode ("utf-8"))
    stamp =datetime .now (TEHRAN_TIMEZONE ).strftime ("%Y-%m-%d_%H-%M")
    out =os .path .join (tempfile .gettempdir (),f"darkself_{stamp }.py")
    try :
        with open (out ,"w",encoding ="utf-8")as fh :
            fh .write (raw )
        cap =("✦ <b>𝗗𝗔𝗥𝗞𝗦𝗘𝗟𝗙</b> ✦  ·  SOURCE\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"◈ خط      <code>{lines :,}</code>\n"
        f"◈ حجم     <code>{size //1024 :,}</code> کیلوبایت\n"
        f"◈ تاریخ   <code>{stamp .replace ('_',' ')}</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "✧ آخرین نسخه، مستقیم از سرور")
        await client .send_document (message .chat .id ,out ,caption =cap ,parse_mode =ParseMode .HTML ,
        file_name =f"darkself_{stamp }.py")
    except Exception as exc :
        logger .warning ("source send failed: %s: %s",type (exc ).__name__ ,str (exc )[:120 ])
        try :
            await message .reply_text ("**ارسال سورس ناموفق بود.**")
        except Exception :
            pass
    finally :
        try :
            os .remove (out )
        except Exception :
            pass
    raise StopPropagation

@manager_bot .on_message (filters .private &filters .regex (r"^لاگ$"),group =-20 )
async def admin_log_menu_handler (client ,message ):
    if not _admin_log_access (message .from_user ,message .chat ):
        raise StopPropagation 
    try :
        await _show_admin_log_page (message )
    except Exception as exc :
        logger .warning ("Admin log page failed: %s",type (exc ).__name__ )
    raise StopPropagation 

def _admin_text_reset_access (user ,chat ):
    return bool (user and chat and user .id ==ROOT_ADMIN and chat .type ==ChatType .PRIVATE and chat .id ==ROOT_ADMIN )

def _admin_other_keyboard ():
    return ReplyKeyboardMarkup ([
    [KeyboardButton ("ریست لیست")],
    [KeyboardButton ("بازگشت به پنل ادمین")]
    ],resize_keyboard =True )

def _reset_all_target_reply_texts ():
    
    defaults ={"enemy_replies":ENEMY_REPLIES_DEFAULT ,"friend_replies":FRIEND_REPLIES_DEFAULT ,"crash_replies":CRASH_REPLIES_DEFAULT }
    affected =[]
    skipped =0 
    for uid_str ,data in list (data_manager .get_all_users ().items ()):
        try :uid =int (uid_str )
        except (TypeError ,ValueError ):
            skipped +=1 
            continue 
        if not isinstance (data ,dict ):
            skipped +=1 
            continue 
        for key ,baseline in defaults .items ():
            data [key ]=list (baseline )
        affected .append ((uid_str ,uid ))
    if not affected :return {"users":0 ,"skipped":skipped }
    data_manager .save_data ()
    data_manager .force_save_sync ()
    if data_manager ._needs_save :
        raise OSError ("Reply defaults were not saved")
    
    persisted =data_manager ._read_json_file (data_manager .file_path ).get ("users",{})
    for uid_str ,uid in affected :
        saved =persisted .get (uid_str )
        if not isinstance (saved ,dict )or any (saved .get (key )!=baseline for key ,baseline in defaults .items ()):
            raise RuntimeError ("Reply defaults persistence verification failed")
    for uid_str ,uid in affected :
        ENEMY_REPLIES [uid ]=list (ENEMY_REPLIES_DEFAULT )
        FRIEND_REPLIES [uid ]=list (FRIEND_REPLIES_DEFAULT )
        CRASH_REPLIES [uid ]=list (CRASH_REPLIES_DEFAULT )
    _shard_signal_reload ()
    return {"users":len (affected ),"skipped":skipped }

@manager_bot .on_message (filters .private &filters .regex (r"^(سایر|ریست لیست|بازگشت به پنل ادمین)$"),group =-20 )
async def admin_other_menu_handler (client ,message ):
    try :
        if not _admin_text_reset_access (message .from_user ,message .chat ):
            return 
        if getattr (message ,"forward_date",None )or getattr (message ,"via_bot",None ):
            return 
        uid =message .from_user .id 
        text =(message .text or "").strip ()
        ADMIN_TEXT_RESET_CONFIRMATIONS .pop (uid ,None )
        if text =="بازگشت به پنل ادمین":
            await message .reply_text ("<b>پنل مدیریت</b>",parse_mode =ParseMode .HTML ,reply_markup =get_admin_menu_keyboard (uid ))
        elif text =="سایر":
            await message .reply_text ("<b>سایر</b>\nگزینهٔ موردنظر را انتخاب کنید.",parse_mode =ParseMode .HTML ,reply_markup =_admin_other_keyboard ())
        elif text =="ریست لیست":
            token =secrets .token_hex (12 )
            markup =InlineKeyboardMarkup ([
            [InlineKeyboardButton ("تأیید ریست برای همه",callback_data =f"admintexts_reset_confirm:{token }")],
            [InlineKeyboardButton ("انصراف",callback_data =f"admintexts_reset_cancel:{token }")]
            ])
            sent =await message .reply_text (
            "<b>ریست متن‌های همهٔ کاربران</b>\n\nمتن‌های دوست، دشمن و کراشِ همهٔ کاربران، حتی کاربران غیرفعال، دقیقاً با پیش‌فرض‌های همین فایل جایگزین می‌شوند.\nمتن‌های اختصاصی حذف می‌شوند؛ سشن‌ها، تنظیمات و افراد ثبت‌شده تغییر نمی‌کنند.\n\nتأیید می‌کنید؟",
            parse_mode =ParseMode .HTML ,reply_markup =markup )
            ADMIN_TEXT_RESET_CONFIRMATIONS [uid ]={"token":token ,"message_id":sent .id ,"expires":time .monotonic ()+300 }
    except Exception as exc :
        logger .warning ("Admin other menu failed: %s",type (exc ).__name__ )
    finally :
        raise StopPropagation 

@manager_bot .on_callback_query (filters .regex (r"^admintexts_reset_"),group =-20 )
async def admin_text_reset_callback (client ,callback ):
    try :
        chat =getattr (callback .message ,"chat",None )
        if not _admin_text_reset_access (callback .from_user ,chat ):
            await callback .answer ("دسترسی غیرمجاز.",show_alert =True )
            return 
        uid =callback .from_user .id 
        match =re .fullmatch (r"admintexts_reset_(confirm|cancel):([0-9a-f]{24})",callback .data or "")
        pending =ADMIN_TEXT_RESET_CONFIRMATIONS .get (uid )
        if not match or not pending or pending ["token"]!=match .group (2 )or pending ["message_id"]!=callback .message .id or pending ["expires"]<=time .monotonic ():
            await callback .answer ("این درخواست معتبر نیست یا منقضی شده؛ دوباره «ریست لیست» را بزنید.",show_alert =True )
            return 
        
        ADMIN_TEXT_RESET_CONFIRMATIONS .pop (uid ,None )
        try :await callback .answer ()
        except Exception :pass 
        if match .group (1 )=="cancel":
            await callback .message .edit_text ("ریست لیست لغو شد.",reply_markup =None )
            return 
        try :
            result =_reset_all_target_reply_texts ()
        except Exception as exc :
            logger .error ("Global reply reset could not be verified: %s",type (exc ).__name__ )
            await callback .message .edit_text ("ذخیرهٔ کامل ریست تأیید نشد. جزئیات در لاگ مدیر ثبت شده است؛ پیام موفقیت صادر نمی‌شود.",reply_markup =None )
            return 
        logger .info ("Root admin reset reply defaults for %s users",result ["users"])
        if not result ["users"]:
            await callback .message .edit_text ("کاربر معتبری برای ریست لیست ثبت نشده است.",reply_markup =None )
            return 
        text =f"<b>ریست لیست انجام شد.</b>\n\nمتن‌های پیش‌فرض دوست، دشمن و کراش برای {result ['users']} کاربر ذخیره شد.\nکش‌های همین پردازش به‌روز شدند و درخواست همگام‌سازی به شاردها ارسال شد.\nکاربران نیازی به خروج یا ریست حساب ندارند."
        if result ["skipped"]:text +=f"\nرکورد نامعتبرِ ردشده: {result ['skipped']}"
        await callback .message .edit_text (text ,parse_mode =ParseMode .HTML ,reply_markup =None )
    except Exception as exc :
        logger .warning ("Admin reply reset callback failed: %s",type (exc ).__name__ )
    finally :
        raise StopPropagation 

def get_admin_menu_keyboard (uid ):
    if uid ==ROOT_ADMIN :
        return ReplyKeyboardMarkup ([
        [KeyboardButton ("فعال‌سازی سلف"),KeyboardButton ("تنظیم لیمیت")],
        [KeyboardButton ("مدیریت ادمین‌ها"),KeyboardButton ("مدیریت کاربران")],
        [KeyboardButton ("پیام همگانی"),KeyboardButton ("وضعیت سرور")],
        [KeyboardButton ("وضعیت سراسری سلف‌ها"),KeyboardButton ("عضویت اجباری سراسری")],
        [KeyboardButton ("بکاپ دیتابیس"),KeyboardButton ("بازیابی دیتابیس")],
        [KeyboardButton ("حذف کامل دیتابیس")],
        [KeyboardButton ("لاگ"),KeyboardButton ("سایر")]
        ],resize_keyboard =True )
    else :
        rows =[[KeyboardButton ("فعال‌سازی سلف")]]
        if uid in data_manager .get_admins ():
            rows .append ([KeyboardButton ("لاگ")])
        return ReplyKeyboardMarkup (rows ,resize_keyboard =True )

def _self_limit_text ():
    limit ,used ,free =data_manager .self_limit_status ()
    if not limit :
        return (
        "**تنظیم لیمیت فعال‌سازی سلف**\n\n"
        "وضعیت فعلی: **نامحدود**\n"
        f"سلف‌های فعال همین حالا: `{used }`\n\n"
        "با «تعداد دلخواه» می‌تونی سقف تعداد کاربرهایی که اجازهٔ فعال‌سازی سلف دارن رو مشخص کنی."
        )
    return (
    "**تنظیم لیمیت فعال‌سازی سلف**\n\n"
    f"وضعیت فعلی: **{limit } نفر**\n"
    f"پر شده: `{used }`  ·  جای خالی: `{free }`\n\n"
    "وقتی ظرفیت پر بشه، نفر بعدی پیام «ظرفیت تکمیل است» می‌گیره و نمی‌تونه سلف فعال کنه.\n"
    "هر وقت سلف یکی از کاربرها غیرفعال یا حذف بشه، یک جا آزاد می‌شه."
    )

def _self_limit_markup ():
    return InlineKeyboardMarkup ([
    [InlineKeyboardButton ("نامحدود",callback_data ="slflimit_off")],
    [InlineKeyboardButton ("تعداد دلخواه",callback_data ="slflimit_set")],
    ])

@manager_bot .on_message (filters .regex ("^تنظیم لیمیت$")&filters .private )
async def self_limit_menu_handler (client ,message ):
    if not message .from_user or message .from_user .id !=ROOT_ADMIN :return 
    await message .reply_text (_self_limit_text (),reply_markup =_self_limit_markup ())

def self_capacity_full_text ():
    limit ,used ,free =data_manager .self_limit_status ()
    return (
    "**ظرفیت فعال‌سازی سلف تکمیل شده.**\n\n"
    f"در حال حاضر فقط **{limit } نفر** می‌تونن سلف فعال کنن و همهٔ جاها پر شده.\n"
    "هر وقت یکی از کاربرها سلفش رو غیرفعال کنه یا حذف بشه، یک جا آزاد می‌شه.\n\n"
    "بعداً دوباره /start رو بزن و امتحان کن."
    )

# ======================= Main menu (پنل اصلی) =======================
_RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
_MINIAPP_EXPLICIT = os.environ.get("MINIAPP_URL", "").strip()
_MINIAPP_PUBLIC = _MINIAPP_EXPLICIT if (_MINIAPP_EXPLICIT.startswith("https://") and "github.io" not in _MINIAPP_EXPLICIT) else (f"https://{_RAILWAY_DOMAIN}/" if _RAILWAY_DOMAIN else "")
MENU_MINIAPP_URL = _MINIAPP_PUBLIC or _MINIAPP_EXPLICIT or "https://mashaiiiooob-bot.github.io/Myself-/miniapp/"
MENU_CHANNEL_URL = os.environ.get("CHANNEL_URL", "").strip()
MENU_SUPPORT_URL = os.environ.get("SUPPORT_URL", "").strip()
_MENU_PHOTO_FILE_ID = None
_MENU_CAPTION = "<b>⚡ پنل اصلی VOLDYSELF</b>\n\nیکی از گزینه‌های زیر را انتخاب کن 👇"
_MENU_IMG_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAUEBAQEAwUEBAQGBQUGCA0ICAcHCBALDAkNExAUExIQEhIUFx0ZFBYcFhISGiMaHB4fISEhFBkkJyQgJh0gISD/2wBDAQUGBggHCA8ICA8gFRIVICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICD/wAARCALQBQADASIAAhEBAxEB/8QAHQABAAMBAAMBAQAAAAAAAAAAAAECAwQFBgcICf/EAEkQAQACAQIEBAIHBQUGAwcFAAABAgMEEQUGITESQVFhBxMUInGBkaGxMkJScsEVYoKSoggjM0PR4SWy8CQ0RFNjc8I1RmSjs//EABsBAQADAQEBAQAAAAAAAAAAAAABAgMEBQYH/8QANhEBAAICAQMCAwYFBAEFAAAAAAECAxEEEiExBRMGQVEiMmFxodEUQoGxwSMzQ+HxNVJikfD/2gAMAwEAAhEDEQA/APxkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmAASAAAAAAAAAAAAAlMVtPaECo0jFaU/KsnSNwyGny5RNZg6TcKC20oOlKBOyEaABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJgAEgAAAAAAAADfFp75esdK+qNomYjvLGImZ6Ru2x6e9us9Id+PTVx9o6+raMfsr1Q57Zvo4q6akdZ6/a0jFEeTq+WjwK9bKbzLn8EKzT2dM0VmqepHU5pp7K2x+jp8MKzX0TFlos5LY2U0ds169mdqLxLWt3HMbDa1GUxss2idq7IWRMKzCyAFQAAAToAEAAAAAAnQAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMAAkAAAAAAExEzPTqmKza0ViN5ns8xpNBGOIvfrf9FLWiFL3ikblzafQzO1ssfZV5CuLaOzpri22hrGL2c9sjgvkm3lyRj6LfL9XXGPon5ezLrU25Plx6Kzj9nZ8tE09k9ZtxTT2Umvs7Zp7Mpp7LRdO3HNWcxLrtRlajSLLRLCY6M7V6dW1o2UlpErxLntVlarqmPZjaGkS2rLlmENLQzld0RO0ShZVVInZCdwSISkRKEyhEgAgAEgAAAiQAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYABIAAAAJiJmdohDy/CtF45+kZI3iP2I/qpa3TG5VtaKxuWug0Hy6/Myx9ee0fwvK1x+zSmPaG1aPPvl3LzLXm07llFI9F4o2inRaKOebs2Hg9jwOjwHghXrTtzzTorNHTNVZomLjktRnavs65r0ZWq1i6YclqsLV9nZarG1W1bLw47V9mMx1dd6ue8OisrwxsytDaWdoaxLSHNeGVo2b2hjaGkS6KyoqsiSWqAWBVMSkBEoTKESACAASACQAQACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATAAJAAAEwgdGj01tVqa469u9p9Ie2YsNaVitY2rEbREeUOPhGj+TpYvaPr5Os/Z5Q8tSjzs+Xc6h52fJ1W1CK0axRetY2Xirz5u55lSKrbQv4fZPh9mXWjbPw+aPC28PRHh9kdYw8KJq3mvsiardaXNMdGVquqa+zO1fZpW6XHerC9Xbevs58ldnTSy0OK8Oa8dZdl4jq5skdJdVZaQ5bMrd212MuiGkMrsLd29mF20S6Ks1VlUthZVZMAAAjYSCJQsqiQAVABMAAkAEAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEgAkHXw/TfStbjxT+z3t9kd3K9j5e022HLqLR+1Pgj7I6z/AEZZb9FZlnkt01mXm8dOnZvWqa1a1q8G93kqxXq0isLRXr2aRVzTZDPwp8DWKwtFWfUlj4DwN/Cnwq9Q5vAiaOnwKzRPUOWaMrV6OyadGVqNK2WcV6ubJV5C9HJlq6qXTDx149nLkjrLuyw48nm78c7aQ4r92FnRkc1p67OyraGd2F21mdMWXUZYxYMV8t57VpWbTP3Q1iezoqxlD2rQ/D7m/iMVth4HnxUn9/UbYo/1TD2jRfBfjGWInXcW0elie9ccWyzH5RH5uPL6hxcP38kR/VM5aV8y+XRCfN900nwU4LSKzrOMa7PPnGKlMcfn4nndN8JuSsMR49BqNTMd5y6m3X/Ls8zJ8R8GniZn8o/fTKeTSH5u2n0Nn6lw/DvkrF+zy3pbfz2vb9bOuvInJ8V2jljh23vh3/q45+KuJHitv0/dX+Kr9H5PmJ9EbS/WVuQuTbxtbljh/wB2OY/SXFn+FvI+oid+AUxTPnhz5K7f6k1+KeJM962j+kfufxVfo/LaJfozWfBDlTPvOl1fENHby2yVyVj7piJ/N6rxP4EcUxxa3COOabVRHamox2w2n748Ufo9HF67wcvbr1+caaRnxz83xwezcZ5D5s4DW2TiXBNTTDXvmx1+Zj/zV3iPvetTGz16ZKZI6qTuPwbRMT4QA1SAAAAAAAKgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmAASJh7zwzB8jQYMc94pEz9s9f6vS9Nj+bqcWL+O8V/GX0KlY3edzLaiIcfKt2iGlY82kRPdFa+zaI6dnh2s4URWN2lapiOvRpFdvJjMisVWiF4jdeKs5kZxVaKNYovFFJslz+BHg9nXFPZPy0dY4px+zO+L2eR+VuTp5lMZEvDXxezizY+/R7BfSTMfszLH+yNZqbeHBpsl/sjp+LopmiPMj1TNXbfo8fm6RMy+l6PkHNqNr8R1cYK7/sYfrWn756R+b2nh3J/L/DrVvi4dTNlj/maj/eW/PpH4LX9X4+H57n8E+5EPiOh5e43xiY/s3hmfPWf+ZFfDSP8U7R+b2/hvwk4ln2vxXiWHSV86YInLf8AHpEfm+w1pG0Rt0jtHo2rTyeTn+Is9u2KIr+s/wD7+iPft8npfDfhhypofDbNpMnEMkeeqyTNZ/w12j9XuGi4dotBjjHodJg0lI6eHBjikflDqrVtWvV8/n53Izf7l5lSbWt5lnGPfrPdpGKI8mla9GtavPm8qsoxw0rjaRVrFVY3IyrT2aVxbta1aRTs0iiWUYloxN4p7LxRrFUOeMfstGJ0RVPhTo25/BNZ3rvE+3R6lzB8O+VOY63vruFUw6m3/wATpYjFk39Z2ja33xL3Xwomu7ow58uC3VitMT+C1bTXvEvzNzR8FePcJrfVcByf2zpa7zOOtfDnrH8na3+Gd/Z8tyYsmLLbHlpal6zNbVtExNZjvEx5P3RakbdnqHN/w85f5ww2vrcH0biG21NdgiPmR6eKO149p6+kw+u4HxHMapy4/rH+Y/Z2Y+T8rvyHsh7LzZybxrk/if0Tium/3V5n5Opp1x54jzrPr6xPWHrb7Wl65Kxek7iXdExMbhAC6QAABUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEjyHBqRfjOmiY3iLb/hG73ukdIek8vxvxnH7VtP+mXvOOOkPH58/ah5/J+9ENax0awpXs2iHi2lyprXo1rG6IhrWrKZCtevZpFeqa1aRDKZSrWrStOi1atq1ZTZLOuNrXFv5NqUdFMbG10MKaffydWPRxM9Yb48cbQ7cWOHLfLKNssGjxxO/gj8Hk8WGsViIjpCuOsRDopDhyXmWe2lKR6Nq1jZSrWvo5ZkWiGtYUq1qxkaVjo0iFaz0XqxlLSsdWkR5q17tKs/KWlatq1jZWkNax1b1gTWrWKx0K13a1q2iEIiq0VWiNlohbQjwwbQv4d0xU0M9oRNW3hR4UjCaI8DfZE1RoeJ4vwbhvHOF5eGcV0ePV6PNH18d/KfK0T3i0eUx1h+W/iH8OddyVroz4bX1fB89tsOp260n+DJt2t6T2mO3nEfrjb1cfEeHaPinDs/D+Iaamq0mopNMmK8dLR/T2ny7va9M9UycK+p70nzH+YbYss45/B+FpQ90+IXI2q5J5itp48ebhuo3vo9RaP26+dbf3q9p+6fN6ZL9MxZa5aRkpO4l60TFo3CAGqQBUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAeW5fnbjWL3raP9MveqR0egcEtFeN6Xedom/h/GJh9Ax9njeofeh5/J+9DasezasM6R0bV7vFlzL1jo3rHszrDarG0pWiOzSseyKx2a0hjMi1at61VrDelfdhaUL0o6cdWdIb0hzWlDelXXjjZz44dNXJdWXRRtVjWWlXPKrerWvkxiWtZ6MZG0dGtWENq9mMpbVaVZVlpVlKzavdvSGFHRRWsdxvSOzekMqeTorEumIRK9Y6NKwitd29a+y6FYr0XistIpPTo0ik+iRj4JlaMct4onw+y2jbDwSeGXR4Tw+yNDl8Cs1dU09lZp7GhzTRSa7OqaKTXp2QPWObeV9Bzby3qeDa+taxk+tizbbzgyxH1bx+kx5xMw/G3GeE63gfGdVwjiOH5Wq0uSceSveN/WPWJjaYnziX7rtX2fD/jxyjGq4Zp+bdFhj5+k2wayax1timdqXn+Wfq/ZaPR9X6B6hOPJ/DXntbx+E/8Abr42TU9M+H50EzCH3z0gBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJABAAA30uX5Orw5v4Lxb8JfSqd527bvl8Po3C830jhumy+dqRv9sdJ/R5fqFfsxZx8mO0S8nTs3qxo2q+fs4oa1htWGVW9WEpaVjs2rDKvk2qwsNat6MatqsLI03pDoo56OikueyJdNHRVzUno3rLmsq6K9mtGEW8mtbMJhDestaz07uestaz0ZTA3rPu2rPu5qzLassZhLestqy56y2pLG0JdNXTjclJdeJWvlLrxR7OmsdmGKHZipMuqFWlKuimNbFjddMTSIQxrjaxjdFcUy0jDO6dDmjH7J+XHo6vlHy06HL8uPRWaOvwKzQ0OSaKzSXVNFZoaHJ4YlS1HXanmymqo47UcWv0Gl4hw/U8P1uP5ml1WO2HLT1raNpeVtRjevSU1tNZi0eYN6fhPmTgmp5c5l4hwTV9cujzWxeL+OP3bffG0/e8Q+3/7QvAvo/HuF8w46bV1mGdPmmI/fx/szP20tEf4XxB+tcPkfxOCmX6x+vzezjt11iwA62gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmAASACNA9y5V1MX0eXS2nrit4oj2n/vH5vTXlOB6yNHxfFa07Y8n+7v9k+f47Ofk4/cxzDLLXqpMPotJ6N6uak+U+TorL5O0PMdFW1ZYUltEueRvVtVz1n3bRLC0Destqz2c9ZbVljaB0VlvSXNWW1LMLQq7Ky2pZy1s2rZzzCHTWerasw5a22hrWzGYRp01lpWzmrZrWzKYHRSzeJclbNq2YzCXVWezakuWtuzelmNoIddJduHtDx+OzuwT2ZV+8l5LDXd5TT4pnbo4dJSbTEd3s2j0NprEzEuusKyyxaf2dlMHs78ek2jZvGCIaxCHj4w+y3ynf8AJ+9E4kjh+UrOP2d04+qs0BwzRSaO21O/RS1DQ4popajrmnRnNUDkmqlq7uq1Gc1QOSa7Mclekuy9GF691ZgfK/jTweOKfC7iGStPFl4ffHrKdOsRE+G3+m8z9z8izG07P3px3h1eKcA4lw28RMavS5cO0+tqTEfns/BlomLTE946S+++G8s249sc/wAs/wB3o8W26zCoD6l2ABIAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMQbJW0KiwaEQbJE6EbEJDQ+g8E1307huO9p3yU+pf7Y8/vh5mkvnXAuI/QOIRGS22HNtW/t6S+g0t0fMc3B7eTceJebmp02dlZbVly1lrFujy5hk6ay2i0OStt2tbMbQOutoa1s5a2lrWzGYTp1Vs3raHHWzatmNoV07a2bVs46WbVswtVXTri3RrWzki3RpWzGaodcW2a1s5Is0rZlNR1xbs2rZx1s1rdlNUu2tm9J6uKt9o3mdo9Zec4Vy/wAc4xMf2dwvPnpM7fM8Php/mnaGE0mfAwx2jd5HSRfJkrjx1m97dIrWN5mfaHuvCfhXqbeHLxnX0xR3nDpvrTP22npH3RL37hfLnCeDYvBoNJXHbbrkn617fbaeqnszvZL1DgfLWprWM+up8v0x/vff6PaaaKKViIrDy/yax5HyobREwq8X9H9kTh9nk5xM7YzaHjpxeyk4+kvIWx+zK2ODY4Jxz6M7U6u61NmVqLbHFbGytTo7bUZWr5JHHarK1XXajK1Qckx6s7VdN6s5jpsgcs1c+Svd2WqwvXeJRI4bRtekzHTxRv8Ai/BfMul+g828X0Xh8MYNZmx7em15h+98lekw/D/xHxRT4o8zViOkcRzf+bd9b8M21fJX8IdvFnvL1LY2X8BMPuXftTZCyqJSAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMCY7JITs0iBAtsbJRtUT4fdO0oNqp2WivReKIR1Mdp3e68t8V+k6f6Fmt/vsUfVme96/9YeoeBpgyZdNqKZ8NvDek7xLm5GGM1OmWd4i8al9PraGtbQ8Rw3iOLX6SuWn1bx0vTzrP/T0d8ZYi0RNoj7ZfK5MU1may8+Y1OpdtbNa29TR8O4nrZiNFw3V6nft8rBe/wCkPO6fkXnbPETi5U4rMT5zprV/XZzWqibVjzLw9bNKz1ezY/hlz/eImOV9XH800r+tnXT4V/EC3/7dyV/mzY4//JhbX1R7lPq9UrPRrWdu73DD8Jef8kxE8Epjj1vqsUf/AJPL6b4Kc55Zj51+G6f+fUTb/wAtZY219VJy0+r5/Wzat4fU9L8CeLW2+l8xaPF6xiw3v+uzzml+BfD6bfTOYtVl9YxYKU/WZYWmv1V92n1fFIu0i34P0Hpfg3ydgmJzfT9XP/1NR4Y/CsQ87pPh3yRo9vl8u6W8x55vFln/AFTLGZqr7tX5mwxfNeKYqWyWnptSJtP5PYdDyfzXxCInScv629Z7WvinHWfvts/Tun02m0lIppNPi09I6RXFSKxH4N/FM953+1nM1Pdh8G4f8IuatRtbV5NHoKz5Xy/MtH3Vif1e3cO+DfDMO1+KcW1OqnzpgrGKv4zvL6bvJ4lE+48JwvkzlfhO1tHwbT/Mr2yZY+bf8bbvYI2iIiI2iOkeym5Eqrda6VN1t1dLRJsia7pSjSWfhVmsNUTVSao0wmnRlans6ZjZW1YlnMaUcVqsbUh22r7MLVREjjtVjans7b1Y2r6rRI47QwtWXXarK8eyw47VZWr7Oq1WNoBzWhz3j2ddo6sLwiRwZY79H4i+JE/M+KfM9omP/wBRzR0/m2fuK9d8lY9ZiPzfg/mzUxrudeOays7xm1+e8T6xOS2z6r4bj7eS34Q6uP5mXgPDKJq12RMPtol2xLCY2Ul0WqytHkvEtIlmJnogWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEwhaFoEwsVhaI2X2orsnw9FtkxCNo2rFd1oqtFWkV7I2pNmcVXiq+3Tq+x/Df4B8x860wcW4va/A+B32tXLkx759RX/AOnSe0f3rdPSJc+bPjw168k6hjky1pHVadQ+RaLQaziOtx6Ph+kzavU5Z2phwY5yXtPtEdX2blb/AGaeeeNVpn45k03L2mttPhzz83Pt/wDbr0if5rQ/U3J3w/5U5E0M6fl3hdcGW9fDl1WSfHnzfzXnrt7RtHs9q7Q+Y5PrdpmYwRqPrLxc3qc+MUf1l8Y5a/2cOQuBTXNrsvEOM6jba0583ysc/wCDHt0+2ZfS+Gcn8q8GrWOF8u8P0sx2tTT1m3+ad5/N5zeEeKHh5eTmyzu9tvLycnJkndrLR9WsVrO0ekdIN/vV8UG8OZj1Lbx6Lb+zPdO6JTFmsSnfbsyiVt0aaxZpErRZnumJ6KtYs13907sonZeJVaxZpEp3ZxK26GsWab9CFdzeUS0iWm6YlTdMIlpErp3V3Sq0iV4lMSpumJQ0iVxEJQ0VmFZhdEqzCJhlaN2Fqum0dWdo3hjMKS5LR1YXq67wxtG8CHHarC8Oq0bMLwvA5rwxtEum9fRhaEjmtHswvHTs6bx1YXjpIPD8Y1lOG8I1vEbzEV0unyZ5mf7tJt/R+B8kWyXtktO9rz4pn3nu/ZPxi4pHC/hbxWsX8OTXRTRU9/Hb63+mtn5Cvj69n2PoNejDa/1n+zpw9o28ZNdpV2dl8bC1NpfUxZ1RLGYZ2q3mGdo6NIlaJc0wq0tCkrw3hACUgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJiF4hWGtYWhSZTWFtlqwt0TtnMqxWForC0VWiqNqTKIq0pS171pSs2taYiIiN5mZREfc/UXwA+EWPHg0vP3M2li2W+2Thely1/Yjyz2ifOf3I8v2vOHJyuTTj45vZzZs1cVJvZ2fB/4BYeGV0/M/Pekrm1/TJpuF5Y3pp/OLZY/ev/AHe1fPee36K80bqzO74Pk8nJyL9d5fLZ+RfNbdlpmEeJVEuZyTZbdHilXf3R4oW0p1L7ybspujxyt0HU23lMXYeOfU+Yj25TFnVE7rbuSuXaW1ckW6b9Wc0mGtb7bRPVeJ82UT1XiWTesr7rRKiYVaxK+60SziVolVtEtIlKkStEjWJWhMd0ESrLWJX3WhSE7oaRK5CIlKstYleJSrCY7oaxKyJ7JPJC6kwpPZrLOe6loZywtDC0Oq8MLwyVcl46ue8dHXeHNeOi0Dmsws6bQwv3XHNdz37S6buLVZsWn0+XPnyRjw4qzfJef3axG8z90RKdTPaB+evj/wAa+kcW4Xy7iv8AV0uOdXmiP47/AFaR91Ymf8T4dej2bmnjWXmXmriPHMsTEarNNqVn9zHHSlfurEPA3p7PveLT2cVcf0dde0aeOvTpLlvR5O9PZy3p7PSpdrEvH2rsxs7MlOrmvXaXVWV4ct4ZS2tDKW0N6qgLLgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAL1bVhlVvRLKzSsLxEJpEr7SMJlXaExHktstWszMVrE2me0R3lWZU2+nfBX4dRz7zpF+IYpngfDPDm1m/SM07/AFMP+KYmZ/uxPrD9x1rXHSKUrFa1jaK1jaIj0iPKHpHwq5Mx8jfDrh/Cb44jX5q/StdbznNeImY/wxtX/D7vdp9XwvqPKnkZpiJ+zHaHzHO5HuX1HiDdXclEvNeZMm6JtsiZ2ZWtO68VUWm3kpMomzOZlvFELzdWbKTOys23axQXm3ur4/SVJlWbNIorNmvzJTGWY7Sw8XRHiW9uJV69PIY9ZtG1o3h14s1Mn7Nvu83gpsfMmJ3idtmN+JW3js0ryNeXsm6XgsfEc2PvPjj0s7cXFdPP/Ei1J/GHFfi5K/LbrpyMc/PTyMLMMeowZf8Ah5a2+yW8S5JiY7S7KzE+FoWhWEqN4XTHdELDWEwmEQlVrCYWRHdKGkJhaFYW8lWsLJ8lY7JiENIRKlu7SeillZRLKzC7oswuxUc94ct/2XVdzZOy0Ic93Nk7um7lv3XgYZJfI/jVzP8A2ZyzXl/S5P8A2vim8ZNp60wRP1v807V+yLPqPE9fpeGcO1HENbmjDpdNScmS8/u1j+vlHu/JHNXG9VzPzJq+M6qJpOa22PFv0xY46Vr90fnMvT9Pw9eT3LeI/uvWNy9VmrG1HffHtLC1H1MXbvH3o5707vJXo5707uml1ol4zJSNuzhzU2eWy17vH6iHbjttrEvGWhhLoyd2FnbV01UAXXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaVdFIYUdWMY3b0jp2abeytPVojbkmVYh9H+CvLFeaPi1wjT5sfj0mhmdfqImN4muPaaxP23mkPncRO/Z+oP9lrgtacP5j5hyU3vkyY9Djt6RWPHb87V/B5/Oze1gtaHNyMnRjtZ+jp6zMz39VLSvPZnM9Hwb5K0omVZnaEz0Z2lesMtq2mZlSZ2TadoZz3dFaoRuraxM+Sst4hEybq7+5MqTLaKs5laZ91JkmVJlpFWUyTKsyTKrWKs5smZ91JnYmWdrbb7tYqymy02Um/upMzPtCtrRDSKMpuvOT0bY+IavDt4M94j0md4/NxTbupNvdp7NbfejasZrV71nTzWPmDWU/bjHkj3jafydePmXFvtl01o962if1er2t7s7Xn1Yz6bgv5q1r6nnp/M93xcw8Nv+1ltjn+/Sf6O/FxDQ5v8Ah6vDb2i8Pms5JjzZzl39NmNvRMdvu2mHTX13JX71Yn9H1iJ36xO8esLvktNZmwzvhzXxz/ctMfo68fMnFsHbiGS0el4i36uW3oGX+S0S66fEeD/krMfr+z6hCYfPMPPPEMc7ZsWnzRHtNJ/q8lg5+0UztqdFlxx647Rf8p2lxZPReZT+Tf5PRxevcC/b3Nfm9zhLwOl5t4BqZiI4hTFaf3c0TT9ejzeHNiz18eHLTJX1paLR+Ty8vHy4u2Ssx+cPawcjDmjeK8W/KdtYSiFtmDshW3ZSV57KWUsiWdmF5b27Oa7n+bNjfs5by6Mk9dnLe0LwMLz0lyZLd/P2b5LRtL5f8R+eP7K0+TgnCc3/AIjlrtmy1n/3ekx2j+/P5R177N8dJvPTBp6b8VucP7U1k8ucNy76LS331N6z0zZY/d/lr+c/ZD5Rens8hkp1c96dH0OKIpWK1bR2eNyU9nLeryOSvdxZI6y7aW2ttx3hzZHXkhy5IdlExLhyx3eO1Ed3k8sd3jdTD0MTarxeSOrnt3dWSHLd6FXTVQBo0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbUdONzUdeNEue7oxx0axCuOOjWK9FHHaURD9o/wCzxpK6b4M6PLWNrarWanNb/PFP0o/GcV6v258CY2+CXAPt1H/+13iesW1giPxebzrf6WvxfSbM5aTDOXyUPnJVmdmM992l5nZnLekM1Lbs57NJ82cumsEqyrbdZWW8QymVVJXlSWsQylEypMrSpLWIZWlEypMplS07NqwxtKszszmfVaY26qTPq3rVjMqzPVna28rWlnLetWNpRMs5laZ6MbW3lvWrntYtbqytZMz3Y2l01o5bXLXY3ybR3VvfZy3vv5uqmNwZc2ml8077MLZLWUmZ3TEumKRDz7ZZsjrPdWVplWWkQyRMtMOoz6e/j0+a+G38WO01n8mcoWmkWjUwvW1qzus6ex6LnXj+jmItqq6rHH7ueu/5xtL2jh3xF0eWa4+I6O+mme+THPjr+Hf9XzIeXyPROHn801P1js9/ifEHqHGmOnJ1R9J7/wDb71o+J8P4jj8ei1mLPHnFLbzH2x3hvMvgOPLkxZIy4slqXjtaszEx972XhvPHGdFMU1F667FHll6W/wA0f13fLcz4WzVjq41ur8J7S+v4fxdhyfZ5NOmfrHeP3/u+p3no5sk+7wvD+b+E8SiuO2WdJnn9zN0ifst2n8nlcluj4zkcXNxr9Gas1n8X1/H5WHk168NotH4MslnHkvs2y5IfN+bOeK6et9DwTJF8/a+pjrXH/L6z79o92MOiTnrnaOCYrcO4Xet+J3j61u8aaPWY/i9I++XwrUePJkvly3tfJeZta1p3mZnvMz5vLamL3yWvktN7WmZta07zM+czLx2Wr0cOojUG3i8lHLkjaJeQy12cWWO70aSvEvH5Y7uDJHWXkc0d3Blh345WiXHkjq5skOu8d3Lkjo7aStEuLLDxupju8pkju8Zquj0MTasvFZXLd1Ze7lu9KjrqzAaNAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG+N2Y4cmN2Y0ObI7MURs3iGOLs6I7KS8+09yIfs3/Z/wBTGo+DWgxRO86bVajDPt9fxfpZ+NYh+n/9mXi0X4Fx/gVrRF8Gox6ukTP7t6+CfzpH4vG9Vr1ceZj5ODlx1Ypff56qT5r+ak95fJQ+dllbqys1tMMbT17umkKKz22Un0RkyRWtrWmK1r1m09Ij7Z8nqPFfiPydwi9sefjWPPlr0nHpInNMf5en5u7DgyZZ1Ssz+RqZ8Pbt1Z83yTWfHHhGOZjQcD1uoj+LNkpij8I8UvE3+Our/c5Zw7f3tXaf0q9WnpPKt/J/ZX2rS+2z1Vl8Vr8dc0THzOV8e3n4NXP9aPJ6T44cEyTEa7guu0289ZxXpliP/LLSfS+VX+T+yk4L/R9VlSXrHC/iHydxi1cem43hw5rdseq3w2n2+t0n8Xs/Sa1tE71t1ifKfslzWxXxzq8TDlvW1fvQpZnO0y0szmF6w5plnPVSfVe3Sdmdm9YY2lSWdu69mdpdNYc9pZ2ljae7SzKzorVy3lnaWNrL3lz3nbzdVKuHJfUMslvdzTO697TM7M57O2tdPJvbqlAIbRVQlG5KGkVSndWZN0TK0UTEEoN0NIqsbpVN/dbpF93luHcf4lw3w0xZvmYI74cnWv3ecfc8PE9ExLDPxMXIr0ZaxMfi3wcjLx7+5htNZ/B5TmHmLX8RwWwYazpdLMbXrSd5v67z6e34vQ9RWOu0bPa4lxazhmLU0m2KYx5P9M/9HwHqfwpau8vCnf8A8Z/xL7v034pi2sfN7T/7v3h6XnrHV43NHV5rXabLpss482OaW9/OPWHh8z4+tLY7dF41MPuaZa3rFqzuJeNyx3cOXzd+bu4cu3V6GNtFnBmhw5Y6S8hlcGXtL0MbSJcd4c2TpDqyT3ceWend3Y42tEuPLPd4vVT1eRzT17vGamY69XqYob0l4zL3ctnTkc1u70Ku2igC7UAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0Y3ZiceN24YRLlyO7FH1W9YZYY6N4Zy86y1X1H4HcfjgXxW4fjy5Pl6bidbaHLv23t1p/riv4vmFXRgy5cObHmw5Jx5cdovS9Z2mtoneJj7Jc2akZKTSfm5rxuNS/ol19Gduj17kXmnDznyPw7j2Oa/Oy08GppX/AJeavS8fj1j2mHVzFzFwrlnhV+I8W1PyscdKUrG98tv4ax5z+Ueb4quG85PbiNy+cyUmtpiXbqM2PBhvmy5KY8dI8Vr3tFa1j1mZ7Q+Sc1fGPRaO1tJyxipr88bxbVZYmMNP5Y6Tf7ekfa+c84c+cY5v1NqZrTpOGxbfHo8c/V9pvP79vyjyh6p4YfccD0KtIi/J7z9Pky3EPI8a5k4/zDkm3F+KZ9TTfeMU28OOv2Uj6sfg8N4I2iNm07R5qTaH1FKVpGqxqE9UyzmvqpMQva0d91JtG7VpG0bQpMLzaEbwlaFPD7dHmODc08w8v3ieE8Vz4Kb9cM28eOftpO8PE7olW9K3jVo2t57S+58r/GDQa+1dJzNipw7PvEV1OOJ+Tb+aOs0+3rH2Pp1MmPNjrlxXrkx3jxVvSYmto9YmOkw/Hr2blXnjjfKmaKabL9J0EzvfR5Z3pPrNf4J94++JeLyfS6z9rD2/BxZuJW/enaX6Zt1mWcw8Vy7zPwnmnh0azhmfe1YiM2C/TJhn0tH6T2n8nl5eL0TSem0d3i5K2pPTaGVo6Mbd21mVo6tqw5LMbMb+beejnv3dVIcd5Y3ly5Z6OmzkzdnZjh5me3ZzT3RPZaVZ7OyIeahCUNYhZWe6JSiWsQtCJRKZQ0iFkIETLSISALRVKY7J3VE9KF4tO69Z82W6Yk6UTCdRptPrdPOHU4/HWesT51n1ifKXonHOD6jhmSb9cumtO1MsR+U+kvfYtG616Y82G2HNjrkx3ja1LRvEx7vC9U9Gxc6vV4v8p/d7XpXrGb0+2vNJ8x+z43mnq4Ms93t/M3Ld+Gb63SeLJobTtO/W2GZ8p9vSfxem5Z7vzfLxMvGyTiyxqYfq3E5ePlY4y4p3EubLLhzS6sk7uLLLfHV3RZx5Z7uPJPR1ZZ7uHLL1MVWsS5c0vGame7yOXzeN1Hm9LHDpx+Xjsjnt3dGTzc9u7rq76KALtQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG+J34XDi8nkMKJcmWXfhjo3iGWGPqtoZy8y3lasNIUhpSJtaK1jeZnaI9WetsZfWPgx8Qp5N4zrtFr6Zs/CdbinJbHijeaZqx9W0em8fVn7YnyU5l5l4pzVxvJxPieXef2cWKs/Uw08q1j9Z856y9c4doq6DSRSY/31ut59/R0TZ7PD4GPDPvTH2pfP8AJyxkvPT4T0Vtbopa+zG952ejpzVrta+T3Y2v7qWt7spt17piHTWjSbI8TLeUbylp0tfEnxMd59TeRPS3i3undjEzstFvcVmGiERO6yVXbwni/EeB8TxcR4ZqLYNRj6RMdrR51tHnE+cS/R3KXNug5t4T9I0+2HWYoiNTppnrjmfOPWsz2n7p6vzH3eQ4NxjX8B4th4nw3NOLPinz/ZvXzraPOs+cOLlcWuaNx5YZ8Fc1dfN+qrQyt3eM5c5i0PNHBMfEdF9S2/gzYJnecN/OJ9Y84nzj73lbR1fP9M1npny+Xy0mlum3lz27ML93TeHPeHRRwZHNaHJm7O28OLP3duPy8nk+HOiVlXZDgRKq0oltEJURKZ7q+basLwSrKVZaxC0EygRMtIhbRMo3kRutpKd5TCu6VtCyVd0waRpaJXhnErbo0rMNfqXpNL1i9LRMWraN4tE94mPN8q5w5dtwbU/StJW08OzTtSe/yrfwT7ek/d3h9SiUajT4NbpMuj1eKM2DNXw3pPnH9J84nyl5PqPp1OZj1P3o8S9b0r1O/Azb80nzH+fzfnzJbu48k93sHM/A9Ry/xa2kyWtkw3jx4Msx/wASm/6x2n3+2HrWS3fq+C9i2O01tGph+tYc9ctIvSdxLmzT7uHLPu6sk93Fll2Y6O2ltubLPu8bnnq7ss93j88u2lXdjcWSXPZtknqws6IejRUBZoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA6cTvwuDE78KsuPK8jin6raOzDF+y3qo8y3leOzz/AC/ovmZrazJXemKdq9O9v+zwVImfqxE7z0e96bBXR6DFp4jrWPre8+bs4WH3Mm58Q8zm5ejHqPMrXt1lhay156ywtPu+gl41aotZjaybTLK0zuo6K1RMqzMEyrMobRCZn3V36omUboX0vujeVdzcTpeLdFollv7rbisw2iV6yxie3VeJ2WZzDU2RErJZvYOUeZtXytxymuw+LJp77U1GCJ2+bj3/AFjvE+v2y/SGk1el4jocOu0OaM2mz0jJjvHnE/8ArafeH5Qh9K+GHN39l8QjgPEcu2h1d/8Ac2tPTDln9K27e07T5y87mcfqj3K+YedzeP7teqvmH2a0MLw7L02md/JzXjZ5NHyuSrlvHRw546PI2hyZq7xLtxy8rk13Dh8lZaWjZSYd9XlKqytKJhtVaFJVleVJ7t6w0hSUSmVZ7tohaEITKsy1iq8EoJlG68VWTuboFtC0J3ViQ6UNNzdWJTEo6USvErxaWcJiVZhSYeO5k4Fi5j4Hk0NprTUV+vpsk/uZP+k9p+6fJ+fdViy6fUZdPnx2x5cVppelo2mtonaYl+lon1fL/ijy/wCG+LmPS0+rkmMWqiPK231b/fttPvEer5v1XhxaPfrHePL7H4b9Qmtv4TJPafH7PlWSe7iyOzJ5uPJ2eFWr9HxuLK4M7uzODNPV01h6mJxZGEtsndg0ejXwAC4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADpxO7C4cTvwoceV5DF+y3r3YYv2XRVSXm28vKcF0/wBI4tgrMb1pPjt9kdXt+a2+7wXLGOPm6nPPetYrH3z/ANnmss9e73eBTpxdX1fN823Vm19HPee7G0tLyxtLtllWFLT0ZTPVe0s5lSXRWETPdTcme6sz7oaRBujdXdEz1Qvpbc3V3N0J0vundnumJ9wmGsT2aRLCJ92lZ91oZzDorLWOznpPu6Krwwt2F69zb2WiPZZnt+gPh9zVXmLgkaLV5d+J6KkVyeKeuakdIyfpE+/Xze25KPzHwfims4NxXBxHQZZx6jDbes+U+tZjziY6S/RvAOO6LmTguPiWk+rM/VzYpnecN/Os/rE+cPD5WCcduqviXz/O42p66+G9quXLV5C9Npc2WnTsyx2fPZse4eKyV2ndjLuy4+7kvXaXo4528PJTpllMIWmES6qs4ZzHdSWkqWdFWkM5VlaVZdFYaQqrKZV3b1qvAjclVfS+kpiVNzdOjS+6YnopEp3TpGl07qRKUTCNLxK8MoleJ91ZhWWkd2Wu0WDifDNVw7U7fJ1OO2K0zG+2/afunafuXifdes9WF6Ras1n5lL2x3i9e0x3fmHiWiz8O4jqdBqq+HPp8lsd494nZ4vJPR9T+LXCPkcU0vG8Vdqayvysu3/zKR0n767f5ZfLMnWHxuTDOK80n5P2zgcivJwUzV+cf+XFl83j8/d5DL3ePzd0xD3cThyd2LbIxRL0q+ABCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADpxO/D3cGJ24vJDkyvJYuzojs5cP7LprPRWXmX8vbuW424Xmv52y7fhH/d5DJ2cXL8bcF39clv6Ou8vouNGsNXy/I757MbsbNLebK0tpTWGUs5leZ2ZW9VHRWETPRSSZVmUNYglVEyjdDTSdzfZTeDeEbTpfxQmJZ+KE7mzTXxNIlzxLSJWhSYdVJdePrDgpPZ5DBG9N2lXJljS+y2ydkxEtNOfZD2blHmXUcs8Zrq6VnLpsn1NRhidvHT1j+9HeP+71uIaV7qWrF46ZZXiLRqX6i0uq0vEdDh1+izVzafNXx0vHnH9JjzjyL03h8S5J5wy8uav6NqfFl4ZntvlpHWcc/x1/rHn9r7ljyYdTp8eo0+WmbDlrF6ZKTvW1Z84eFmw2wW1Ph85yuN0T28PH5Mfs4s2LpLzGTH3mIcmXHvv0aY7vCzYdvDzXadpUmHbmw9fdyzE9pelS23j2rNZ1LGfNnLW0SymHXVarOeykytMKTLrpDaFZlSZ6FrxDG1/d0xGmsQvNuqvihnN0eIaRVr4vJO+zHxJiZE9LWJTuz3hMSK6axMrbst4WiRXTSFoZwtEoVmGkSvHZnErRKkwzmHr3PnDP7V5H4hhpXxZcFY1WP7adZ/Gs2fnHJ5v1jtS8TXJETS0bWifOJ6TH4PyzxjQ24ZxnW8Ovvvps98XX0rMxH5bPnvUcWrxePm/R/hLkdeG+Cf5Z3/APf/AIeHy+bhzd3fk7uPNHR5un6Hjl47JDGe7fJ3YT3Zy9GvhACi4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADoxu3F5OHG7cUjlyPI4ezorLmwz0b1naUS828d3uvAZ/8ABK7eWS39HVklwcvW34PMfw5bR+UO7I+h4/8AtVfLZ41mt+bC092NpaXnuxtLSV6wztPRnaVp6srT1UlvWFZlWZ90zPkzmeqG0QTPujf3VmUbqtIhO6N/dG6u6FtL7ni91NzcNNYsvWzCLLRZMSrMOqtnldJ9bDv36vCRbq8xwy3irevp1a0nu5M9fs7dkV3Ts0iEbOh5u1YheI2kiFohGlZlpWdnvXJXOmTgF/oGui2bhmS/imI62wzPe1Y849Y++Ovf0WsNaTtKt8dclemznvWLRqX6cw5MGr02PVaXNTNgyx4qZKTvFo9WWTHPk+Ictc18R5dzzGnmM2kvO+TTZJ+rb3j+G3vH37vsHBeZeD8wYojSZ4x6jbe2myzEZI+z+KPeHi5ePfDO47w8bPxdd4aZcW7x+bF193nsmGevRxZsPfo0xZXhZ+Pt4S0d4mGNoeRzYZ6zEPE6nWaXBvF89ZtH7tZ3l62Kerw8uMV96iEWhyZs1a9N+rl1HE5yTtir4K+s95cU5pnzelSNO7Hx582dls26k5HLGRPiX26Pb06PGnxMIst4g6W0WTFmMWheLCsw1jZaLeTLdaJFJhrE+68T7solaJTtSYaxK8MoleJQzmGkLM4leOwpLWvZ+ffifpPovxA19o7aiuPPH+Kkb/nEv0DE+T4t8YsPh5m0Gfb/AIujiJn1mt7R+kw8n1Cu8cT+L6v4UydPNtX61n9Jh8syQ487vyR0lw5vR4fS/Wsfl4/I557ujJ3c892FoenTwgBmuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA2x+TsxS46OnGlz5IeRxW2hvEy5MVumzes7QaefaO73Hlm/i4fqKb9a5In8Y/7PKZPN4DlbLHzdVh9aVtH3T/3eeyvc4s7xQ+Z5denkS5rsbS1uws2lWrO09WUz1XtLK0qS6Kwi091JktPRSZ90NogmVZlEz7qzKrSIJlG6sz7o390L6WmZ3Rv6K7niNp00iVosx8SdxE1dG7yfCMu2sik/vxs8PFm2DNOLPTJXvW0StWdSxyY+qs1e4+FGzWnhyY65K/s2iJiU+F3R3fOb12Y+FaIabGxo2iIXiERVbZKky1pLqxZJraJiZiY6xPo5KtqrOe0Pb9HztzFp6RT+0bZqx02z1jJP4zG/wCbstzpxzLG1tVSv8mKsf0el0ts6aXVjDj3vphxZMcS8/n4xrtZG2p1eXLHpa3T8OzGMrxtbN6XdFdR4hyWxw7YyLxZzVs0i7TbCauiLLxZzxZaJSzmroiy0Swiy8WSzmG0SvEsYnt1XiU7UmG0StEson3XiRnMNYleGUSvEpZTDWJ6L1ZRMtKyM5aQ0r2ZRMtKyM5aR3fIvjLH/iPBrf8A8fJH+uH12HyD4x5N+LcIw+ddNe345J/6ODmx/pvovhj/ANQj8pfKMnZwZ3kMnZwah4c17P2HF5eOyd3NPd05O7nt3cl3p08KgMGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADWjqxuWjoomGF3Zj7Q2iejnxz0jq1iY9VnHMPPctZvl8apWZ6ZKWp+W/wDR7bl9HoHDtR9G4lp8/lTJEz9m/V7/AJo2mev3vU4dvszD571GmslbfWHHee7C0tr92FnVLlrDO0srL2ZWlV01hWzOZ6rWlnMqy2iETKkyTKsz7oaxBMqzKJlEyhpEJ3Rurv7o3QnTTxG7PxSRIabxZaLdpYRK8SlWYe5cB1EZ9B8qZ3vhnbr6eTys1em8E1v0TiVPFO2PJ9S3tv2n8XvEx7O3FbdXzPOxe3l38pYeE8Ps28KPC204epltO60R5rbdU7BsiPNpCIj2XiPZMM5levdtWWVYbVWhhZtSW9Jc9Wtei7ntDprbo0ifdz1mGtVolzzDaJlpEywifdpWfWVmUw3rPReJ6sYlpCWUw1hpE+bGstIlZlMNYXiWcL17jKYaRK8M4aVSylrHZevkyhpVLKWsL17s47Na9xjLWvZ8P+LeojLzniwxO/0fR46zHpMza39YfcKxMxtHeez85c9a2Nfz1xjPWd6VzzirO/lSIp/Rw8z7sQ+t+E8XVyr5PpH95eq5JcOd25HFmeTaOz9VxeXBkc1nTkc13n5Hp0UAczUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABpWXRSXNWW1ZWhlaHXSejTxOelmkTKzmmG0TL6Jpc8arhmnzxPW1I3+2Okvm8W6vceWtR83hmTTzPXDfePsn/vDr4ltX19Xk+o494ur6PJ5O8uezoyebmtL0pePTwyt2ZWaW7MbKS6awpafJnMrzLOZ6obRCsqTPWU2U3VbQiZVmSZVmUbXiEzKu6sz1RM+qNrxDTc3Zbm6Np02iV4nyc8W6tK2TtWYbx06w9/4JrY1/DKWtO+XH9S/2+U/e+exLy/AOI/QeJ1jJbbBm2pf29JbYr9Nu7zebg97FOvMPfvCrNfRt4YR4Xow+R2x8J4Ws16IiJE7Viq9a9YTELRArMlY6tIjZER13XiOq0MplevdpClV47pYy1q0iejKOrSOyzKWsd2kMq9l4WYy2js0iWUdmkdkspaRPm0iWUS1r2WYy0ieq8eTOGle0JZSvE9Wte7KGte6WMrw0r2ZxDSEspaR2a1Z17NqwljZjxHW4+F8I1nEsn7Glw2zffEdI++doflvNe+TJfJkt4r3mbWn1mes/m+4fFXiv0PlbBwzHbbJxDL9b/wC3TaZ/G01/CXw20PM5M9V9fR+l/C/G9riTlnzef0jt+7nvDizw779pcWfs47V7PtscvHZO7lv3dWXu5bvLyw9OigDkbAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALRK9ZZLRK0KzDppbs1i3Ry1mWsS00ymroifd5vlvV/I4tGK0/Vz1mn394/R6/EtsOW2LLTJSdrVmLRPvC1J6bRLmy44vSaT830bL5uWzojLXU6bHqKfs5KxePvc93sb33h8pWJjtLG0sbS1sysrLpqytPRnaV7dmcqy3qpM9FLT1Wnszsq2iETKkyTPVSZVlrEJmeqsz7omVd0LxC3iR4vdXdEyrtbS8WXrZhvsmLJ2TV2VtK8T17uat20TuvE7YTV9E5b4nHEOH/ACslt8+D6tt/3q+U/wBHnJq+W8M4hk4bxDHqqdYr0vX+KvnD6jhy49RgpnxW8WPJWLVmPOJehgydUany+Q9T43s5Ouvif7nhPC02g2dGnk7Z7LRCdkxBCJkiF4giFtkqTKYheIVjyXiOqWcrxC8dlYXjssylevZeFKtIjpCYZS0js0jszjs0josyleNtujWvZnWPJpCWMtKr1Uq0qtDKV4jq0qpXyaRGyYYyvXs1iOqkQ0pCWMyvWHRjrMzFYjeZnaGVYeuc+ce/sDlXJGC/h1uu30+HaetY2+vf7onaPe0K2t01204vGty89cNPMvk/PvHK8d5t1ObDfxaTTf8As+CY7TWs9bffbefweoWbX6do2Y2eZPfvL9owYq4sdcdPERpjdxZ3ZeXFnUtHZ6GPy8flct3Vl7ua7x8z06MwHE2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEwgWgXiWkSyhbf3bRKsw2391q2Yb+69Z22lOlJq925b1fzuH5NJafrYZ3r/ACz/AN/1eTyR1el8F1v0PimHJadqWnwX+yXu2Wu1piXfgtuuvo+Z5uL283VHiXJdlZtfuxs2Y1ZWZS0sylSW9Wdmcr2nqytKrorCtpUmU2nozmfdVrEEyrvBMqTKsy0iEzKN0TPTurM+6q+lvFKYszmyN5Np06K3bUu4ots1pf3TEs7Udvi83t/J/GYpljhOov8AUvO+GbeVv4fv8vd6VW268XtW0Wrbw2id4mPJtW81ncOLkceufHOO3zfbduiJq8Py3xmOM8Miclo+lYfq5Y9fS32T+rzmz1a2i0bh+fZsVsGScd/MMZhMQ0mEbdV2WyITEGy8R7JVmSsdl4REey0QM5laF4hWI9l4hZnMrRC8eSIhesJZStHZpXspENax0TDKZWjylpCsRGy9YWhjLSvResdVYhrWFoZWlasNIhWsNIhZhMrxDWkK1q6KVmZ7b/YMLSWvhwYcmoz5a4sGKs5MmS3SKViN5mX5+5u5hycycfy63aaaWkfK02Oe9Mcdt/ee8+8+z3D4l81/MyW5Z4flj5WOYnWZKT+3eOsY9/SvefWfsfLrWceS3XOvk/RvQPTP4bH7+SPt2/SGV3PZtafdjZjp9fWGN3Hmdl3HnZ3js68flwZPNy3dWVy3eNnenRmA4WwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACYSiEtIkFomVReJQ2pbZ79wnWTruFY8lp3y0j5d/tjtP3xs+exO2zz3Lmu+jcRjBe3+7z/AFZ9Inyn+n3unFbps87nYPcxTMeY7vaLuezryxtO23Vy3h3S+foxsxs3swso6asrT1ZWlpZlZWXRVnad2c9l7ebOZUbxCsz1VmUzKm6jSIJnorMkyrM+6GkQbomZ3V390TPXuLaW8Ur1uxm33kWQmau2l20WcFb+7et/deJYWo8vwniuo4RxLHq8HWI6XpvtGSvnE/8Aru+waLV4NfosOs01/Hhy18VZ/WJ947Phfi6PZuUeZP7H1s6XVXn6Bnn60z/yrfxfZ6/j5OnBl6LanxLwvVfT/wCJx+5jj7UfrH0/Z9X8J4YXiI23jaYmN4mOu54Xr9nwMzrspstEStFVogVmVdlohMR7LRWfQVmSIWiCI9l4j2SzmSsNKwRGy0R6JZzKaw1rG0IrHs0rHssxmSIa1jp3REezSsey0MbSmsNawiKxu1rXqsxtKaw1rX2K1b48czO0RulzzJSr1HnnnGvL+mvwvh2SJ4tmr9a9ev0Ws+f88+UeXf0a85c6YOW8d+H8Pmubi9o2nfrXSxPnb1t6V8u8+k/D82bLnzXzZslsmXJabXvad5tM95mfOXPkvvtD7D0T0WbTHJ5MdvlH+ZZ2tO8zO+8+csbStaWNpYPv6wraerOZ7ptPVna0odFYVtLjzebotZzZZZ38OjHHdw5O7lu6cjmu8XO9KjMBwNgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABO6AExKVUxK0SLQtW01tExO0+ykLOisomHv/D9ZGv4biz7x8yI8OSP70f9e614er8v6+NJrvk5LbYc/wBWd+0T5T/T73tmWsxM9HoY7dVXzHJw+zlmPlPhyWYW7Oi7C60q0YWY27NrebCzOXVVnLKzS3myspLoqrMqTKZUmVZaxBMqTJMqTKGkQTMqzZEyrMjSIW8SPEpNoVm0qrabRfZtW7j8S0X2WhWabd8XLWc1ci03Sy6NPpnInNUWnFwDiOXaf2dLlvP/APXP9Pw9H0fbr2fmr5kxMTE9Y9H2Pkbm+ONaevDOIZf/ABLFH1bT/wDEVjz/AJo8/Xv6u/jZ/wCSz471z0mY3ysEfnH+f3e5bQnZbaUxD0nxG1YheITEJiEqzKIjqvWJ2IrG+7SITCkyVhpEbER5tIjeEsZsVqvFeia16tKx0XiGUyRVrFStWtaLaYWsVru2rVfHhtby6MOKcV4Ty/po1HF9VGKbRvjwVjxZMn8tf6ztHuibRXyY8OTPaKY43Luw4Jv17RHXf0eg82/EXFo6X4ZyzljJn/Zya6OsUn0x+s/3u3p6vVuZ+e+JcwRbSYInQ8Nmf+BS31skf37ef2dvtenXlha82/J9t6b6HTDMZc/e30+UK5L3vkte9pva0zNptO8zM95mWF56LWllae6mn11YUtLK0rWllaVZb1hW1urG1lrWY2spLorCtpc+WWtpYZOylvDppDkv3c9295c9ni53dRQBwNQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFkoI7tqoleJ2e78I1v0/h0Tad82Lal/f0n73o7yHCtb9B19ctt/lW+rkiP4f8A11deO3TLj5eD3ceo8x4e25I2c13dlito8VZi1Z6xMebjyR0l1y8Ck/JzW83Pd0W83PdSXZVlZlZpbzZWZumrOZZzK9uzOVZbwrMqzPuWnqpMoaxCJt7qTPuTKsz5oaRCZlWZRuhDTSdzxSrubo2nTSLrRkY7m51KzVr45nzaYdTl0+ox58GW2LLjtFq3pO01mO0w5tzc6jpjw+98l844eZdL9G1U1x8Uw13vSOkZo/jrH6x5d+3b2+I9n5c0ur1Gi1WPVaXNbDnxWi1L0naazHnD73ybzhpuZtFGHLNcXFMNf99ijpGSP46+3rHl9j1eNyer7FvL869d9EnBM8njx9n5x9P+v7Paoj2WiqYqtEdXoviplXwtKx1Wiu7WuNZlNlYhrWq1cctq41oYWuzis7tq0bY9Ne+/hrM7fk8ZxDmblzg28aziVMuav/I00fNvv93SPvkm0R5XxYM2eenFWZeUpim07RBrtXw3g2mjU8X1uLS0mN6xefrW/lr3n7ofNuM/E7iGoicHA9NHDsXnlttky2/Lav3b/a9D1Oq1Or1FtRqtRkz5r9bZMl5tafvlnOSZ8PouL8PTOrcif6Q+i8c+KGS1b6flzTTp6dvpWesTef5a9q/fvL5zqdVqNXqL6nVZ8mfNed7ZMlpta32zLCZUmZU/N9Zx+Li49enFXS/iUtbdSbQpNkbdkVTM+7K0+5azG1kbbVqm0sLym12NrK7dFaq2ljZeZ82czuq6KwrMsMs92tp2c+SWd/DesOe8uezazGzxs7sqqA4GgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACUwJShLeqJFolVMNYQ9p4Dr/nYJ0WWfr443xz619PueRy123elYM18GembHbw3pO8S90w6jHrdJTUY+nijrX+GfOHVjtuNPE5mHov7lfEuTJDnvDryV2ct4WlnSdue3mxs3uwsyddWVmVvNpaWNpQ6KqTKkym09VJlDaIVlG5MoVlrEG6qUSzmUhujcUmyU7m6BSbGk7oRubq9ZpMS6NJrNTodZi1ekzXw58VvFTJSdprLm3Ik65JiJjUv0DyTzzpeZcNdFrJpp+LVj/hx0rn9Zp7+tfwe9Vo/I+LLkw5aZcWS2O9Ji1bVnaaz6xMdn0PhvxF4/q8ddLreNZsWbtGSsxWL/bMRG0+/m9njc/eqZPL4D1X4Y67+7xZ1E+Y+n5Pv9NPe0bxS0/cx1Gu4Xoa76ziWk0/tkzV3/COr4fqeI8R1MzGq1+pze2TLa36y4+kdtoen7s/KHi4/h6v/Jkn+kPser575Y0m8Y9Rn1to/wDkYto/G2z1/W/E/UzE14XwrBp48sme05bfhG0fq+dzb3Vmys3tPzenh9H4mLv07n8e7zfEuZ+O8W3rr+J58mOf+XWfBT/LXaHh/F02hlN1fGjb1644rGqxqG/j90TaPNh4/c8a3Uv0NJt0UtZnNo2VmyNrxVabKWspN2drq7axVNrsrXUvf3Y2uiZdFaLWuzm3VWZ381ZmN0dTeKpmVLTKs2UtaFZs1iqbT0YZJ6rWn0Y3ndlaezasM7Sys0szl5OaXRCoDiXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEx2QmOyYEpQlvWQTCEw0hCXk+Ea/wCh6iaZJn5GTpaP4fd4xMNazpnekXrNbPdc1fOI6S4r1mN2XCNbGbBGjyz9ekfUn+KPT7nVlrtLo8xt4c1nHbolw3c9u7qyRPVzXUdVJc9mNvNrdjbzVdVWdpZzO61u7NR0VhEoTKGcyuboJGMysIEM5kTugFdgAgAAExOyAHm+HcczaeK4NTvlwx0if3qR/V7DTPjzYoyYskXpbtMPQ3Zotdl0eXxVnek/tV8pd+Dl2p9m/h5+fh1v9qnaXuE391Ju5sepx58VcuKd6z+XsmcnR7MXiY3DyvbmJ1Lab9VZv7sJurNza0UdHjRORz+P3RNzqWijacnurOTr3c83Um/U6mkUbzfv1Z2uym6k3V6mkUWtdnNvcmWdpRtrELTZS1uvdWbKTPVG2sQnxKzburMqzKu2kQWszmUzspLO09msQrZnK8qT2eZlaQgByLAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACY7ITHZMCSO4NYEhHYawhbyEb9CGkShriyWxZK3pO1qzvEx5S9n02prrdN8yOl46Xr6T6vVHVotXfS6iMlete1o9YbVnTlz4fcr28vOZa93Hkh5C00yYoyY58VbRvDjy1laXBjn5S4ruezpvDnuq7qMLKL2Z9mcumDdEyInuwtK4jc3QwmUgCgAAAAAAAAAA69Hq7abL1647ftQ85GSJrvWd4ntL1l5HQ6iZxzitPWOsfY7+Lmms9EuTPi6vtQ8nN1Zye7Cb9VfG9LqckUdHzFZv7sPF7nijzOpPQ1mys2Zzb3Um3uja8VaTZWbM5tCs290baRVrNlZsym3uibe5taKtJlSZ6qzb3Um3U2vELTbopNkTKFZlpEJ3VlKJUtPZKsqStKsvOySvCAHMkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASgTAsA0EiEw0iUCYQLwlYhESlpEqvI8O1vybfKyTvit/pl5LNXr7PXYeU0Wr8VY0+Wesfsy2rPycWbF366pyV69nJkjrLyGakxMuLJHclGOXJdnLSzOWNnbCESmVZ7Oa8rQgBgkAAAAAAAAAAAAXxXnHki0T2UExOp2eXlPHvHdHjc2O/1I9k+N7Fb7jbl6G/j9zx+7DxnjW2dLabqzaWXi90Tb3RtaKrzaVZspvv5o3lHUt0r+JHilXc3R1raTubq7iOs0nc3QK9SU7okRKJt2ESrKZRLivK0IAYJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEwLALQAC0CRG6WsSgTEoFxZMTtO6sSlpEo08rptT8/H8vJP14jv6qZavHVtNbRas7THZ5DHmjPTr0vHePVpFt9nLfH0zuPDkyQwnu68tXLMdWdobUnsrKs91pVnu48jWEAMkgAAAAAAAAAAAAANKT9VbdSqzux2+zCsgI3X6kaTuI3N0dRpIjc3R1J0kRubo2JEbm5sSI3NzYlEm6JRMiJlE90queyQBkkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMJVWWgAFokEwgXiUJAagndAkTutW01tFonaYUSnaHdGSuem/a0d4cuSsxKtbzWd4naW02jLXeP2vOGm+qGUV6Z7OaVZXmNlZcmSG0KgMEgAAAAAAAAAAAAALRPRO6id2kX0Lbm6qVuoSIF9oTuboRupNkrbm6u5ujrFtzdAt1CdxAtEoSSbiZkQqsqxskAZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAndACwiJSvEgAsBuC20aSIFosJDcWiQTEzHZAnaF5mJjfzUmEolFtWghWULTHVVyzGlgBAAAAAAAAAAAAAAAJ3QAsKp36LdQTKARsAECYSqlaJEgNNgAbRpEoBnMpAFQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATEoAWERKWkSABAAJ2ACdgAbABGwRKUSrM7EAKAAAAAAAAAAAAAAAAAAAAAAAACYN0CdidxAnYAIABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAJ2Cd0BsTuboE7E7m6A2J3QCNgAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAf/9k="

class _MenuMsg:
    """Adapter so start_handler can be re-used from a button press."""
    def __init__(self, client, user, chat_id, text):
        self._c, self.from_user, self.text = client, user, text
        self.chat = type("C", (), {"id": chat_id})()
        self.chat_id = chat_id
    async def reply_text(self, text, **kw):
        return await self._c.send_message(self.chat_id, text, **kw)

def _menu_buttons(styled=True):
    def b(text, style, **kw):
        d = {"text": text, **kw}
        if styled:
            d["style"] = style
        return d
    rows = [
        [b("🤖 مدیریت سلف", "success", callback_data="mm:self")],
        [b("📖 راهنما", "primary", callback_data="mm:help"), b("👤 حساب کاربری", "primary", callback_data="mm:acct")],
    ]
    if styled and MENU_MINIAPP_URL.startswith("https://"):
        rows.append([b("🚀 مینی‌اپ سلف", "success", web_app={"url": MENU_MINIAPP_URL})])
    links = []
    if MENU_CHANNEL_URL.startswith("http"):
        links.append(b("📣 کانال", "danger", url=MENU_CHANNEL_URL))
    if MENU_SUPPORT_URL.startswith("http"):
        links.append(b("💬 پشتیبانی", "danger", url=MENU_SUPPORT_URL))
    if links:
        rows.append(links)
    rows.append([b("❓ سلف چیه؟", "danger", callback_data="mm:about")])
    return rows

async def send_main_menu(chat_id):
    """Photo + coloured inline buttons via the Bot API. Falls back to a plain Pyrogram menu."""
    global _MENU_PHOTO_FILE_ID
    try:
        img = base64.b64decode(_MENU_IMG_B64)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        markup = json.dumps({"inline_keyboard": _menu_buttons(True)}, ensure_ascii=False)
        async with aiohttp.ClientSession() as sess:
            for _ in range(2):
                form = aiohttp.FormData()
                form.add_field("chat_id", str(chat_id))
                form.add_field("caption", _MENU_CAPTION)
                form.add_field("parse_mode", "HTML")
                form.add_field("reply_markup", markup)
                if _MENU_PHOTO_FILE_ID:
                    form.add_field("photo", _MENU_PHOTO_FILE_ID)
                else:
                    form.add_field("photo", img, filename="menu.jpg", content_type="image/jpeg")
                async with sess.post(url, data=form, timeout=aiohttp.ClientTimeout(total=25)) as r:
                    j = await r.json(content_type=None)
                if j.get("ok"):
                    try:
                        _MENU_PHOTO_FILE_ID = j["result"]["photo"][-1]["file_id"]
                    except Exception:
                        pass
                    try:
                        _pu = _miniapp_public_url()
                        if _pu:
                            asyncio.create_task(_set_menu_button(_pu, chat_id))
                    except Exception:
                        pass
                    return True
                if _MENU_PHOTO_FILE_ID:
                    _MENU_PHOTO_FILE_ID = None   # stale file_id -> re-upload once
                    continue
                logger.warning(f"main menu sendPhoto failed: {str(j)[:200]}")
                break
    except Exception as e:
        logger.warning(f"main menu Bot API error: {e}")
    try:   # fallback without button colours / web_app
        rows = [[InlineKeyboardButton(x["text"], callback_data=x.get("callback_data"), url=x.get("url")) for x in row] for row in _menu_buttons(False)]
        bio = io.BytesIO(base64.b64decode(_MENU_IMG_B64)); bio.name = "menu.jpg"
        await manager_bot.send_photo(chat_id, bio, caption=re.sub(r"</?b>", "**", _MENU_CAPTION), reply_markup=InlineKeyboardMarkup(rows))
        return True
    except Exception as e:
        logger.warning(f"main menu fallback failed: {e}")
        return False

async def main_menu_callback(client, callback):
    act = (callback.data or "").split(":", 1)[-1]
    user = callback.from_user
    chat_id = callback.message.chat.id if callback.message else user.id
    try:
        await callback.answer()
    except Exception:
        pass
    if act == "self":
        return await start_handler(client, _MenuMsg(client, user, chat_id, "فعال‌سازی سلف"))
    if act == "help":
        txt = ("📖 **راهنمای سریع**\n\n"
               "بعد از فعال‌سازی، این دستورها را در تلگرام خودت بنویس:\n"
               "• `پنل` — پنل کنترل سلف\n• `راهنما` — مرکز راهنمای کامل\n• `ping` — تست سرعت\n"
               "• `ساعت` / `تاریخ` — زمان و تاریخ\n• `ترجمه` — ریپلای روی یک پیام\n• `هوش سوال` — هوش مصنوعی\n• `نرخ` — نرخ ارز و طلا\n\n"
               "همه‌ی دستورها در مینی‌اپ هم هست 🚀")
        return await client.send_message(chat_id, txt)
    if act == "acct":
        ud = data_manager.data.get("users", {}).get(str(user.id), {})
        phone = str(ud.get("phone") or "")
        phone_txt = ("•••• " + phone[-4:]) if len(phone) >= 4 else "ثبت نشده"
        if user.id in ACTIVE_BOTS:
            st = "🟢 فعال و متصل"
        elif ud.get("session_string"):
            st = "🟡 ثبت‌شده، در حال اتصال یا غیرفعال"
        else:
            st = "🔴 فعال نشده"
        return await client.send_message(chat_id, f"👤 **حساب کاربری**\n\n🆔 آیدی: `{user.id}`\n📱 شماره: {phone_txt}\n⚙️ وضعیت سلف: {st}")
    if act == "about":
        return await client.send_message(chat_id, "❓ **سلف چیه؟**\n\nسلف یک دستیار هوشمند روی حساب تلگرام خودته: ابزارهای گروه، ترجمه، جستجو، هوش مصنوعی، آمار، ساعت و پروفایل و ده‌ها قابلیت دیگر، فقط با نوشتن چند کلمه.\n\nبرای شروع «🤖 مدیریت سلف» را بزن.")

@manager_bot.on_message(filters.private & (filters.command(["panel", "help", "menu"]) | filters.regex(r"^(پنل|راهنما|منو)$")), group=-15)
async def menu_cmd_handler(client, message):
    if not message.from_user:
        return
    await send_main_menu(message.chat.id)
    message.stop_propagation()
# =====================================================================

@manager_bot .on_message ((filters .command ("start")|filters .regex ("فعال‌سازی سلف"))&filters .private )
async def start_handler (client ,message ):
    if not message .from_user :return 
    uid =message .from_user .id
    if (message .text or "").startswith ("/start"):
        _menu_ok =await send_main_menu (message .chat .id )
        if _menu_ok and uid not in data_manager .get_admins ():
            return 

    if uid in data_manager .get_admins ()and (message .text =="/start"or message .text =="فعال‌سازی سلف"):
        kb =get_admin_menu_keyboard (uid )
        if message .text =="/start":
            return await message .reply_text ("**خوش اومدی به پنل مدیریت DARKSELF.**",reply_markup =kb )

    if not data_manager .data .get ("global_bot_status",True ):
        return await message .reply_text ("**سلف‌ها موقتاً توسط مدیریت خاموش شدن.** لطفاً صبر کن.")

    user_data =data_manager .data ["users"].get (str (uid ),{})
    has_session =bool (user_data .get ("session_string"))
    is_running =uid in ACTIVE_BOTS 

    if not has_session and not data_manager .self_slot_available (uid ):
        return await message .reply_text (self_capacity_full_text (),reply_markup =ReplyKeyboardRemove ())

    if has_session :
        kb_rows =[[KeyboardButton ("فعال‌سازی سلف"),KeyboardButton ("ورود مجدد (ریست)")]]
        kb_user =ReplyKeyboardMarkup (kb_rows ,resize_keyboard =True )
        wait_left =_activation_wait_left (uid )
        if wait_left >0 :
            await message .reply_text (f"**فعال‌سازی در انتظار است.**\n\nاز انتظار ثابت ۲ دقیقه‌ای، {math .ceil (wait_left )} ثانیه باقی مانده است.\nبعد از اتصال، پیام آماده‌بودن و دستور استفاده ارسال می‌شود.",reply_markup =kb_user )
            phone =user_data .get ("phone")
            s_str =_db_decrypt (user_data .get ("session_string",""))
            if phone and s_str :asyncio .create_task (start_bot_instance (s_str ,phone ,uid ,'stylized'))
            return 
        if is_running :
            await message .reply_text ("**سلف فعال و متصله.**\n\nبرای استفاده دستور `پنل` یا `راهنما` رو تو تلگرامت بزن.",reply_markup =kb_user )
        else :
            phone =user_data .get ("phone")
            s_str =_db_decrypt (user_data .get ("session_string",""))
            if phone and s_str :
                await message .reply_text ("**سلفت موقتاً غیرفعال بود، داره وصل می‌شه...**\n\nاگه وصل نشد دکمه «ورود مجدد (ریست)» رو بزن.",reply_markup =kb_user )
                asyncio .create_task (start_bot_instance (s_str ,phone ,uid ,'stylized'))
            else :
                if phone :data_manager .delete_session (phone )
                kb_login =ReplyKeyboardMarkup ([
                [KeyboardButton ("ارسال شماره",request_contact =True )]
                ],resize_keyboard =True ,one_time_keyboard =True )
                await message .reply_text ("**برای اتصال به تلگرام، شمارتو ارسال کن:**",reply_markup =kb_login )
    else :
        kb_login =ReplyKeyboardMarkup ([
        [KeyboardButton ("ارسال شماره",request_contact =True )]
        ],resize_keyboard =True ,one_time_keyboard =True )

        text ="**سلام و خوش اومدی!**\n\n"if message .text =="/start"else ""
        text +="**برای فعال‌سازی سلف، شماره تلگرامتو ارسال کن:**"
        await message .reply_text (text ,reply_markup =kb_login )

@manager_bot .on_message (filters .regex ("ورود مجدد \\(ریست\\)")&filters .private )
async def reset_session_handler (client ,message ):

    if not message .from_user :return 
    uid =message .from_user .id 
    await stop_user_bot (uid )
    phone =data_manager .data ["users"].get (str (uid ),{}).get ("phone")
    if phone :data_manager .delete_session (phone )
    if str (uid )in data_manager .data ["users"]:
        data_manager .data ["users"][str (uid )]["session_string"]=""
        _load_target_reply_texts (uid ,restore_defaults =True )
        _commit_and_broadcast_shards ("reset-session-defaults")

    kb_login =ReplyKeyboardMarkup ([
    [KeyboardButton ("ارسال شماره",request_contact =True )]
    ],resize_keyboard =True ,one_time_keyboard =True )
    await message .reply_text ("**سلف متوقف شد و نشست قبلی پاک شد.**\nبرای ورود مجدد شمارتو ارسال کن:",reply_markup =kb_login )

@manager_bot .on_message (filters .regex ("مدیریت ادمین‌ها")&filters .private )
async def admin_management (client ,message ):
    if not message .from_user or message .from_user .id !=ROOT_ADMIN :return 
    text ,markup =generate_admins_markup ()
    await message .reply_text (text ,reply_markup =markup )

@manager_bot .on_message (filters .regex ("مدیریت کاربران")&filters .private )
async def user_management (client ,message ):
    if not message .from_user or message .from_user .id not in data_manager .get_admins ():return 
    text ,markup =generate_users_markup (0 )
    await message .reply_text (text ,reply_markup =markup )

@manager_bot .on_message (filters .regex ("عضویت اجباری سراسری")&filters .private )
async def global_fjoin_management (client ,message ):
    if not message .from_user or message .from_user .id !=ROOT_ADMIN :return 
    text ,markup =generate_global_fjoin_markup ()
    await message .reply_text (text ,reply_markup =markup )

@manager_bot .on_message (filters .regex ("وضعیت سراسری سلف‌ها")&filters .private )
async def global_bot_status_management (client ,message ):
    if not message .from_user or message .from_user .id !=ROOT_ADMIN :return 
    text ,markup =generate_global_bot_status_markup ()
    await message .reply_text (text ,reply_markup =markup )

@manager_bot .on_message (filters .regex ("بکاپ دیتابیس")&filters .private )
async def manual_database_backup_handler (client ,message ):
    if not message .from_user or message .from_user .id !=ROOT_ADMIN :
        return 
    status =await message .reply_text ("**در حال ساخت و ارسال بکاپ دیتابیس...**")
    ok ,info =await send_database_backup_to_admin (message .from_user .id ,manual =True )
    if ok :
        await status .edit_text (f"**بکاپ دیتابیس ارسال شد.**\n`{info }`")
    else :
        await status .edit_text (f"**ارسال بکاپ انجام نشد:**\n`{info }`")

@manager_bot .on_message (filters .regex ("بازیابی دیتابیس")&filters .private )
async def database_restore_prompt (client ,message ):
    if not message .from_user or message .from_user .id !=ROOT_ADMIN :
        return 
    LOGIN_STATES [message .from_user .id ]={"step":"awaiting_db_restore"}
    await message .reply_text (
    "**بازیابی دیتابیس**\n\n"
    "فایل بکاپ `bot_data.json` رو همینجا به صورت فایل ارسال کن.\n"
    "بعد از بررسی، دیتابیس جایگزین می‌شه و ربات ری‌استارت می‌شه.\n\n"
    "برای لغو: `لغو`"
    )

@manager_bot .on_message (filters .regex ("حذف کامل دیتابیس")&filters .private )
async def wipe_database_prompt (client ,message ):
    if not message .from_user or message .from_user .id !=ROOT_ADMIN :
        return 
    buttons =InlineKeyboardMarkup ([
    [InlineKeyboardButton ("بله، همه چیز را کامل حذف کن",callback_data ="wipe_db_confirm")],
    [InlineKeyboardButton ("انصراف",callback_data ="close_admin")]
    ])
    await message .reply_text (
    "**حذف کامل دیتابیس**\n\n"
    "این عملیات همه کاربران، سشن‌ها، ادمین‌های اضافه و تنظیمات را برای همیشه پاک می‌کند "
    "و همه سلف‌های فعال را خاموش می‌کند.\n\n"
    "**این کار غیرقابل بازگشت است.** اگر بکاپ سالم داری، بعد از حذف می‌توانی از دکمه "
    "«بازیابی دیتابیس» جایگزینش کنی.\n\n"
    "آیا مطمئن هستید؟",
    reply_markup =buttons 
    )

@manager_bot .on_message (filters .regex ("پیام همگانی")&filters .private )
async def broadcast_msg (client ,message ):
    if not message .from_user or message .from_user .id not in data_manager .get_admins ():return 
    LOGIN_STATES [message .from_user .id ]={"step":"awaiting_broadcast"}
    await message .reply_text ("**پیامی که می‌خوای برای همه کاربرا ارسال بشه رو بفرست** (متن، عکس یا ویدیو):\nبرای لغو بنویس `لغو`")

@manager_bot .on_message (filters .regex ("وضعیت سرور")&filters .private )
async def status_msg (client ,message ):
    if not message .from_user or message .from_user .id not in data_manager .get_admins ():return 
    total_users =len (data_manager .get_all_users ())
    active =len (ACTIVE_BOTS )
    status_str ="روشن"if data_manager .data .get ("global_bot_status",True )else "خاموش"
    text =f"**وضعیت سرور:**\n\n"
    text +=f"وضعیت کل سلف‌ها: **{status_str }**\n"
    text +=f"کاربران ثبت‌شده: `{total_users }`\n"
    text +=f"سلف‌های فعال: `{active }`\n"
    text +=f"زمان سرور: `{datetime .now (TEHRAN_TIMEZONE ).strftime ('%Y-%m-%d %H:%M:%S')}`\n\n"
    text +=get_server_stats_text ()
    await message .reply_text (text ,reply_markup =build_server_status_markup ())

@manager_bot .on_message (filters .contact &filters .private )
async def contact_handler (client ,message ):
    if not message .from_user :return 
    if data_manager .is_banned (message .from_user .id ):
        return await message .reply_text ("**دسترسی مسدود شده.**",reply_markup =ReplyKeyboardRemove ())
    if not data_manager .data .get ("global_bot_status",True ):
        return await message .reply_text ("**ثبت‌نام موقتاً غیرفعال است.**",reply_markup =ReplyKeyboardRemove ())
    if not data_manager .self_slot_available (message .from_user .id ):
        return await message .reply_text (self_capacity_full_text (),reply_markup =ReplyKeyboardRemove ())

    uid =message .chat .id 
    now =time .time ()
    attempts =LOGIN_RATE_LIMIT .get (uid ,[])
    attempts =[t for t in attempts if now -t <LOGIN_RATE_WINDOW ]
    if len (attempts )>=LOGIN_RATE_MAX :
        return await message .reply_text ("**تلاش‌های ورود بیش از حد مجاز است.** لطفاً ۱۰ دقیقه صبر کنید.",reply_markup =ReplyKeyboardRemove ())
    attempts .append (now )
    LOGIN_RATE_LIMIT [uid ]=attempts 

    old_state =LOGIN_STATES .pop (uid ,None )
    old_client =old_state .get ("client")if isinstance (old_state ,dict )else None 
    if old_client :
        try :
            await asyncio .wait_for (old_client .disconnect (),timeout =4 )
        except Exception :
            pass 

    phone =message .contact .phone_number 
    status =await message .reply_text ("**در حال ارسال کد تایید...**",reply_markup =ReplyKeyboardRemove ())
    login_fp =_get_client_fingerprint (uid )
    user_c =Client (
    f"login_{uid }",api_id =API_ID ,api_hash =API_HASH ,
    no_updates =True ,workers =1 ,in_memory =True ,**login_fp ,**_darkself_optional_client_kwargs ()
    )

    async def show_status (text ):
        try :
            await status .edit_text (text )
            return 
        except Exception :
            pass 
        try :
            await message .reply_text (text )
        except Exception :
            pass 

    try :
        await asyncio .wait_for (user_c .connect (),timeout =20.0 )
        sent =await asyncio .wait_for (user_c .send_code (phone ),timeout =60.0 )
        phone_hash =getattr (sent ,"phone_code_hash",None )
        if not phone_hash :
            raise RuntimeError ("phone_code_hash missing")
        LOGIN_STATES [uid ]={
        "step":"code","phone":phone ,
        "client":user_c ,"hash":phone_hash ,
        "started_at":time .time (),
        }
        await show_status ("**کد تایید ارسال شد.**\nآن را با فاصله وارد کنید (مثال: 1 2 3 4 5)")
    except asyncio .TimeoutError :
        try :
            await user_c .disconnect ()
        except Exception :
            pass 
        LOGIN_STATES .pop (uid ,None )
        await show_status ("**ارسال کد بیشتر از حد معمول طول کشید و لغو شد.** چند دقیقه بعد دوباره تلاش کنید.")
    except FloodWait as fw :
        try :
            await user_c .disconnect ()
        except Exception :
            pass 
        LOGIN_STATES .pop (uid ,None )
        await show_status (f"**تلگرام موقتاً محدودیت گذاشته است.** حدود `{fw .value }` ثانیه صبر کنید.")
    except Exception as e :
        try :
            await user_c .disconnect ()
        except Exception :
            pass 
        LOGIN_STATES .pop (uid ,None )
        err =str (e ).lower ()
        if "phone_number_banned"in err or "phone number banned"in err :
            text ="**این شماره توسط تلگرام محدود شده و فعلاً امکان ارسال کد ندارد.**"
        elif "phone_number_invalid"in err or "phone number invalid"in err :
            text ="**شماره معتبر نیست.** شماره را با فرمت درست ارسال کنید."
        elif "phone_code_flood"in err or "flood"in err :
            text ="**درخواست کد برای این شماره موقتاً محدود شده است.** چند ساعت بعد امتحان کنید."
        else :
            text ="**ارسال کد انجام نشد.** چند دقیقه صبر کنید و دوباره تلاش کنید."
        await show_status (text )

@manager_bot .on_message (filters .private &filters .create (lambda _ ,__ ,m :m .chat and m .chat .id in LOGIN_STATES ))
async def text_handler (client ,message ):
    uid =message .chat .id 
    if data_manager .is_banned (uid ):
        LOGIN_STATES .pop (uid ,None )
        return await message .reply_text ("**دسترسی مسدود شده.**",reply_markup =ReplyKeyboardRemove ())
    st =LOGIN_STATES [uid ]

    if st .get ('step')=='awaiting_db_restore':
        if message .text and message .text .strip ()=="لغو":
            del LOGIN_STATES [uid ]
            return await message .reply_text ("**بازیابی دیتابیس لغو شد.**")
        if message .from_user .id !=ROOT_ADMIN :
            return 
        await restore_database_from_document (message )
        try :
            del LOGIN_STATES [uid ]
        except Exception :
            pass 
        return 

    if st ['step']=='awaiting_broadcast':
        if message .text and message .text =="لغو":
            del LOGIN_STATES [uid ]
            return await message .reply_text ("**ارسال همگانی لغو شد.**")

        del LOGIN_STATES [uid ]
        msg_wait =await message .reply_text ("**در حال ارسال پیام همگانی...**")
        success =0 
        failed =0 
        for user_id in list (data_manager .get_all_users ().keys ()):
            try :
                await message .copy (int (user_id ))
                success +=1 
                await asyncio .sleep (0.2 )
            except Exception :
                failed +=1 
        await msg_wait .edit_text (f"**پیام همگانی ارسال شد.**\n\nموفق: `{success }`\nناموفق: `{failed }`")
        return 

    if st ['step']=='awaiting_admin_id':
        if message .text and message .text .isdigit ():
            if data_manager .add_admin (int (message .text )):
                await message .reply_text (f"**ادمین `{message .text }` اضافه شد.**")
            else :
                await message .reply_text ("**این کاربر از قبل ادمین بود.**")
        else :
            await message .reply_text ("**آیدی باید عدد باشد.**")
        del LOGIN_STATES [uid ]
        return 

    if st ['step']=='awaiting_global_fjoin':
        chat_target =message .text .strip ()
        if not chat_target .startswith ("@")and not chat_target .startswith ("-100"):
            await message .reply_text ("**فرمت اشتباه است.** باید با @ یا آیدی عددی کانال (با -100) شروع شود.")
            del LOGIN_STATES [uid ]
            return 

        await message .reply_text ("**بررسی کانال/گروه...**")
        try :
            chat_info =await manager_bot .get_chat (chat_target )
            member =await manager_bot .get_chat_member (chat_info .id ,"me")
            if member .status in [ChatMemberStatus .ADMINISTRATOR ,ChatMemberStatus .OWNER ]:
                chats =data_manager .data .setdefault ("global_fjoin_chats",[])
                stored_target =f"@{chat_info .username }"if chat_info .username else str (chat_info .id )
                if stored_target not in chats :
                    chats .append (stored_target )
                    data_manager .save_data ()
                await message .reply_text (f"**کانال `{stored_target }` به عنوان کانال سراسری ثبت شد.**")
            else :
                await message .reply_text ("**ربات مدیریت در این کانال ادمین نیست.**")
        except Exception as e :
            await message .reply_text (f"**بررسی کانال ناموفق بود.**\n`{str (e )[:150 ]}`")
        del LOGIN_STATES [uid ]
        text ,markup =generate_global_fjoin_markup ()
        await message .reply_text (text ,reply_markup =markup )
        return 

    if st .get ('step')=='awaiting_self_limit':
        if message .from_user and message .from_user .id !=ROOT_ADMIN :
            return 
        raw =(message .text or "").strip ()
        if raw =="لغو":
            del LOGIN_STATES [uid ]
            return await message .reply_text ("**تنظیم لیمیت لغو شد.**",reply_markup =get_admin_menu_keyboard (uid ))
        for i ,d in enumerate ("۰۱۲۳۴۵۶۷۸۹"):raw =raw .replace (d ,str (i ))
        for i ,d in enumerate ("٠١٢٣٤٥٦٧٨٩"):raw =raw .replace (d ,str (i ))
        raw =re .sub (r"\D","",raw )
        if not raw :
            return await message .reply_text ("لطفاً فقط یک عدد بفرست. مثال: `100`\nبرای لغو `لغو` را بفرست:")
        value =int (raw )
        if value <1 :
            return await message .reply_text ("عدد باید حداقل ۱ باشه. اگه می‌خوای محدودیتی نباشه، از دکمهٔ «نامحدود» استفاده کن:")
        data_manager .set_self_limit (value )
        del LOGIN_STATES [uid ]
        limit ,used ,free =data_manager .self_limit_status ()
        return await message .reply_text (
        f"✓ لیمیت فعال‌سازی سلف روی **{limit } نفر** تنظیم شد.\n"
        f"پر شده: `{used }`  ·  جای خالی: `{free }`",
        reply_markup =get_admin_menu_keyboard (uid )
        )

    user_c =st .get ('client')
    if not user_c :return 

    if st ['step']=='code':
        if not message .text :return await message .reply_text ("**کد را به صورت متنی ارسال کنید.**")
        try :
            await asyncio .wait_for (user_c .sign_in (st ['phone'],st ['hash'],re .sub (r"\D+","",message .text )),timeout =20.0 )
            await finalize_login (message ,user_c ,st ['phone'])
        except SessionPasswordNeeded :
            # Reuse the encrypted 2FA credential if this account has one saved.
            saved_uid =st .get ("user_id")
            if not saved_uid :
                try :
                    wanted_phone =str (st .get ("phone") or "").strip ()
                    for _uid ,_ud in data_manager .data .get ("users",{}).items ():
                        if str (_ud .get ("phone") or "").strip ()==wanted_phone:
                            saved_uid =int (_uid )
                            break
                except Exception :
                    saved_uid =None
            saved_password =""
            if saved_uid :
                try :
                    saved_password =_db_decrypt (data_manager .get_user_data (int (saved_uid)).get ("settings",{}).get ("twofa_password","")).strip ()
                except Exception :
                    saved_password =""
            if saved_password :
                try :
                    await asyncio .wait_for (user_c .check_password (saved_password ),timeout =20.0 )
                    await finalize_login (message ,user_c ,st ['phone'])
                    return
                except Exception :
                    # Invalid/stale credential: clear it and fall back to manual entry.
                    try :
                        if saved_uid :
                            data_manager .get_user_data (int (saved_uid)).setdefault ("settings",{})["twofa_password"]=""
                            data_manager .save_data ()
                            data_manager .force_save_sync ()
                    except Exception :
                        pass
            st ['step']='password'
            await message .reply_text ("**رمز دو مرحله‌ای را وارد کنید:**")
        except Exception as e :
            err =str (e ).lower ()
            if "phone_code_invalid"in err or "code_invalid"in err :
                await message .reply_text ("**کد وارد شده اشتباه است.** دوباره وارد کنید.")
            elif "phone_code_expired"in err or "code_expired"in err :
                await message .reply_text ("**کد منقضی شده است.** دوباره فرآیند ورود را شروع کنید.")
            else :
                await message .reply_text ("**ورود انجام نشد.** کد را بررسی کرده و دوباره تلاش کنید.")

    elif st ['step']=='password':
        if not message .text :return await message .reply_text ("**رمز را به صورت متنی ارسال کنید.**")
        password =message .text .strip ()
        try :
            await asyncio .wait_for (user_c .check_password (password ),timeout =20.0 )
            # Store the 2FA password encrypted in the database so a later login
            # can reuse it without asking the user again. Never store plaintext.
            uid_hint =st .get ("user_id")
            if not uid_hint :
                try :
                    me_hint =await asyncio .wait_for (user_c .get_me (),timeout =10.0 )
                    uid_hint =me_hint .id
                except Exception :
                    uid_hint =None
            if uid_hint :
                ud =data_manager .get_user_data (int (uid_hint))
                ud .setdefault ("settings",{})["twofa_password"]=_db_encrypt (password )
                data_manager .save_data ()
                data_manager .force_save_sync ()
            await finalize_login (message ,user_c ,st ['phone'])
        except Exception as e :
            err =str (e ).lower ()
            if "password_hash_invalid"in err or "password"in err :
                await message .reply_text ("**رمز دو مرحله‌ای وارد شده اشتباه است.** دوباره وارد کنید.")
            else :
                await message .reply_text ("**ورود انجام نشد.** رمز را بررسی کرده و دوباره تلاش کنید.")

async def finalize_login (message ,user_c ,phone ):
    chat_id =message .chat .id 
    if data_manager .is_banned (chat_id ):
        try :
            await user_c .disconnect ()
        except Exception :
            pass 
        LOGIN_STATES .pop (chat_id ,None )
        return await message .reply_text ("**دسترسی مسدود شده.**",reply_markup =ReplyKeyboardRemove ())
    try :
        s_str =await asyncio .wait_for (user_c .export_session_string (),timeout =15.0 )
        me =await asyncio .wait_for (user_c .get_me (),timeout =10.0 )
        uid =me .id 
        if data_manager .is_banned (uid ):
            try :
                await user_c .disconnect ()
            except Exception :
                pass 
            LOGIN_STATES .pop (chat_id ,None )
            return await message .reply_text ("**دسترسی مسدود شده.**",reply_markup =ReplyKeyboardRemove ())

        if not data_manager .self_slot_available (uid ):
            try :
                await user_c .disconnect ()
            except Exception :
                pass 
            LOGIN_STATES .pop (chat_id ,None )
            return await message .reply_text (self_capacity_full_text (),reply_markup =ReplyKeyboardRemove ())

        try :
            await user_c .disconnect ()
        except Exception :
            pass 
        if uid in ACTIVE_BOTS :
            await stop_user_bot (uid )
            load_all_states ()
        activation_started_at =time .time ()
        data_manager .update_user_data (uid ,{
        "first_name":me .first_name or "",
        "username":me .username or "",
        "last_login_ts":int (activation_started_at ),
        "activation_ready_at":activation_started_at +_fresh_login_start_delay (phone ),
        "activation_id":uuid .uuid4 ().hex ,
        "activation_notice_chat":chat_id ,
        "activation_notice_pending":True ,
        "activation_failure_notified":False 
        })
        data_manager .save_session (phone ,s_str ,uid )
        _commit_and_broadcast_shards ("fresh-login-activation")
        try :
            asyncio .create_task (start_bot_instance (s_str ,phone ,uid ,'stylized'))
        except Exception as exc :
            logger .warning ("Activation scheduling failed for %s: %s",uid ,type (exc ).__name__ )
        try :
            del LOGIN_STATES [chat_id ]
        except Exception :
            pass 
        try :
            await message .reply_text ("**ورود شما ثبت شد.**\n\nبرای فعال‌سازی سلف، ۲ دقیقه منتظر بمانید؛ این زمان برای همهٔ کاربران یکسان است.\nبعد از پایان انتظار و اتصال واقعی، پیام آماده‌بودن ارسال می‌شود. سپس داخل پیام‌های ذخیره‌شده (Saved Messages) حساب تلگرامتان، دستور `پنل` یا `راهنما` را بزنید.")
        except Exception :
            pass 
    except asyncio .TimeoutError :

        try :
            await user_c .disconnect ()
        except Exception :
            pass 
        try :
            del LOGIN_STATES [chat_id ]
        except Exception :
            pass 
        try :
            await message .reply_text ("**ورود تایم‌اوت شد.** دوباره /start بزنید و شماره را ارسال کنید.")
        except Exception :
            pass 
    except Exception as e :
        logger .warning (f"finalize_login failed for {phone }: {e }")
        try :
            await user_c .disconnect ()
        except Exception :
            pass 
        try :
            del LOGIN_STATES [chat_id ]
        except Exception :
            pass 
        try :
            await message .reply_text (f"**نهایی‌سازی ورود ناموفق بود.**\n`{str (e )[:120 ]}`\nدوباره /start بزنید.")
        except Exception :
            pass 

async def send_database_backup_to_admin (target_id :int =ROOT_ADMIN ,manual :bool =False ):
    try :
        try :
            data_manager .force_save_sync ()
        except Exception :
            pass 

        if not os .path .exists (DATA_FILE )or os .path .getsize (DATA_FILE )<=10 :
            return False ,"فایل دیتابیس پیدا نشد یا خالی است."

        users_count =len (data_manager .data .get ("users",{}))if isinstance (data_manager .data ,dict )else 0 
        sessions_count =len (data_manager .data .get ("sessions",{}))if isinstance (data_manager .data ,dict )else 0 
        now_dt =datetime .now (TEHRAN_TIMEZONE )
        now_text =now_dt .strftime ("%Y/%m/%d - %H:%M:%S")
        mode_text ="دستی"if manual else "خودکار"
        caption =(
        f"بکاپ {mode_text } دیتابیس\n"
        f"زمان: `{now_text }`\n"
        f"کاربران: `{users_count }` | سشن‌ها: `{sessions_count }`"
        )

        backup_send_path =f"/tmp/bot_data_backup_{now_dt .strftime ('%Y%m%d_%H%M%S')}.json"
        try :
            with open (backup_send_path ,"w",encoding ="utf-8")as f :
                json .dump (data_manager .data ,f ,ensure_ascii =False ,indent =2 )
            await manager_bot .send_document (target_id ,backup_send_path ,caption =caption )
        finally :
            try :
                if os .path .exists (backup_send_path ):
                    os .remove (backup_send_path )
            except Exception :
                pass 
        return True ,f"ارسال شد. users={users_count } sessions={sessions_count }"
    except FloodWait as fw :
        await asyncio .sleep (fw .value +5 )
        return False ,f"FloodWait: {fw .value }"
    except Exception as e :
        logger .warning (f"Database backup send failed: {e }")
        return False ,str (e )[:180 ]

async def hourly_database_backup_task ():
    await asyncio .sleep (600 )
    while True :
        ok ,info =await send_database_backup_to_admin (ROOT_ADMIN ,manual =False )
        if not ok :
            logger .warning (f"Hourly database backup failed: {info }")
        await asyncio .sleep (7200 )

FJOIN_MEMBERSHIP_CACHE ={}
FJOIN_CACHE_TTL =90 

def _check_fjoin_cache (uid ,sender_id ,chat =None ):
    try :
        key =(int (uid ),int (sender_id ))
        entry =FJOIN_MEMBERSHIP_CACHE .get (key )
        if entry :
            status ,ts =entry 
            if status and (time .time ()-ts )<86400 :
                return True 
            elif not status and (time .time ()-ts )<5 :
                return False 
    except Exception :
        pass 
    return None 

def _set_fjoin_cache (uid ,sender_id ,chat =None ,status =True ):
    try :
        key =(int (uid ),int (sender_id ))
        FJOIN_MEMBERSHIP_CACHE [key ]=(bool (status ),time .time ())
        if len (FJOIN_MEMBERSHIP_CACHE )>1000 :
            sorted_keys =sorted (FJOIN_MEMBERSHIP_CACHE .items (),key =lambda x :x [1 ][1 ])
            for k ,_ in sorted_keys [:500 ]:
                FJOIN_MEMBERSHIP_CACHE .pop (k ,None )
    except Exception :
        pass 

def _clear_fjoin_cache_for_user (uid ):
    try :
        uid =int (uid )
        keys_to_remove =[k for k in FJOIN_MEMBERSHIP_CACHE .keys ()if k [0 ]==uid ]
        for k in keys_to_remove :
            FJOIN_MEMBERSHIP_CACHE .pop (k ,None )
    except Exception :
        pass 

def _rss_mb ():
    try :
        if psutil is not None :
            return psutil .Process (os .getpid ()).memory_info ().rss /1024 /1024 
    except Exception :
        pass 
    return 0.0 

_LIBC_HANDLE =None
def _malloc_trim ():
    global _LIBC_HANDLE
    try :
        import ctypes
        if _LIBC_HANDLE is None :
            _LIBC_HANDLE =ctypes .CDLL ("libc.so.6")
        _LIBC_HANDLE .malloc_trim (0 )
    except Exception :
        pass 

def _drop_idle_caches (keep_timeline =20 ):
    for cache_uid in list (MESSAGE_TIMELINE_CACHE .keys ()):
        cache =MESSAGE_TIMELINE_CACHE .get (cache_uid )or {}
        extra =max (0 ,len (cache )-keep_timeline )
        for k in list (cache .keys ())[:extra ]:
            item =cache .pop (k ,None )
            if item :
                _drop_timeline_cache_item (item )
    try :
        if len (MESSAGE_ID_INDEX )>500 :
            MESSAGE_ID_INDEX .clear ()
    except Exception :
        pass 
    try :
        if len (RAW_TTL_MEDIA_HINTS )>RAW_TTL_MEDIA_HINTS_LIMIT :
            extra =len (RAW_TTL_MEDIA_HINTS )-RAW_TTL_MEDIA_HINTS_LIMIT 
            for k in list (RAW_TTL_MEDIA_HINTS .keys ())[:extra ]:
                RAW_TTL_MEDIA_HINTS .pop (k ,None )
    except Exception :
        pass 
    for t in list (ANTI_DELETE_MEDIA_TASKS ):
        if t .done ()or t .cancelled ():
            ANTI_DELETE_MEDIA_TASKS .discard (t )
        elif len (ANTI_DELETE_MEDIA_TASKS )>ANTI_DELETE_MEDIA_TASK_LIMIT :
            try :t .cancel ()
            except Exception :pass 
            ANTI_DELETE_MEDIA_TASKS .discard (t )

def _prune_client_runtime (client ,rss =0 ):
    if client is None :
        return 
    
    try :
        mc =getattr (client ,"message_cache",None )
        if mc is not None and len (mc )>64 :
            try :
                while len (mc )>64 :
                    mc .popleft ()
            except Exception :
                try :
                    mc .clear ()
                except Exception :
                    pass
    except Exception :
        pass
    queue_cap =15 if rss >1800 else 40 if rss >1200 else 80 
    peer_keep =400 if rss >1800 else 800 if rss >1200 else 1200 
    try :
        q =getattr (getattr (client ,"dispatcher",None ),"updates_queue",None )
        if q is not None :
            while True :
                try :
                    n =q .qsize ()
                except Exception :
                    break 
                if n <=queue_cap :
                    break 
                try :
                    q .get_nowait ()
                    try :
                        q .task_done ()
                    except Exception :
                        pass 
                except Exception :
                    break 
    except Exception :
        pass 
    try :
        conn =getattr (getattr (client ,"storage",None ),"conn",None )
        if conn is None :
            return 
        try :
            n =conn .execute ("SELECT COUNT(*) FROM peers").fetchone ()[0 ]
        except Exception :
            return 
        if n >peer_keep +200 :
            try :
                conn .execute ("DELETE FROM peers WHERE ROWID NOT IN (SELECT ROWID FROM peers ORDER BY ROWID DESC LIMIT ?)",(peer_keep ,))
                conn .commit ()
            except Exception :
                pass 
            if rss >1100 :
                try :
                    conn .execute ("VACUUM")
                except Exception :
                    pass 
        try :
            conn .execute ("PRAGMA shrink_memory")
        except Exception :
            pass 
    except Exception :
        pass 

async def memory_cleaner ():
    delay =90 
    while True :
        try :
            await asyncio .sleep (delay )
            rss =_rss_mb ()
            logger .info (f"Running memory pruning... RSS={rss :.0f}MB bots={len (ACTIVE_BOTS )}")
            keep =4 if rss >1500 else 8 if rss >800 else 20 if rss >500 else TIMELINE_CACHE_TRIM_TO 
            _drop_idle_caches (keep_timeline =keep )
            for uid in list (ACTIVE_BOTS .keys ()):
                try :
                    pair =ACTIVE_BOTS .get (uid )
                    _prune_client_runtime (pair [0 ]if pair else None ,rss )
                except Exception :
                    pass 
            try :
                if manager_bot :
                    _prune_client_runtime (manager_bot ,rss )
            except Exception :
                pass 
            for cache_uid in list (MESSAGE_TIMELINE_CACHE .keys ()):
                try :
                    _trim_timeline_cache (cache_uid )
                except Exception :
                    pass 

            active_uids =set (ACTIVE_BOTS .keys ())
            active_uids .add (ROOT_ADMIN )
            try :
                if manager_bot and manager_bot .me :
                    active_uids .add (manager_bot .me .id )
            except Exception :
                pass 

            for cache_dict in (CACHE_NAMES ,CACHE_BIOS ,CACHE_LAST_SENT_NAME ,CACHE_LAST_SENT_BIO ,
            LAST_FJOIN_ALERT ,INLINE_IDLE_STATE .get ("panel",{}),
            INLINE_IDLE_STATE .get ("help",{})):
                try :
                    for k in list (cache_dict .keys ()):
                        try :
                            if int (k )not in active_uids :
                                cache_dict .pop (k ,None )
                        except Exception :
                            cache_dict .pop (k ,None )
                except Exception :
                    pass 

            try :
                prune_antidelete_disk_cache ()
                prune_download_temp_dir ()
            except Exception :
                pass 

            try :
                now =time .time ()
                keys_to_remove =[k for k ,(_ ,ts )in FJOIN_MEMBERSHIP_CACHE .items ()
                if (now -ts )>FJOIN_CACHE_TTL *2 or k [0 ]not in active_uids ]
                for k in keys_to_remove :
                    FJOIN_MEMBERSHIP_CACHE .pop (k ,None )
            except Exception :
                pass

            try :
                
                now_ts =time .time ()
                for luid in list (LOGIN_STATES .keys ()):
                    lst =LOGIN_STATES .get (luid )
                    if not isinstance (lst ,dict ):
                        LOGIN_STATES .pop (luid ,None )
                        continue
                    lclient =lst .get ("client")
                    started =float (lst .get ("started_at",0 )or 0 )
                    if lclient is not None and (not started or now_ts -started >600 ):
                        LOGIN_STATES .pop (luid ,None )
                        try :
                            await asyncio .wait_for (lclient .disconnect (),timeout =3.0 )
                        except Exception :
                            pass
            except Exception :
                pass 

            if rss >1100 :
                try :
                    MESSAGE_ID_INDEX .clear ()
                except Exception :
                    pass 
                try :
                    RAW_TTL_MEDIA_HINTS .clear ()
                except Exception :
                    pass 
                for cache_uid in list (MESSAGE_TIMELINE_CACHE .keys ()):
                    cache =MESSAGE_TIMELINE_CACHE .get (cache_uid )or {}
                    extra =max (0 ,len (cache )-8 )
                    for k in list (cache .keys ())[:extra ]:
                        item =cache .pop (k ,None )
                        if item :
                            _drop_timeline_cache_item (item )

            gc .collect (2 )
            _malloc_trim ()
            rss2 =_rss_mb ()
            delay =20 if rss2 >1400 else 40 if rss2 >900 else 90 
            logger .info (f"memory prune done RSS={rss2 :.0f}MB")
            if rss2 >1800 :
                logger .warning (f"RSS still high ({rss2 :.0f}MB) after client/queue/peer prune")

        except asyncio .CancelledError :
            break 
        except MemoryError :
            try :
                MESSAGE_TIMELINE_CACHE .clear ()
                MESSAGE_ID_INDEX .clear ()
                RAW_TTL_MEDIA_HINTS .clear ()
            except Exception :
                pass 
            try :
                gc .collect ()
                _malloc_trim ()
            except Exception :
                pass 
            await asyncio .sleep (15 )
        except Exception as e :
            logger .error ("Error in memory_cleaner loop: %s",type (e ).__name__ )

async def _enforce_access_restrictions ():
    admins =set (data_manager .get_admins ())
    admins .add (ROOT_ADMIN )
    for uid in list (ACTIVE_BOTS .keys ()):
        try :
            if uid in admins :
                continue 
            if data_manager .is_banned (uid )or data_manager .is_invalid_session_uid (uid ):
                logger .info (f"stopping session {uid } due to access restriction (ban/invalid)")
                await stop_user_bot (uid )
        except Exception :
            pass 

async def database_external_reload_watcher ():
    await asyncio .sleep (5 )
    while True :
        try :
            await asyncio .sleep (20 )
            changed =data_manager ._external_reload_pending or data_manager .reload_from_disk_if_changed ()
            if changed :
                data_manager ._external_reload_pending =False 
                load_all_states ()
                _broadcast_database_change ()
                await sync_sessions_from_database ("external-backup-import")
            await _enforce_access_restrictions ()
        except asyncio .CancelledError :
            break 
        except Exception as e :
            logger .error (f"Database watcher error: {e }")

async def main ():
    if SHARD_ID is not None and SHARD_COUNT >1 :
        await _worker_main ()
        return 

    try :
        limits =data_manager .get_server_limits ()
        cpu_limit =int (limits .get ("cpu")or 0 )
    except Exception :
        cpu_limit =0 

    if _sharding_enabled_for (cpu_limit ):

        try :
            apply_server_limits ()
        except Exception as e :
            logger .warning (f"apply_server_limits در master failed: {e }")
        await _master_sharded_main ()
    else :
        await _legacy_main ()

async def _shard_reload_watcher():
    last_signature = None
    while True:
        try:
            await asyncio.sleep(1.0)
            should_reload, signature = _shard_should_reload(last_signature)
            if not should_reload:
                continue
            logger.info("[shard-%s] reload signal received", SHARD_ID)
            try:
                data_manager.reload_from_disk_if_changed(force=True)
                load_all_states()
                last_signature = signature
            except Exception as exc:
                logger.warning("[shard-%s] reload states failed: %s", SHARD_ID, exc)
                continue
            try:
                await sync_sessions_from_database("shard-reload-signal")
            except Exception as exc:
                logger.warning("[shard-%s] sync after reload failed: %s", SHARD_ID, exc)
            try:
                for uid in list(ACTIVE_BOTS.keys()):
                    if not _shard_assigns_to_me(uid):
                        await stop_user_bot(uid)
            except Exception as exc:
                logger.warning("[shard-%s] stop-reassign failed: %s", SHARD_ID, exc)
            try:
                await _enforce_access_restrictions()
            except Exception as exc:
                logger.warning("[shard-%s] enforce-restrictions failed: %s", SHARD_ID, exc)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error("[shard-%s] reload watcher error: %s", SHARD_ID, exc)

async def _shard_status_reporter ():
    if SHARD_ID is None :
        return 
    status_file =os .path .join (
    os .path .dirname (os .path .abspath (__file__ ))or ".",
    f".darkself_shard_status_{SHARD_ID }.json"
    )
    while True :
        try :
            await asyncio .sleep (5 )
            payload ={
            "shard_id":SHARD_ID ,
            "pid":os .getpid (),
            "active":len (ACTIVE_BOTS ),
            "starting":len (STARTING_BOTS ),
            "ts":time .time (),
            }
            with open (status_file ,"w")as f :
                json .dump (payload ,f )
        except asyncio .CancelledError :
            break 
        except Exception :
            pass 

async def _master_health_watcher ():
    while True :
        try :
            await asyncio .sleep (10 )
            try :
                _shard_supervisor .health_check ()
            except Exception :
                pass 
        except asyncio .CancelledError :
            break 
        except Exception :
            pass 

def _read_all_shard_statuses ():
    out ={}
    base =os .path .dirname (os .path .abspath (__file__ ))or "."
    if SHARD_COUNT and SHARD_COUNT >1 :
        n =SHARD_COUNT 
    else :
        try :
            n =int (data_manager .get_server_limits ().get ("cpu")or 0 )
        except Exception :
            n =0 
    for k in range (n ):
        path =os .path .join (base ,f".darkself_shard_status_{k }.json")
        try :
            with open (path )as f :
                out [k ]=json .load (f )
        except Exception :
            out [k ]=None 
    return out 

async def _worker_main ():
    try :
        startup_disk_safety_cleanup ()
    except Exception :
        pass 

    try :
        apply_server_limits ()
    except Exception as e :
        logger .warning (f"[shard-{SHARD_ID }] apply_server_limits failed: {e }")

    try :
        load_all_states ()
    except Exception as e :
        logger .warning (f"[shard-{SHARD_ID }] load_all_states failed: {e }")

    asyncio .create_task (_shard_reload_watcher ())
    asyncio .create_task (_shard_status_reporter ())

    try :
        sessions_to_start =[
        (p ,d )for p ,d in data_manager .get_all_sessions ()
        if _shard_assigns_to_me (int (d .get ("user_id",0 )))
        ]
    except Exception :
        sessions_to_start =[]
    total_mine =len (sessions_to_start )
    logger .info (f"[shard-{SHARD_ID }] starting {total_mine } sessions (my share of {SHARD_COUNT } shards)")

    startup_semaphore =asyncio .Semaphore (STARTUP_CONCURRENCY )

    async def start_one (phone ,s_data ):
        async with startup_semaphore :
            try :
                uid =int (s_data ["user_id"])
                if data_manager .is_banned (uid )or data_manager .is_invalid_session_uid (uid ):
                    return 
                if uid in ACTIVE_BOTS or uid in STARTING_BOTS :
                    return 
                STARTING_BOTS .add (uid )
                try :
                    await start_bot_instance (s_data ["string"],phone ,uid ,'stylized')
                finally :
                    STARTING_BOTS .discard (uid )
            except Exception as e :
                logger .warning (f"[shard-{SHARD_ID }] startup error for {phone }: {e }")

    async def startup_all ():
        tasks =[asyncio .create_task (start_one (p ,d ))for p ,d in sessions_to_start ]
        if tasks :
            await asyncio .gather (*tasks ,return_exceptions =True )
        logger .info (f"[shard-{SHARD_ID }] startup done: {len (ACTIVE_BOTS )} active")

    asyncio .create_task (startup_all ())

    try :
        await idle ()
    except KeyboardInterrupt :
        logger .info (f"[shard-{SHARD_ID }] Ctrl+C; shutting down...")
    finally :
        stop_tasks =[]
        for uid ,(client ,tsks )in list (ACTIVE_BOTS .items ()):
            for t in tsks :
                try :t .cancel ()
                except Exception :pass 
            stop_tasks .append (client .stop ())
        if stop_tasks :
            try :
                await asyncio .wait_for (asyncio .gather (*stop_tasks ,return_exceptions =True ),timeout =3.0 )
            except Exception :
                pass 
        try :
            if HTTP_SESSION and not HTTP_SESSION .closed :
                await HTTP_SESSION .close ()
        except Exception :
            pass 

async def _master_sharded_main ():
    global BOT_USERNAME 
    try :
        startup_disk_safety_cleanup ()
    except Exception :
        pass 

    try :
        _shard_signal_reload ()
    except Exception :
        pass 
    try :
        await manager_bot .start ()
        me =await manager_bot .get_me ()
        BOT_USERNAME =me .username 
        asyncio .create_task (notify_admins (
        f"ربات مدیریت با موفقیت استارت شد.\n"
        f"⚡ شاردینگ فعال: {_SHARD_CURRENT_N } ورکر روی {_SHARD_CURRENT_N } هسته موازی.\n"
        f"سشن‌ها بین ورکرها با uid % {_SHARD_CURRENT_N } پخش شده‌اند."
        ))
    except Exception :
        logger .exception ("manager_bot.start() failed")
        return 

    mem_task =asyncio .create_task (memory_cleaner ())
    db_saver_task =asyncio .create_task (data_manager .auto_save_loop ())
    db_backup_task =asyncio .create_task (hourly_database_backup_task ())
    db_watch_task =asyncio .create_task (database_external_reload_watcher ())
    cpu_sampler_task =asyncio .create_task (cpu_stats_sampler ())
    health_task =asyncio .create_task (_master_health_watcher ())

    try :
        await idle ()
    except KeyboardInterrupt :
        logger .info ("Ctrl+C; در حال خاموش کردن master...")
    finally :
        logger .info ("توقف پروسه‌های master...")
        for t in (mem_task ,db_saver_task ,db_backup_task ,db_watch_task ,cpu_sampler_task ,health_task ):
            try :t .cancel ()
            except Exception :pass 
        try :
            data_manager .force_save_sync ()
        except Exception :pass 
        try :await manager_bot .stop ()
        except Exception :pass 
        try :
            if HTTP_SESSION and not HTTP_SESSION .closed :
                await HTTP_SESSION .close ()
        except Exception :pass 

        try :
            _shard_supervisor .kill_all ()
        except Exception :pass 

_MINIAPP_STATE ={"running":False,"port":None,"url":"","error":""}

def _miniapp_public_url ():
    explicit =str (os .environ .get ("MINIAPP_URL","")).strip ()
    if explicit .startswith ("https://")and "github.io"not in explicit :
        return explicit 
    dom =str (os .environ .get ("RAILWAY_PUBLIC_DOMAIN","")).strip ()
    return f"https://{dom }/"if dom else ""

async def _get_menu_button (chat_id =None ):
    try :
        async with aiohttp .ClientSession ()as sess :
            payload ={"chat_id":chat_id }if chat_id else {}
            async with sess .post (f"https://api.telegram.org/bot{BOT_TOKEN }/getChatMenuButton",json =payload ,timeout =aiohttp .ClientTimeout (total =20 ))as r :
                j =await r .json (content_type =None )
        res =j .get ("result")or {}
        return (res .get ("web_app")or {}).get ("url")or f"({res .get ('type','?')})"
    except Exception as e :
        return f"error: {type (e ).__name__ }"

async def _set_menu_button (url ,chat_id =None ):
    try :
        async with aiohttp .ClientSession ()as sess :
            payload ={"menu_button":{"type":"web_app","text":"⚡ پنل سلف","web_app":{"url":url }}}
            if chat_id :
                payload ["chat_id"]=chat_id 
            async with sess .post (f"https://api.telegram.org/bot{BOT_TOKEN }/setChatMenuButton",json =payload ,timeout =aiohttp .ClientTimeout (total =20 ))as r :
                j =await r .json (content_type =None )
        logger .info (f"[miniapp] menu button -> {url } : {'ok'if j .get ('ok')else j }")
    except Exception as e :
        logger .warning (f"[miniapp] setChatMenuButton failed: {type (e ).__name__ }: {e }")

async def _start_miniapp_server ():
    """Dashboard + API for the Telegram Mini App (served from this process)."""
    if str (os .environ .get ("MINIAPP_ENABLED","1")).strip ().lower ()in ("0","false","no","off"):
        _MINIAPP_STATE ["error"]="disabled (MINIAPP_ENABLED=0)"
        return 
    try :
        import miniapp_api 
        await miniapp_api .start (globals ())
        port =int (os .environ .get ("MINIAPP_PORT")or os .environ .get ("PORT")or 8080 )
        url =_miniapp_public_url ()
        _MINIAPP_STATE .update (running =True ,port =port ,url =url ,error ="")
        logger .info (f"[miniapp] server listening on 0.0.0.0:{port } | public url: {url or 'NOT SET - generate a Railway domain'}")
        if url :
            await _set_menu_button (url )
    except Exception as e :
        _MINIAPP_STATE ["error"]=f"{type (e ).__name__ }: {e }"
        logger .warning (f"mini app server not started: {type (e ).__name__ }: {e }")

@manager_bot .on_message (filters .private &filters .command ("miniapp"),group =-14 )
async def miniapp_status_handler (client ,message ):
    uid =message .from_user .id if message .from_user else 0 
    if uid !=ROOT_ADMIN and uid not in data_manager .get_admins ():
        return 
    st =_MINIAPP_STATE 
    txt =("🚀 **وضعیت مینی‌اپ**\n\n"
    f"سرور: {'🟢 روشن'if st ['running']else '🔴 خاموش'}\n"
    f"پورت: `{st ['port']or os .environ .get ('PORT','—')}`\n"
    f"آدرس عمومی: `{st ['url']or 'تنظیم نشده'}`\n"
    f"خطا: `{st ['error']or '—'}`\n"
    f"دکمه‌ی منوی این چت: `{await _get_menu_button (message .chat .id )}`\n"
    f"آدرس دکمه‌ی «🚀 مینی‌اپ» در منو: `{MENU_MINIAPP_URL }`\n\n")
    _pu =_miniapp_public_url ()
    if _pu :
        await _set_menu_button (_pu ,message .chat .id )
    if not st ["url"]:
        txt +="برای فعال شدن، در Railway بخش Settings > Networking گزینه‌ی Generate Domain را بزنید و دوباره دیپلوی کنید."
    await message .reply_text (txt )
    message .stop_propagation ()

async def _legacy_main ():
    global BOT_USERNAME 
    try :
        startup_disk_safety_cleanup ()
    except Exception :
        pass 
    try :
        await manager_bot .start ()
        me =await manager_bot .get_me ()
        BOT_USERNAME =me .username 
        asyncio .create_task (_start_miniapp_server ())
        asyncio .create_task (notify_admins ("ربات مدیریت با موفقیت استارت شد."))
    except Exception :
        logger .exception ("manager_bot.start() failed")
        return 

    mem_task =asyncio .create_task (memory_cleaner ())
    db_saver_task =asyncio .create_task (data_manager .auto_save_loop ())
    db_backup_task =asyncio .create_task (hourly_database_backup_task ())
    db_watch_task =asyncio .create_task (database_external_reload_watcher ())
    cpu_sampler_task =asyncio .create_task (cpu_stats_sampler ())

    sessions_to_start =list (data_manager .get_all_sessions ())
    total_db =len (sessions_to_start )
    logger .info (f"Starting self sessions from database (legacy mode): {total_db }")

    startup_semaphore =asyncio .Semaphore (STARTUP_CONCURRENCY )

    async def start_one_session (index ,phone ,s_data ):
        async with startup_semaphore :
            try :
                uid =int (s_data ["user_id"])
                if data_manager .is_banned (uid )or data_manager .is_invalid_session_uid (uid ):
                    return 
                if uid in ACTIVE_BOTS or uid in STARTING_BOTS :
                    return 
                STARTING_BOTS .add (uid )
                try :
                    await start_bot_instance (s_data ["string"],phone ,uid ,'stylized')
                    logger .debug (f"[{index }/{total_db }] Session started: {uid }")
                finally :
                    STARTING_BOTS .discard (uid )
            except Exception as e :
                logger .warning (f"Startup error for {phone }: {e }")

    async def startup_all_sessions ():
        tasks =[
        asyncio .create_task (start_one_session (i ,phone ,s_data ))
        for i ,(phone ,s_data )in enumerate (sessions_to_start ,1 )
        ]
        if tasks :
            await asyncio .gather (*tasks ,return_exceptions =True )
        active_count =len (ACTIVE_BOTS )
        asyncio .create_task (notify_admins (
        f"راه‌اندازی سلف‌ها به پایان رسید.\n"
        f"تعداد کل سشن‌های دیتابیس: {total_db }\n"
        f"سلف‌های با موفقیت متصل شده: {active_count }"
        ))
        logger .info (f"All sessions done: {active_count }/{total_db } active")

    asyncio .create_task (startup_all_sessions ())
    asyncio .create_task (_pemoji_premium_autostart ())
    asyncio .create_task (notify_admins (
    f"شروع لود {total_db } سشن در پس‌زمینه..."
    ))

    try :
        await idle ()
    except KeyboardInterrupt :
        logger .info ("دکمه Ctrl+C فشرده شد. در حال خاموش کردن ربات...")
    finally :
        logger .info ("توقف پروسه‌ها...")
        try :mem_task .cancel ()
        except Exception :pass 
        try :db_saver_task .cancel ()
        except Exception :pass 
        try :db_backup_task .cancel ()
        except Exception :pass 
        try :db_watch_task .cancel ()
        except Exception :pass 
        try :cpu_sampler_task .cancel ()
        except Exception :pass 

        data_manager .force_save_sync ()

        try :await manager_bot .stop ()
        except Exception :pass 

        if HTTP_SESSION and not HTTP_SESSION .closed :
            await HTTP_SESSION .close ()

        stop_tasks =[]
        for uid ,(client ,tsks )in list (ACTIVE_BOTS .items ()):
            for t in tsks :
                try :t .cancel ()
                except Exception :pass 
            stop_tasks .append (client .stop ())

        if stop_tasks :
            try :
                await asyncio .wait_for (asyncio .gather (*stop_tasks ,return_exceptions =True ),timeout =3.0 )
            except Exception :
                pass 

if __name__ == "__main__":
    try :
        loop = asyncio .get_event_loop ()
        loop .run_until_complete (main ())

    except KeyboardInterrupt :
        logger .info ("[سیستم] Ctrl+C دریافت شد؛ در حال خاموش‌سازی...")

    except asyncio .CancelledError :
        logger .info ("[سیستم] اجرای asyncio لغو شد.")

    except Exception :
        logger .exception ("[سیستم] خطای غیرمنتظره در اجرای اصلی برنامه")

    finally :
        try :
            data_manager .force_save_sync ()
        except Exception as exc :
            logger .warning ("[سیستم] ذخیره نهایی دیتابیس ناموفق بود: %s",exc )

        logger .info ("[سیستم] فرآیند اصلی به پایان رسید.")
