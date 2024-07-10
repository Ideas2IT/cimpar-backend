from pydantic import BaseModel, Field
from aidbox.base import DomainResource


class UserModel(BaseModel):
    id: str
    email: str
    name: str
    password: str = "SecureRandom$2024!"
    role: str = "patient"


class TokenModel(BaseModel):
    client_id: str = Field(default="cimpar-client-jwt", exclude=True)
    grant_type: str = Field(default="password", exclude=True)
    username: str
    password: str


class ChangePassword(BaseModel):
    client_id: str = Field(default="cimpar-client-jwt", exclude=True)
    grant_type: str = Field(default="password", exclude=True)
    username: str
    old_password: str
    new_password: str


class RotateToken(BaseModel):
    client_id: str = Field(default="cimpar-client-jwt", exclude=True)
    grant_type: str = Field(default="refresh_token", exclude=True)
    refresh_token: str


class User(DomainResource):
    email: str
    inactive: bool


class AccessPolicy(DomainResource):
    engine: str = "allow"
    link: list


class PermissionEndpoint(BaseModel):
    uri: str
    action: list[str]


class Permission(BaseModel):
    engine: str
    endpoints: list[PermissionEndpoint]


class CimparRole(DomainResource):
    resourceType: str
    id: str
    name: str
    permissions: list[Permission]


class CimparPermission(DomainResource):
    user_id: dict
    cimpar_role: dict


class UserToken(DomainResource):
    user_id: str
    token: str
    token_expiration: str
