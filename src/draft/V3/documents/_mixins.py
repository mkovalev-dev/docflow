from typing import ClassVar, Any, Optional
import uuid

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, declared_attr, relationship, backref


class RefDocumentMixin:
    """
    Добавляет:
      - document_id (FK -> documents_document.id, ON DELETE CASCADE)
      - document (child -> parent)
      - при задании __document_backref__ создаёт коллекцию у Document
    """

    __document_backref__: ClassVar[str]
    __document_backref_kwargs__: ClassVar[dict[str, Any]] = {
        "cascade": "all, delete-orphan",
        "passive_deletes": True,
        "lazy": "selectin",  # по желанию
    }
    __document_foreign_keys__: ClassVar[Optional[str]] = None

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents_document.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    @declared_attr
    def document(cls) -> Mapped["Document"]:
        kwargs = cls.__document_backref_kwargs__.copy()
        if cls.__document_foreign_keys__:
            kwargs["foreign_keys"] = cls.__document_foreign_keys__

        if cls.__document_backref__:
            return relationship(
                "Document",
                backref=backref(cls.__document_backref__, **kwargs),
                foreign_keys=cls.__document_foreign_keys__,
            )
        return relationship("Document", foreign_keys=cls.__document_foreign_keys__)
