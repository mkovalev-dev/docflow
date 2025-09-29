from typing import Optional, Any


class DocumentError(Exception):
    """Базовое исключение для ошибок документооборота"""

    pass


class DocumentActionError(DocumentError):
    """Ошибка выполнения действия с документом"""

    def __init__(
        self,
        message: str = "Ошибка выполнения действия с документом",
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DocumentNotFoundError(DocumentError):
    """Документ не найден"""

    def __init__(self, document_id: Optional[str] = None):
        message = "Документ не найден"
        if document_id:
            message = f"Документ {document_id} не найден"
        super().__init__(message)


class PermissionDeniedError(DocumentError):
    """Отказ в доступе"""

    def __init__(self, message: str = "Недостаточно прав для выполнения действия"):
        super().__init__(message)


class DocumentValidationError(DocumentError):
    """Ошибка валидации документа"""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message)


class DocumentStateError(DocumentError):
    """Некорректное состояние документа для выполнения действия"""

    def __init__(self, current_state: str, required_state: Optional[str] = None):
        message = f"Некорректное состояние документа: {current_state}"
        if required_state:
            message = f"Документ должен быть в состоянии {required_state}, текущее состояние: {current_state}"
        super().__init__(message)
