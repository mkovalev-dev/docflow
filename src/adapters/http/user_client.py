from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel

from src.adapters.http.client import get_http_client
from src.common.enum import EnumData
from src.common.enum.user_roles import UserRolesEnum
from src.core.settings import get_settings
import uuid, json


class User(BaseModel):
    id: uuid.UUID
    avatar: Optional[str] = None
    status_text: str
    department: str
    email: str
    username: str
    full_name: str
    job_title: str
    roles: list[str]


class ExternalUserOrganization(BaseModel):
    id: uuid.UUID
    name: str


class ExternalUser(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    middle_name: str | None = None
    is_active: bool
    created_at: datetime
    role: str
    organizations: List[ExternalUserOrganization]


class Organization(BaseModel):
    id: uuid.UUID
    name: str
    is_active: bool
    inn_number: str
    kpp_number: str


class UserClient:
    """Клиент для взаимодействия с сервисом пользователей"""

    def __init__(self, session_id: str):
        self.settings = get_settings()
        self._http = get_http_client()
        self.session_id = session_id

    def request(self):
        cookies = {"SESSION": self.session_id}
        self._http.cookies.update(cookies)
        return self._http

    async def get_current_user(self) -> User:
        """Возвращает текущего пользователя в системе"""

        response = await self.request().get(
            url=f"{self.settings.services.USERS_SERVICE_URL}/current-user-info"
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return User.model_validate(response.json())

    async def get_users(self, ids: list) -> dict[str, User]:
        data = {}
        response = await self.request().post(
            url=f"{self.settings.services.USERS_SERVICE_URL}/event-users-info",
            json={"ids": list(set(ids))},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        if response_data := response.json():
            for user in response_data:
                user = User.model_validate(user)
                data[str(user.id)] = user
        return data

    async def get_organizations(self, ids: list) -> dict[str, User]:
        data = {}
        response = await self.request().post(
            url=f"{self.settings.services.USERS_SERVICE_URL}/event-organizations-info",
            json={"ids": list(ids)},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        if response_data := response.json():
            for organization in response_data:
                organization = Organization.model_validate(organization)
                data[str(organization.id)] = organization
        return data

    async def get_external_users(self, ids: list) -> dict[str, User]:
        data = {}
        response = await self.request().post(
            url=f"{self.settings.services.USERS_SERVICE_URL}/event-external-users-info",
            json={"ids": list(ids)},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        if response_data := response.json():
            for external_user in response_data:
                external_user = ExternalUser.model_validate(external_user)
                data[str(external_user.id)] = external_user
        return data

    async def get_user_ids_from_role(self, role: UserRolesEnum) -> list[uuid.UUID]:
        response = await self.request().post(
            url=f"{self.settings.services.USERS_SERVICE_URL}/users-by-role",
            json={"role": role},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return [uuid.UUID(id) for id in response.json()]
