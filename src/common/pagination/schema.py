from typing import TypeVar, Generic, List

from fastapi import Query
from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.core.settings import get_settings

T = TypeVar("T")
_settings = get_settings()


class PageParams(BaseModel):
    """
    Query-параметры пагинации.
    Использование в эндпоинте: q: PageParams = Depends()
    """

    page: int = Field(
        default=Query(1, ge=1, description="Номер страницы (начиная с 1)")
    )
    per_page: int = Field(
        default=Query(
            _settings.pagination.DEFAULT_LIMIT,
            ge=1,
            le=_settings.pagination.MAX_LIMIT,
            description=f"Размер страницы (<= {_settings.pagination.MAX_LIMIT})",
        )
    )

    # на всякий случай «зажмём» limit в рантайме по текущим настройкам
    @field_validator("per_page")
    @classmethod
    def _cap_limit(cls, v: int) -> int:
        max_lim = _settings.pagination.MAX_LIMIT
        return min(v, max_lim)


class PageOut(BaseModel, Generic[T]):
    """
    Универсальная модель ответа с пагинацией.
    """

    total: int
    data: List[T]
    lastPage: int
    perPage: int
    currentPage: int
