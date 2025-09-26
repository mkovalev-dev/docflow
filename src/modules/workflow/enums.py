from src.common.enum import EnumData


class StepTypeEnum(EnumData):
    """Типы шагов"""

    REGISTRATION = "REGISTRATION"
    AGREEMENT = "AGREEMENT"
    SIGNING = "SIGNING"
    INTRODUCTION = "INTRODUCTION"
    DECISION = "DECISION"
    EXECUTION = "EXECUTION"
    REVOKE = "REVOKE"
    REVISION = "REVISION"


class StatusEnum(EnumData):
    """Статус выполнения"""

    WAITING = "WAITING"
    SENDED = "SENDED"
    IN_WORK = "IN_WORK"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    REVISION = "REVISION"
