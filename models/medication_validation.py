from typing import List
from typing import Optional
from pydantic import BaseModel


class Concept(BaseModel):
    code: str
    system: str
    display: str


class MedicationCreateModel(BaseModel):
    request: List[Concept]
    statement: List[Concept]
    request_approved: bool
    statement_approved: bool
    family_medications: str
    family_status: str


class MedicationUpdateModel(BaseModel):
    request: List[Concept]
    statement: List[Concept]
    request_approved: bool
    statement_approved: bool
    request_id: Optional[str] = None
    statement_id: Optional[str] = None

