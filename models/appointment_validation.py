from typing import List, Optional, Literal
from pydantic import BaseModel


class Concept(BaseModel):
    code: str
    system: str
    display: str


class Test(BaseModel):
    code: str
    display: str


class AppoinmentModel(BaseModel):
    test_to_take: List[Test]
    date_of_appointment: str
    schedule_time: str
    reason_for_test: str
    other_reason: Optional[str] = None
    current_medical_condition: Optional[List[Concept]] = None
    other_medical_condition: Optional[List[Concept]] = None
    current_allergy: Optional[List[Concept]] = None
    other_allergy: Optional[List[Concept]] = None


class StatusModel(BaseModel):
    status: Literal['available']
