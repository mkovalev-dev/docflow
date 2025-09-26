from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.core.settings import get_settings

settings = get_settings()


# Единая схема именования ограничений — стабильные имена для Alembic/диагностики
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """База для всех ORM-моделей сервиса документов."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # не навязываем __tablename__, обычно вы укажете его в модели явно.
    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[override]
        return cls.__name__.lower()


# Async Engine / Session factory
engine: AsyncEngine = create_async_engine(
    settings.db.database_url,
    echo=settings.db.ECHO,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Зависимость для FastAPI (если хочется использовать прямо отсюда):
        async def endpoint(db: AsyncSession = Depends(get_session)): ...
    Коммит/rollback — на слое сервисов.
    """
    async with SessionLocal() as session:
        yield session


__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_session",
]
