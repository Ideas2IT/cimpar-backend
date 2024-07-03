from pydantic import BaseModel
from typing import Optional

class Concept(BaseModel):
    code: str
    system: str
    display: str

class ConditionModel(BaseModel):
    current_condition: list[Concept]
    additional_condition: list[Concept]
    current_allergy: list[Concept]
    additional_allergy: list[Concept]
    family_condition: bool
    family_medications: list[Concept]

class ConditionUpdateModel(BaseModel):
    current_condition_id: Optional[str] = None
    additional_condition_id: Optional[str] = None
    current_allergy_id: Optional[str] = None
    additional_allergy_id: Optional[str] = None
    family_condition_id: Optional[str] = None
    current_condition: list[Concept]
    additional_condition: list[Concept]
    current_allergy: list[Concept]
    additional_allergy: list[Concept]
    family_condition: bool
    family_medications: list[Concept]



