from pydantic import BaseModel
from typing import Literal

class MasterModel(BaseModel):
    code: str
    display: str
    is_active: Literal[True]


class DeleteMasterModel(BaseModel):
    is_active: bool


class UpdateMasterModel(BaseModel):
    code: str
    display: str
