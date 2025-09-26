from typing import Annotated

from pydantic import BeforeValidator

from src.common.utils import is_uuid, to_uuid
from src.modules.documents.enums import DocumentPartyTypeEnum
from src.modules.documents.schemas.base import DocumentAddressCreateModel
import uuid, json


def deserialize_sender(v):
    if isinstance(v, list):
        if len(v) == 1:
            v = v[0]
        else:
            raise ValueError("Sender list must contain only one item")

    if isinstance(v, str):
        if is_uuid(v):
            return {"user_id": uuid.UUID(v), "party_type": DocumentPartyTypeEnum.SENDER}
        v = json.loads(v)

    if not isinstance(v, dict):
        raise ValueError("Sender must be a UUID or dict")

    return {
        "organization_id": to_uuid(v.get("organization_id")),
        "external_user_id": to_uuid(v.get("external_person_id")),
        "party_type": DocumentPartyTypeEnum.SENDER,
    }


NormalizedSender = Annotated[
    DocumentAddressCreateModel, BeforeValidator(deserialize_sender)
]
