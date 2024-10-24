from pydantic import BaseModel
from typing import Literal

class LocationModel(BaseModel):
    city: str
    state: str
    pincode: str
    service_center_name: str
    is_active: bool


class LocationDeleteClient(BaseModel):
    is_active: Literal[False]


