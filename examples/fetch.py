"""Safe fetching so the agent never receives raw remote content.

Hardening: http/https only, every hop's host must resolve to public addresses,
redirects are re-validated, size and time are capped, only text-like content is read.
Known limit: DNS rebinding between this check and the actual connect is not fully
closed; for high-risk deployments also restrict egress at the network level.
"""
from __future__ import annotations

import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from salamander.integrations.gate import scan_and_gate

MAX_BYTES = 2_000_000
ALLOWED_TYPES = ("text/", "application/json", "application/xml", "application/xhtml+xml")


class FetchError(Exception):
    """Raised for any refused or failed fetch. Messages never contain remote content."""


def check_url(url: str) -> None:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise FetchError("only http/https URLs are allowed")
    host = parts.hostname
    if not host:
        raise FetchError("URL has no host")
    try:
        port = parts.port or (443 if parts.scheme == "https" else 80)
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, ValueError, UnicodeError) as exc:
        raise FetchError("host could not be resolved") from exc
    for info in infos:
        ip = ipaddress.ip_address(str(info[4][0]).split("%")[0])
        mapped = getattr(ip, "ipv4_mapped", None)
        if mapped is not None:
            ip = mapped
        if not ip.is_global:
            raise FetchError("URL resolves to a non-public address")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


def fetch_text(url: str, *, max_bytes: int = MAX_BYTES, timeout: float = 10.0,
               max_redirects: int = 3) -> str:
    # Proxies are disabled so the address we validated is the address we connect to.
    opener = urllib.request.build_opener(_NoRedirect, urllib.request.ProxyHandler({}))
    for _ in range(max_redirects + 1):
        check_url(url)
        request = urllib.request.Request(url, headers={"User-Agent": "salamander-gate/0.1"})
        try:
            response = opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308):
                location = exc.headers.get("Location")
                if not location:
                    raise FetchError("redirect without location") from exc
                url = urllib.parse.urljoin(url, location)
                continue
            raise FetchError(f"HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise FetchError("network error") from exc
        with response:
            ctype = response.headers.get_content_type()
            if not ctype.startswith(ALLOWED_TYPES):
                raise FetchError(f"unsupported content type: {ctype}")
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise FetchError("response too large")
            charset = response.headers.get_content_charset() or "utf-8"
        try:
            return data.decode(charset, errors="replace")
        except LookupError:
            return data.decode("utf-8", errors="replace")
    raise FetchError("too many redirects")


def fetch_and_gate(url: str, *, mode: str = "refuse", allow_suspicious: bool = True,
                   scanner: Any = None) -> dict[str, Any]:
    try:
        text = fetch_text(url)
    except FetchError as exc:
        return {"allowed": False, "verdict": "error", "score": None, "categories": [],
                "content": None, "reason": str(exc), "url": url}
    result = scan_and_gate(text, mode=mode, allow_suspicious=allow_suspicious, scanner=scanner)
    result["url"] = url
    return result
