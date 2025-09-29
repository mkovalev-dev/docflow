from enum import StrEnum


class DocumentPartyTypeEnum(StrEnum):
    """Тип пользователя в документе"""

    SENDER = "SENDER"
    RECIPIENT = "RECIPIENT"
