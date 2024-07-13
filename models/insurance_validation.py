from pydantic import BaseModel
from typing import Optional


class CoverageModel(BaseModel):
    insurance_type: str
    groupNumber: Optional[str] = None
    policyNumber: Optional[str] = None
    providerName: Optional[str] = None


class CoverageUpdateModel(BaseModel):
    insurance_type: str
    providerName: Optional[str] = None
    policyNumber: Optional[str] = None
    groupNumber: Optional[str] = None

    
