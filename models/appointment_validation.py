from typing import List, Optional
from pydantic import BaseModel

class Concept(BaseModel):
    code: str
    system: str
    display: str

class AppoinmentModel(BaseModel):
    test_to_take: List[Concept]
    date_of_appoinment: str
    schedule_time: str
    reason_for_test: str
    other_reason: Optional[str] = None
    current_medical_condition: Optional[List[Concept]] = None
    other_medical_condition: Optional[List[Concept]] = None
    current_allergy: Optional[List[Concept]] = None
    other_allergy: Optional[List[Concept]] = None
    