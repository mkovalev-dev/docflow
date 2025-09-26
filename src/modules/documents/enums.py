from src.common.enum import EnumData


class DocumentTypeEnum(EnumData):
    """Типы документов"""

    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"
    ASSIGNMENT = "ASSIGNMENT"
    ASSIGNMENT_INTERNAL = "ASSIGNMENT_INTERNAL"
    PROTOCOL = "PROTOCOL"
    ORDER = "ORDER"
    DIRECTIVE = "DIRECTIVE"
    NOTES = "NOTES"

    def get_russian_name(self):
        """Возвращает русскоязычное название типа документа"""
        russian_names = {
            self.INCOMING.value: "Входящий",
            self.OUTGOING.value: "Исходящий",
            self.ASSIGNMENT: "Поручение",
            self.ASSIGNMENT_INTERNAL.value: "Внутреннее поручение",
            self.PROTOCOL.value: "Протокол",
            self.ORDER.value: "Приказ",
            self.DIRECTIVE.value: "Распоряжение",
            self.NOTES.value: "Служебная записка",
        }
        return russian_names[self.value]

    
class DocumentTypesRequestEnum(EnumData):
    """Список slug документов в системе"""

    OUTGOING = "outgoing-correspondence"
    INCOMING = "incoming-correspondence"
    ASSIGNMENT = "assignment"
    ORDER = "order"
    PROTOCOL = "protocol"
    DIRECTIVE = "directive"


class DocumentPartyTypeEnum(EnumData):
    """Тип пользователя в документе"""

    SENDER = "SENDER"
    RECIPIENT = "RECIPIENT"


class DocumentConfidentialTypeEnum(EnumData):
    DOCUMENT_PRIVACY_LEVEL_OFFICIAL_USE_ONLY = (
        "ROLE_VSM_DOCFLOW_PRIVACY_LEVEL_OFFICIAL_USE_ONLY"
    )
    DOCUMENT_PRIVACY_LEVEL_CONFIDENTIAL = "ROLE_VSM_DOCFLOW_PRIVACY_LEVEL_CONFIDENTIAL"
    DOCUMENT_PRIVACY_LEVEL_COMMERCIAL_SECRET = (
        "ROLE_VSM_DOCFLOW_PRIVACY_LEVEL_COMMERCIAL_SECRET"
    )
    DOCUMENT_PRIVACY_LEVEL_PERSONAL_DATA = (
        "ROLE_VSM_DOCFLOW_PRIVACY_LEVEL_PERSONAL_DATA"
    )


class DocumentAccessTypeEnum(EnumData):
    READONLY = "READONLY"


class DocumentLinkTypeEnum(EnumData):
    """Тип связки с документом"""

    RELATED = "RELATED"
    ANSWER_TO = "ANSWER_TO"
