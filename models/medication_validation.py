from typing import List
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
    patient_id: str
    family_medications: str
    family_status: str

class MedicationUpdateModel(BaseModel):
    request: List[Concept]
    statement: List[Concept]
    request_approved: bool
    statement_approved: bool
    patient_id: str
    request_id: str
    statement_id: str
