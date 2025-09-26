from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response


class AuthHeaderContextMiddleware(BaseHTTPMiddleware):
    """Промежуточное программное обеспечение для сбора заголовков авторизации пользователя"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        session_id = request.cookies.get("SESSION", None)

        request.state.session_id = session_id

        return await call_next(request)
