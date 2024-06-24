from pydantic import BaseModel


class CoverageModel(BaseModel):
    status: str
    insurance_type: int
    provider_name: str
    policy_number: str
    group_number: str


class CoverageUpdateModel(BaseModel):
    status: str
    insurance_type: int
    provider_name: str
    policy_number: str
    group_number: str

    
