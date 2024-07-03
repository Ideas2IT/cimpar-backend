import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


def validate_date_of_birth(date_str: str) -> str:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError('date_of_birth must be in the format YYYY-MM-DD')
    return date_str


def validate_phone_number(phone_number: str) -> str:
    if not re.match(r'^\+1\d{10}$', phone_number):
        raise ValueError('Phone number must be in the format +1 followed by 10 digits')
    return phone_number


def validate_zip_code(zip_code: str) -> str:
    if not re.match(r'^\d{5}(-\d{4})?$', zip_code):
        raise ValueError('Zip code must be a valid 5-digit')
    return zip_code


def validate_name(name: str) -> str:
    if not re.match(r'^[A-Za-z]+(?: [A-Za-z]+)*$', name):
        raise ValueError('Name must  contain alphabetic characters and spaces alone')
    return name


class PatientModel(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: str
    date_of_birth: str
    phone_number: str
    city: str
    zip_code: str
    full_address: str
    state: str
    country: str
    race: str
    ethnicity: str
    email: EmailStr
    height: str
    weight: str
    _validate_first_name = validator('first_name', allow_reuse=True)(validate_name)
    _validate_middle_name = validator('middle_name', allow_reuse=True)(validate_name)
    _validate_last_name = validator('last_name', allow_reuse=True)(validate_name)
    _validate_gender = validator('gender', allow_reuse=True)(validate_name)  
    _validate_city = validator('city', allow_reuse=True)(validate_name)
    _validate_state = validator('state', allow_reuse=True)(validate_name)
    _validate_country = validator('country', allow_reuse=True)(validate_name)
    _validate_zip_code = validator('zip_code', allow_reuse=True)(validate_zip_code)
    _validate_date_of_birth = validator('date_of_birth', allow_reuse=True)(validate_date_of_birth)
    _validate_phone_number = validator('phone_number', allow_reuse=True)(validate_phone_number)


class PatientUpdateModel(BaseModel):
    patient_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: str
    date_of_birth: str
    phone_number: str
    city: str
    zip_code: str
    full_address: str
    state: str
    country: str
    race: str
    ethnicity: str
    email: EmailStr
    height: float
    weight: float
    _validate_first_name = validator('first_name', allow_reuse=True)(validate_name)
    _validate_middle_name = validator('middle_name', allow_reuse=True)(validate_name)
    _validate_last_name = validator('last_name', allow_reuse=True)(validate_name)
    _validate_gender = validator('gender', allow_reuse=True)(validate_name) 
    _validate_city = validator('city', allow_reuse=True)(validate_name)
    _validate_state = validator('state', allow_reuse=True)(validate_name)
    _validate_country = validator('country', allow_reuse=True)(validate_name)
    _validate_zip_code = validator('zip_code', allow_reuse=True)(validate_zip_code)
    _validate_date_of_birth = validator('date_of_birth', allow_reuse=True)(validate_date_of_birth)
    _validate_phone_number = validator('phone_number', allow_reuse=True)(validate_phone_number)
