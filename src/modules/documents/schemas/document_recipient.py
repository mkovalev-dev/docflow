import json,uuid
from typing import Annotated, List

from pydantic import BeforeValidator

from src.common.utils import is_uuid, to_uuid
from src.modules.documents.enums import DocumentPartyTypeEnum
from src.modules.documents.schemas.base import DocumentAddressCreateModel


def deserialize_recipients(v):
    if isinstance(v, list):
        if len(v) == 1 and isinstance(v[0], str):
            v = json.loads(v[0])
    elif isinstance(v, str):
        if is_uuid(v):
            return [
                {"user_id": uuid.UUID(v), "party_type": DocumentPartyTypeEnum.RECIPIENT}
            ]
        v = json.loads(v)

    if not isinstance(v, list):
        raise ValueError("Recipients must be a list of dicts or a UUID")

    return [
        {
            "user_id": to_uuid(item.get("user")),
            "organization_id": to_uuid(item.get("organization_id")),
            "external_user_id": to_uuid(item.get("external_person_id")),
            "is_responsible": item.get("is_responsible", False),
            "comment": item.get("comment"),
            "party_type": DocumentPartyTypeEnum.RECIPIENT,
        }
        for item in v
    ]


NormalizedRecipients = Annotated[
    List[DocumentAddressCreateModel], BeforeValidator(deserialize_recipients)
]
