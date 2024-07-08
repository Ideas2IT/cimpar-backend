from typing import List
from typing import Optional
from pydantic import BaseModel


class Concept(BaseModel):
    code: str
    system: str
    display: str


class MedicationCreateModel(BaseModel):
    request: Optional[List[Concept]] = None
    statement: Optional[List[Concept]] = None
    request_approved: bool
    statement_approved: bool


class MedicationUpdateModel(BaseModel):
    request: Optional[List[Concept]] = None
    statement: Optional[List[Concept]] = None
    request_approved: bool
    statement_approved: bool
    request_id: Optional[str] = None
    statement_id: Optional[str] = None

