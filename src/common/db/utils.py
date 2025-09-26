from typing import Type, Optional, Iterable

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base


async def exist_by(db: AsyncSession, model: Type[Base], *filters) -> bool:
    """Возвращает True/False есть ли хотя бы одна строка под условиями"""

    stmt = select(exists().where(*filters))

    return bool(await db.execute(stmt))


async def first(
    db: AsyncSession,
    model: Type[Base],
    *filters,
    order_by: Optional[Iterable] = None,
    options: Optional[Iterable] = None
):
    """Возвращает первый элемент"""
    stmt = select(model).where(*filters).limit(1)
    if order_by:
        stmt = stmt.order_by(*order_by)
    if options:
        stmt = stmt.options(*options)

    result = await db.execute(stmt)
    return result.scalars().first()
