from math import ceil

from src.common.pagination.schema import T, PageOut


def make_page(items: list[T], total: int, page: int, limit: int) -> PageOut[T]:
    """
    Собрать PageOut из списка и total. page начинается с 1.
    """

    last = max(ceil(total / limit), 1) if total else 1
    page = max(min(page, last), 1)

    return PageOut[T](
        total=total,
        data=items,
        lastPage=last,
        perPage=limit,
        currentPage=page,
    )
