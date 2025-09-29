from enum import StrEnum


class DocumentTypeEnum(StrEnum):
    """Типы документов"""

    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"
    ASSIGNMENT = "ASSIGNMENT"
    ASSIGNMENT_INTERNAL = "ASSIGNMENT_INTERNAL"
    PROTOCOL = "PROTOCOL"
    ORDER = "ORDER"
    DIRECTIVE = "DIRECTIVE"
    NOTES = "NOTES"


DOCUMENT_TYPE_NAMES = {
    DocumentTypeEnum.INCOMING: "Входящий",
    DocumentTypeEnum.OUTGOING: "Исходящий",
    DocumentTypeEnum.ASSIGNMENT: "Поручение",
    DocumentTypeEnum.ASSIGNMENT_INTERNAL: "Внутреннее поручение",
    DocumentTypeEnum.PROTOCOL: "Протокол",
    DocumentTypeEnum.ORDER: "Приказ",
    DocumentTypeEnum.DIRECTIVE: "Распоряжение",
    DocumentTypeEnum.NOTES: "Служебная записка",
}


def get_name_document_type(document_type: DocumentTypeEnum) -> str:
    return DOCUMENT_TYPE_NAMES[document_type]


class DocumentTypesRequestEnum(StrEnum):
    """Список slug документов в системе"""

    OUTGOING = "outgoing-correspondence"
    INCOMING = "incoming-correspondence"
    ASSIGNMENT = "assignment"
    ORDER = "order"
    PROTOCOL = "protocol"
    DIRECTIVE = "directive"
