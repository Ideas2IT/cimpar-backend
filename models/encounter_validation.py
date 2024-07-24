import re
from pydantic import BaseModel, validator

def validate_phone_number(phone_number: str) -> str:
    if not re.match(r'^\d{10}$', phone_number):
        raise ValueError('Phone number must be 10 digits')
    return phone_number

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

    

