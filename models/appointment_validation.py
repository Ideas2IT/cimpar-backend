from typing import List, Optional
from pydantic import BaseModel

class Concept(BaseModel):
    code: str
    system: str
    display: str

class AppoinmentModel(BaseModel):
    status: str
    participant_status: str
    test_to_take: List[Concept]
    date_of_appoinment: str
    schedule_time: str
    reason_for_test: str
    other_reason: str
    current_medication: Optional[List[Concept]] = None
    other_medication: Optional[List[Concept]] = None
    current_allergy: Optional[List[Concept]] = None