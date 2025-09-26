from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression

from src.adapters.http.user_client import User, UserClient
from src.common.pagination import make_page, PageParams
from src.core.auth import get_current_user
from src.core.db import get_session
from src.modules.documents.enums import DocumentTypesRequestEnum
from src.modules.documents.models import Document
from src.modules.documents.schemas.document_create import DocumentCreateSchema
from src.modules.documents.schemas.document_list_item import (
    DocumentListItem,
)
from src.modules.documents.services.document_create import DocumentCreateService
from src.modules.documents.utils import collect_party_ids
import asyncio, uuid

from src.modules.workflow.actions.workflow_activate_service import (
    WorkflowActivateService,
)
from src.modules.workflow.utils import document_status_expression

router = APIRouter(prefix="/correspondence", tags=["documents"])


@router.post("/list")
async def get_documents(
    request: Request,
    page_params: PageParams = Depends(),
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Контракт для получения списка документов у пользователя"""

    expr = document_status_expression(user.id)

    query = select(Document).options(with_expression(Document.document_status, expr))

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    offset = (page_params.page - 1) * page_params.per_page

    result = await db.execute(
        query.order_by(Document.created_at.desc())
        .offset(offset)
        .limit(page_params.per_page)
    )
    docs = result.scalars().all()
    user_ids, external_user_ids, org_ids = collect_party_ids(docs)
    user_client = UserClient(
        session_id=request.cookies.get("SESSION"),
    )
    users, organizations, external_users = await asyncio.gather(
        user_client.get_users(ids=user_ids),
        user_client.get_organizations(ids=org_ids),
        user_client.get_external_users(ids=external_user_ids),
    )
    items = [
        DocumentListItem.model_validate(
            d,
            from_attributes=True,
            context={
                "users": users,
                "organizations": organizations,
                "external_users": external_users,
            },
        )
        for d in docs
    ]

    return make_page(
        items,
        total,
        page_params.page,
        page_params.per_page,
    )


@router.get("/{id}/detail", response_model=DocumentListItem)
async def get_document_detail(
    id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Контракт для получения документа у пользователя"""

    expr = document_status_expression(user.id)

    query = (
        select(Document)
        .where(Document.id == id)
        .options(with_expression(Document.document_status, expr))
    )
    result = await db.execute(query)
    doc = result.scalars().first()

    user_ids, external_user_ids, org_ids = collect_party_ids([doc])
    user_client = UserClient(
        session_id=request.cookies.get("SESSION"),
    )
    users, organizations, external_users = await asyncio.gather(
        user_client.get_users(ids=user_ids),
        user_client.get_organizations(ids=org_ids),
        user_client.get_external_users(ids=external_user_ids),
    )

    return DocumentListItem.model_validate(
        doc,
        from_attributes=True,
        context={
            "users": users,
            "organizations": organizations,
            "external_users": external_users,
        },
    )


@router.post(
    "/{document_type}",
)
async def create_new_document(
    document_type: DocumentTypesRequestEnum,
    data: Annotated[DocumentCreateSchema, Form()],
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    document_create_service = DocumentCreateService(
        db=db, document_type=document_type, user=user, request=request
    )
    document = await document_create_service.create_document(
        data=data,
    )
    await WorkflowActivateService(document_id=document.id, db=db).execute()
    # TODO: далее конфиденциальность и воркфлоу
    # Todo: инфу о юзерах получать списком из запроса и дальше через контекст подставлять в нужное
    print(1)
