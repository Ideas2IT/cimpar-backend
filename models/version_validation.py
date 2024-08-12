from typing import Optional
from pydantic import BaseModel

class VersionUpdateModel(BaseModel):
    andriod: Optional[str] = None
    ios: Optional[str] = None