"""Browser-grade TLS transport for httpx using curl_cffi.

Cloudflare and X detect Python's default TLS fingerprint (JA3/JA4)
and block requests from httpx/httpcore. This module replaces httpx's
default transport with curl_cffi, which impersonates a real Chrome
browser at the TLS level.

The replacement is transparent: httpx still handles cookies, redirects,
and header management. Only the underlying TCP/TLS connection is routed
through curl_cffi.
"""
from __future__ import annotations

import httpx
from curl_cffi.requests import AsyncSession

_curl_session: AsyncSession | None = None

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
)


def _get_curl_session() -> AsyncSession:
    global _curl_session
    if _curl_session is None:
        _curl_session = AsyncSession(impersonate="chrome")
    return _curl_session


async def curl_cffi_transport(self, request: httpx.Request) -> httpx.Response:
    """Drop-in replacement for AsyncHTTPTransport.handle_async_request.

    Routes the HTTP request through curl_cffi with Chrome TLS fingerprint
    while letting httpx manage cookies, redirects, and headers.
    """
    session = _get_curl_session()
    session.cookies.clear()

    headers = dict(request.headers)
    headers.pop("host", None)

    ua = headers.get("user-agent", "")
    if not ua or ua.startswith("python-httpx"):
        headers["user-agent"] = BROWSER_UA

    content = request.content if request.content else None

    resp = await session.request(
        method=request.method,
        url=str(request.url),
        headers=headers,
        content=content,
        allow_redirects=False,
    )

    # curl_cffi decompresses automatically; strip encoding headers
    # so httpx doesn't try to decompress again.
    resp_headers = [
        (k, v) for k, v in resp.headers.multi_items()
        if k.lower() not in ("content-encoding", "transfer-encoding")
    ]

    return httpx.Response(
        status_code=resp.status_code,
        headers=resp_headers,
        content=resp.content,
        request=request,
    )


def install():
    """Replace httpx's default transport with curl_cffi.

    Call this once at import time. All subsequent httpx requests
    will use Chrome-grade TLS.
    """
    httpx.AsyncHTTPTransport.handle_async_request = curl_cffi_transport
