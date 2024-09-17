from pydantic import BaseModel
from typing import Optional

class MasterModel(BaseModel):
    code: str
    display: str