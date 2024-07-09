import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, timezone


def validate_date_of_birth(timestamp: int) -> str:
    timestamp = int(timestamp)
    dob_datetime = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    if dob_datetime > datetime.now(timezone.utc):
        raise ValueError('Date of birth cannot be in the future.')
    return dob_datetime.strftime('%Y-%m-%d')


def validate_phone_number(phone_number: str) -> str:
    if not re.match(r'^\d{10}$', phone_number):
        raise ValueError('Phone number must be 10 digits')
    return f"+1{phone_number}"


def validate_zip_code(zip_code: str) -> str:
    if not re.match(r'^\d{5}$', zip_code):
        raise ValueError('Zip code must be a valid 5-digit')
    return zip_code


def validate_name(name: str) -> str:
    if not re.match(r'^[A-Za-z]+(?: [A-Za-z]+)*$', name):
        raise ValueError('Name must  contain alphabetic characters and spaces alone')
    return name


class PatientModel(BaseModel):
    firstName: str
    middleName: Optional[str] = None
    lastName: str
    gender: str
    dob: int
    regPhoneNo: str
    city: str
    zipCode: str
    address: str
    state: str
    country: str
    race: str
    ethnicity: str
    regEmail: EmailStr
    height: str
    weight: str
    _validate_first_name = validator('firstName', allow_reuse=True)(validate_name)
    _validate_middle_name = validator('middleName', allow_reuse=True)(validate_name)
    _validate_last_name = validator('lastName', allow_reuse=True)(validate_name)
    _validate_gender = validator('gender', allow_reuse=True)(validate_name)  
    _validate_city = validator('city', allow_reuse=True)(validate_name)
    _validate_state = validator('state', allow_reuse=True)(validate_name)
    _validate_country = validator('country', allow_reuse=True)(validate_name)
    _validate_zip_code = validator('zipCode', allow_reuse=True)(validate_zip_code)
    _validate_date_of_birth = validator('dob', allow_reuse=True)(validate_date_of_birth)
    _validate_phone_number = validator('regPhoneNo', allow_reuse=True)(validate_phone_number)


class PatientUpdateModel(BaseModel):
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
