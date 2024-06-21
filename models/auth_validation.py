from pydantic import BaseModel, Field
from aidbox.base import DomainResource, BackboneElement


class UserModel(BaseModel):
    id: str
    email: str
    password: str = "SecureRandom$2024!"
    role: str = "patient"


class TokenModel(BaseModel):
    client_id: str = Field(default="cimpar-client-jwt", exclude=True)
    grant_type: str = Field(default="password", exclude=True)
    username: str
    password: str


class RotateToken(BaseModel):
    client_id: str = Field(default="cimpar-client-jwt", exclude=True)
    grant_type: str = Field(default="refresh_token", exclude=True)
    refresh_token: str


class User(DomainResource):
    email: str
    password: str


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

