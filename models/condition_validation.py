from pydantic import BaseModel


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
    current_condition_id: str
    additional_condition_id: str
    current_allergy_id: str
    additional_allergy_id: str
    family_condition_id: str
    current_condition: list[Concept]
    additional_condition: list[Concept]
    current_allergy: list[Concept]
    additional_allergy: list[Concept]
    family_condition: bool
    family_medications: list[Concept]



