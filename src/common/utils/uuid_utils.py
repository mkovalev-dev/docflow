import uuid
from typing import Optional


def to_uuid(value: Optional[str]) -> Optional[uuid.UUID]:
    return uuid.UUID(value) if value else None


def is_uuid(val: str):
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False
