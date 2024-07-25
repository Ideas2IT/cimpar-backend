import re
from pydantic import BaseModel, validator
from models.patient_validation import validate_phone_number


class EncounterModel(BaseModel):
    location: str 
    phone_number: str
    admission_date: str
    discharge_date: str
    reason: str
    primary_care_team: str
    treatment_summary: str
    follow_up_care: str
    activity_notes: str
    _validate_phone_number = validator('phone_number', allow_reuse=True)(validate_phone_number)



class EncounterUpdateModel(BaseModel):
    location: str 
    phone_number: str
    admission_date: str
    discharge_date: str
    reason: str
    primary_care_team: str
    treatment_summary: str
    follow_up_care: str
    activity_notes: str
    _validate_phone_number = validator('phone_number', allow_reuse=True)(validate_phone_number)

    

