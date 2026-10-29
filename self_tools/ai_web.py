"""Web access for the AI: public-internet-only fetching, readable text extraction, search."""
import asyncio, ipaddress, re, socket
from html.parser import HTMLParser
from urllib.parse import parse_qs, unquote, urlparse, urljoin

MAX_BYTES = 1_500_000
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def is_public_ip(ip):
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return not (a.is_private or a.is_loopback or a.is_link_local or a.is_multicast or a.is_reserved or a.is_unspecified)


def valid_url(url):
    p = urlparse(url or "")
    return p.scheme in ("http", "https") and bool(p.hostname) and not p.username and p.port in (None, 80, 443, 8080, 8443)


async def resolve_public(host):
    infos = await asyncio.get_running_loop().getaddrinfo(host, None, type=socket.SOCK_STREAM)
    ips = {i[4][0] for i in infos}
    if not ips or not all(is_public_ip(i) for i in ips):
        raise ValueError("blocked-address")
    return ips


def make_safe_session():
    """aiohttp session whose resolver refuses non-public addresses at connect time (no DNS-rebinding gap)."""
    import aiohttp
    from aiohttp.abc import AbstractResolver

    class SafeResolver(AbstractResolver):
        def __init__(self):
            self.inner = aiohttp.ThreadedResolver()

        async def resolve(self, host, port=0, family=socket.AF_INET):
            res = await self.inner.resolve(host, port, family)
            ok = [r for r in res if is_public_ip(r["host"])]
            if not ok:
                raise OSError("blocked-address")
            return ok

        async def close(self):
            await self.inner.close()

    return aiohttp.ClientSession(connector=aiohttp.TCPConnector(resolver=SafeResolver(), limit=8),
                                 headers={"User-Agent": UA})


async def fetch(session, url, max_redirects=3, timeout=15):
    """GET a page (text only). Re-validates every redirect hop. -> (final_url, text)."""
    import aiohttp
    for _ in range(max_redirects + 1):
        if not valid_url(url):
            raise ValueError("bad-url")
        await resolve_public(urlparse(url).hostname)
        async with session.get(url, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
            if r.status in (301, 302, 303, 307, 308) and r.headers.get("Location"):
                url = urljoin(url, r.headers["Location"])
                continue
            if r.status != 200:
                raise ValueError("http-%d" % r.status)
            ctype = (r.headers.get("Content-Type") or "").lower()
            if not any(t in ctype for t in ("text/", "json", "xml")):
                raise ValueError("not-text")
            raw = await r.content.read(MAX_BYTES)
            enc = r.charset or "utf-8"
            return url, raw.decode(enc, "ignore")
    raise ValueError("too-many-redirects")


class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form", "iframe", "aside"}
    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr", "section", "article", "pre"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.title, self._in_title = [], 0, "", False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "title":
            self._in_title = True
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == "title":
            self._in_title = False
        if tag in self.BLOCK:
            self.out.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self.skip:
            self.out.append(data)


def html_to_text(html_text, limit=6000):
    p = _Text()
    try:
        p.feed(html_text)
    except Exception:
        pass
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(p.out))
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return p.title.strip(), text[:limit]


# ----------------------------------------------------------------- DuckDuckGo (HTML endpoint)
_RESULT = re.compile(r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.S)
_SNIP = re.compile(r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', re.S)


def _clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def parse_ddg(page):
    import html as _h
    links = _RESULT.findall(page)
    snips = _SNIP.findall(page)
    out = []
    for i, (href, title) in enumerate(links):
        href = _h.unescape(href)
        if "uddg=" in href:
            href = unquote(parse_qs(urlparse(href if href.startswith("http") else "https:" + href).query).get("uddg", [""])[0])
        if not valid_url(href):
            continue
        out.append({"url": href, "title": _h.unescape(_clean(title)),
                    "snippet": _h.unescape(_clean(snips[i])) if i < len(snips) else ""})
    return out


async def search(session, query, n=5):
    import aiohttp
    async with session.post("https://html.duckduckgo.com/html/", data={"q": query[:200], "kl": "wt-wt"},
                            timeout=aiohttp.ClientTimeout(total=15)) as r:
        if r.status != 200:
            raise ValueError("search-http-%d" % r.status)
        return parse_ddg(await r.text())[:n]


async def research(session, safe_session, query, pages=2):
    """Search, open the top pages in parallel and return numbered sources for the LLM."""
    hits = await search(session, query, 5)
    if not hits:
        return []

    async def grab(h):
        try:
            _, body = await fetch(safe_session, h["url"], timeout=12)
            _, text = html_to_text(body, 2500)
            return text
        except Exception:
            return ""
    texts = await asyncio.gather(*[grab(h) for h in hits[:pages]])
    for i, h in enumerate(hits):
        h["text"] = texts[i] if i < len(texts) and texts[i] else h["snippet"]
    return hits
