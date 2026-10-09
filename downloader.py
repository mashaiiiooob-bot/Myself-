#!/usr/bin/env python3
"""
HAJINOA Downloader Module (hardened)
------------------------------------
yt-dlp based downloader used by the self bot. No Telegram code in here.

Differences from the first version:
  * every download runs in its own temp directory (no mixing/races between downloads)
  * the real output path comes from yt-dlp (requested_downloads), not from glob guesses
    (the old `*[id].*` glob treated [id] as a character class and never matched)
  * size / duration limits are checked BEFORE downloading
  * refuses private / loopback / link-local addresses (SSRF protection)
  * works without ffmpeg (single-file formats, original audio instead of MP3)
  * optional cookies (YTDLP_COOKIES file path or YTDLP_COOKIES_B64) for sites that need login

Env: DL_MAX_HEIGHT (720) DL_MAX_MB (1900) DL_MAX_MINUTES (180) DL_ALLOW_PRIVATE (0)
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import ipaddress
import os
import re
import shutil
import socket
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:
    import yt_dlp
except ImportError as exc:  # pragma: no cover
    raise SystemExit("yt-dlp is not installed. Run: pip install -U yt-dlp") from exc

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
DEFAULT_DIR = Path(tempfile.gettempdir()) / "self_downloads"


class DownloaderError(RuntimeError):
    """Raised when a download cannot be completed."""


@dataclass
class DownloadResult:
    path: Path
    workdir: Path
    title: str = ""
    duration: int = 0
    width: int = 0
    height: int = 0
    is_audio: bool = False
    size: int = 0


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "") or default)
    except ValueError:
        return default


def extract_url(text: str) -> Optional[str]:
    """Return the first HTTP(S) URL found in text."""
    if not text:
        return None
    match = URL_RE.search(text)
    if not match:
        return None
    return match.group(0).rstrip(".,!?;:)]}،؛")


def is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def is_public_url(url: str) -> bool:
    """False for localhost / private / link-local / metadata addresses."""
    if os.environ.get("DL_ALLOW_PRIVATE", "0") == "1":
        return True
    try:
        host = urlparse(url).hostname
        if not host:
            return False
        for info in socket.getaddrinfo(host, None):
            if not ipaddress.ip_address(info[4][0].split("%")[0]).is_global:
                return False
        return True
    except Exception:
        return False


def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _cookies_file() -> Optional[str]:
    path = os.environ.get("YTDLP_COOKIES", "").strip()
    if path and os.path.exists(path):
        return path
    b64 = os.environ.get("YTDLP_COOKIES_B64", "").strip()
    if b64:
        target = Path(tempfile.gettempdir()) / "ytdlp_cookies.txt"
        try:
            target.write_bytes(base64.b64decode(b64))
            return str(target)
        except Exception:
            return None
    return None


def _options(workdir: Path, audio: bool) -> dict:
    height = _env_int("DL_MAX_HEIGHT", 720)
    ffmpeg = check_ffmpeg()
    opts = {
        "outtmpl": str(workdir / "%(title).80B [%(id)s].%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "retries": 2,
        "fragment_retries": 2,
        "socket_timeout": 30,
        "max_filesize": _env_int("DL_MAX_MB", 1900) * 1024 * 1024,
    }
    if audio:
        if ffmpeg:
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
    elif ffmpeg:
        opts["format"] = (f"bv*[height<={height}][ext=mp4]+ba[ext=m4a]/b[height<={height}][ext=mp4]/"
                          f"bv*[height<={height}]+ba/b[height<={height}]/b")
        opts["merge_output_format"] = "mp4"
    else:
        opts["format"] = f"b[height<={height}][ext=mp4]/b[ext=mp4]/b"
    cookies = _cookies_file()
    if cookies:
        opts["cookiefile"] = cookies
    return opts


def prune(base_dir: str | Path = DEFAULT_DIR, max_age: int = 3 * 3600) -> None:
    """Remove stale download folders left behind by crashes."""
    try:
        base = Path(base_dir)
        now = time.time()
        for p in base.glob("dl_*"):
            if p.is_dir() and now - p.stat().st_mtime > max_age:
                shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass


def download_media(url: str, audio: bool = False, output_dir: str | Path = DEFAULT_DIR,
                   max_bytes: Optional[int] = None) -> DownloadResult:
    """Download one video (or audio) into a fresh folder. Caller must call cleanup()."""
    if not is_http_url(url):
        raise DownloaderError("لینک معتبر نیست.")
    if not is_public_url(url):
        raise DownloaderError("این آدرس مجاز نیست.")

    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)
    prune(base)
    workdir = Path(tempfile.mkdtemp(prefix="dl_", dir=base))
    opts = _options(workdir, audio)
    limit = max_bytes or opts["max_filesize"]
    opts["max_filesize"] = limit
    max_minutes = _env_int("DL_MAX_MINUTES", 180)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise DownloaderError("اطلاعاتی از این لینک پیدا نشد.")
            if info.get("entries"):
                entries = [e for e in info["entries"] if e]
                if not entries:
                    raise DownloaderError("ویدیویی در این لینک پیدا نشد.")
                info = entries[0]
            duration = int(info.get("duration") or 0)
            if duration and duration > max_minutes * 60:
                raise DownloaderError(f"ویدیو بیش از {max_minutes} دقیقه است.")
            approx = info.get("filesize") or info.get("filesize_approx") or 0
            if approx and approx > limit and not audio:
                raise DownloaderError("حجم فایل از سقف مجاز بیشتر است.")
            done = ydl.process_ie_result(info, download=True)

        files = (done or {}).get("requested_downloads") or []
        path = None
        for f in files:
            fp = f.get("filepath")
            if fp and Path(fp).exists():
                path = Path(fp)
                break
        if path is None:  # fallback: biggest file in this download's own folder
            found = sorted((p for p in workdir.iterdir() if p.is_file() and not p.name.endswith((".part", ".ytdl"))),
                           key=lambda p: p.stat().st_size, reverse=True)
            if not found:
                raise DownloaderError("فایلی دانلود نشد (احتمالاً حجم از سقف مجاز بیشتر است).")
            path = found[0]
        return DownloadResult(path=path, workdir=workdir, title=str(info.get("title") or "")[:200],
                              duration=duration, width=int(info.get("width") or 0), height=int(info.get("height") or 0),
                              is_audio=audio or path.suffix.lower() in {".mp3", ".m4a", ".opus", ".ogg"},
                              size=path.stat().st_size)
    except DownloaderError:
        shutil.rmtree(workdir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(workdir, ignore_errors=True)
        raise DownloaderError(f"Download failed: {exc}") from exc


def cleanup(result: Optional[DownloadResult]) -> None:
    if result:
        shutil.rmtree(result.workdir, ignore_errors=True)


# ---- backward compatible API (first version) -------------------------------------------
def download_video(url: str, output_dir: str | Path = DEFAULT_DIR) -> Path:
    """Returns the file path; the caller removes it with safe_remove()."""
    return download_media(url, False, output_dir).path


def download_audio(url: str, output_dir: str | Path = DEFAULT_DIR) -> Path:
    return download_media(url, True, output_dir).path


def safe_remove(path: str | Path | None) -> None:
    """Delete a downloaded file (and its private download folder)."""
    if not path:
        return
    try:
        p = Path(path)
        p.unlink(missing_ok=True)
        if p.parent.name.startswith("dl_"):
            shutil.rmtree(p.parent, ignore_errors=True)
    except OSError:
        pass


async def async_download_media(url: str, audio: bool = False, output_dir: str | Path = DEFAULT_DIR,
                               max_bytes: Optional[int] = None) -> DownloadResult:
    return await asyncio.to_thread(download_media, url, audio, output_dir, max_bytes)


async def async_download_video(url: str, output_dir: str | Path = DEFAULT_DIR) -> Path:
    return await asyncio.to_thread(download_video, url, output_dir)


async def async_download_audio(url: str, output_dir: str | Path = DEFAULT_DIR) -> Path:
    return await asyncio.to_thread(download_audio, url, output_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="HAJINOA standalone yt-dlp downloader")
    parser.add_argument("url", help="HTTP(S) media URL")
    parser.add_argument("--audio", action="store_true", help="Download audio (MP3 when ffmpeg is available)")
    parser.add_argument("--output-dir", default=str(DEFAULT_DIR))
    args = parser.parse_args()
    url = extract_url(args.url)
    if not url:
        print("ERROR: No valid HTTP(S) URL found.")
        return 2
    try:
        print(download_media(url, args.audio, args.output_dir).path)
        return 0
    except DownloaderError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
