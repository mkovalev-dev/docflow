from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from src.adapters.http.user_client import User


class RegistrationModel(BaseModel):
    external_registration_number: Optional[str] = None
    external_registration_at: Optional[datetime] = None

    registration_number: Optional[str] = None
    at: Optional[datetime] = None
    registrator: Optional[User] = None
    is_registered: bool = False

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def from_orm_obj(cls, v):
        if isinstance(v, dict):
            return v

        reg_num_obj = getattr(v, "registration_number", None)

        return {
            "external_registration_number": getattr(
                v, "external_registration_number", None
            ),
            "external_registration_at": getattr(v, "external_registration_at", None),
            "registration_number": getattr(reg_num_obj, "full_name", None),
            "registration_at": getattr(reg_num_obj, "created_at", None),
            "registrator": None,
            "is_registered": True if reg_num_obj else False,
        }
