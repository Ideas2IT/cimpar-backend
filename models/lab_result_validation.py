from pydantic import BaseModel
from typing import Literal

class StatusModel(BaseModel):
    status: Literal['upcoming appointment', 'under processing', 'available']
    