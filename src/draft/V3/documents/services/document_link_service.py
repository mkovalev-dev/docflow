import uuid
from typing import Optional, List

from src.modules.documents.enums import DocumentLinkTypeEnum
from src.modules.documents.models import DocumentLink


class DocumentLinkService:

    def __init__(self):
        pass

    async def execute(
        self,
        answer_to: Optional[List[uuid.UUID]] = [],
        related_to: Optional[List[uuid.UUID]] = [],
    ) -> List[DocumentLink]:
        links: List[DocumentLink] = []

        for answer in answer_to:
            links.append(
                DocumentLink(
                    document_id=uuid.UUID(answer),
                    link_type=DocumentLinkTypeEnum.ANSWER_TO,
                    target_id=answer,
                )
            )
        return []
