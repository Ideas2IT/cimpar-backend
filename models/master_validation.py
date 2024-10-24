from pydantic import BaseModel
from typing import Literal

class MasterModel(BaseModel):
    code: str
    display: str
    service_type: str
    center_price: float
    home_price: float
    currency_symbol: Literal["$"] = "$"
    is_active: Literal[True]
    is_telehealth: bool


class DeleteMasterModel(BaseModel):
    is_active: bool


class UpdateMasterModel(BaseModel):
    code: str
    display: str
    service_type: str
    center_price: float
    home_price: float
    currency_symbol: Literal["$"] = "$"
    is_active: Literal[True]
    is_telehealth: bool


class UpdateMasterPrice(BaseModel):
    center_price: float
    home_price: float
