from fastapi import Request

from src.adapters.http.user_client import UserClient, User


async def get_current_user(request: Request) -> User:
    """Получение авторизованного пользователя"""
    user_client = UserClient(
        session_id=request.cookies.get("SESSION"),
    )
    user = await user_client.get_current_user()
    request.state.user = user

    return user
