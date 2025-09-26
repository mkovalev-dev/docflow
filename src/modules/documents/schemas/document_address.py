from __future__ import annotations
from typing import Optional, List, Tuple
from pydantic import BaseModel, ConfigDict, model_validator, ValidationInfo

from src.adapters.http.user_client import ExternalUser, Organization, User


class ExternalUserEntry(BaseModel):
    user: Optional[ExternalUser] = None
    organization: Optional[Organization] = None


class AddressGroups(BaseModel):
    users: List[User] = []
    external_users: List[ExternalUserEntry] = []
    organizations: List[Organization] = []

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def build_groups(cls, v, info: ValidationInfo):
        """
        v: None | ORM DocumentAddress | list[ORM DocumentAddress] | уже собранный dict
        context ожидает мапы:
          - users: dict[str|UUID, UserBrief]
          - external_users: dict[str|UUID, ExternalUserBrief]
          - organizations: dict[str|UUID, OrgBrief]
        """
        if v is None:
            return {"users": [], "external_users": [], "organizations": []}
        if isinstance(v, dict):
            return v

        addrs = v if isinstance(v, list) else [v]
        ctx = info.context or {}
        users_map = ctx.get("users", {}) or {}
        ext_map = ctx.get("external_users", {}) or {}
        orgs_map = ctx.get("organizations", {}) or {}

        users_out: list[User] = []
        external_out: list[ExternalUser] = []
        orgs_out: list[Organization] = []

        seen_users: set[str] = set()
        seen_ext: set[Tuple[Optional[str], Optional[str]]] = set()
        seen_orgs: set[str] = set()

        def _k(val) -> Optional[str]:
            if not val:
                return None
            return str(val)

        for a in addrs or []:
            uid = getattr(a, "user_id", None)
            oid = getattr(a, "organization_id", None)
            xid = getattr(a, "external_user_id", None)

            # users[]
            if uid:
                key = _k(uid)
                if key not in seen_users:
                    seen_users.add(key)
                    brief = users_map.get(key) or users_map.get(uid)
                    if brief:
                        users_out.append(brief)

            # organizations[] (только «чистая» организация)
            if oid and not uid and not xid:
                key = _k(oid)
                if key not in seen_orgs:
                    seen_orgs.add(key)
                    ob = orgs_map.get(key) or orgs_map.get(oid)
                    if ob:
                        orgs_out.append(ob)

            # external_users[] — пара (external_user, organization)
            if xid or (xid is not None and oid is not None):
                key = (_k(xid), _k(oid))
                if key not in seen_ext:
                    seen_ext.add(key)
                    eb = ext_map.get(key[0]) or ext_map.get(xid)
                    ob = orgs_map.get(key[1]) or orgs_map.get(oid)
                    external_out.append(ExternalUserEntry(user=eb, organization=ob))

        return {
            "users": users_out,
            "external_users": external_out,
            "organizations": orgs_out,
        }
