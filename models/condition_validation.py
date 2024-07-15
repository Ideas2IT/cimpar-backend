from pydantic import BaseModel
from typing import Optional, List

class Concept(BaseModel):
    code: str
    system: str
    display: str

class ConditionModel(BaseModel):
    current_condition: Optional[List[Concept]] = None
    additional_condition: Optional[List[Concept]] = None
    current_allergy: Optional[List[Concept]] = None
    additional_allergy: Optional[List[Concept]] = None
    family_condition: bool
    family_medical_condition: Optional[List[Concept]] = None

class ConditionUpdateModel(BaseModel):
    current_condition_id: Optional[str] = None
    additional_condition_id: Optional[str] = None
    current_allergy_id: Optional[str] = None
    additional_allergy_id: Optional[str] = None
    family_condition_id: Optional[str] = None
    current_condition: Optional[List[Concept]] = None
    additional_condition: Optional[List[Concept]] = None
    family_condition: bool
    current_allergy: Optional[List[Concept]] = None
    additional_allergy: Optional[List[Concept]] = None
    family_medical_condition: Optional[List[Concept]] = None



