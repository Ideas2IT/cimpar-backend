from pydantic import BaseModel


class EncounterModel(BaseModel):
    location: str 
    phone_number: str
    admission_date: str
    discharge_date: str
    reason: str
    primary_care_team: str
    treatment_summary: str
    follow_up_care: str
    status: str
    class_code: str


class EncounterUpdateModel(BaseModel):
    location: str 
    phone_number: str
    admission_date: str
    discharge_date: str
    reason: str
    primary_care_team: str
    treatment_summary: str
    status: str
    class_code: str
    

