from __future__ import annotations

import httpx
from src.core.settings import get_settings

_http: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """
    Ленивая инициализация общего httpx.AsyncClient.
    Повторные вызовы возвращают один и тот же клиент (общий пул соединений).
    """
    global _http
    if _http is None or _http.is_closed:
        s = get_settings()
        _http = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=s.http_client.CONNECT_TIMEOUT_S,
                read=s.http_client.READ_TIMEOUT_S,
                write=s.http_client.WRITE_TIMEOUT_S,
                pool=s.http_client.POOL_LIMIT,
            ),
            limits=httpx.Limits(max_connections=s.http_client.POOL_LIMIT),
        )
    return _http


async def aclose_http_client() -> None:
    """Корректно закрыть клиент на shutdown."""
    global _http
    if _http and not _http.is_closed:
        await _http.aclose()
    _http = None
