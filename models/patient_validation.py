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
    if name and not re.match(r'^[A-Za-z]+$', name):
        raise ValueError('Name must contain alphabetic characters and spaces alone')   
    return name


class InsuranceDetail(BaseModel):
    providerName: Optional[str] = None
    policyNumber: Optional[str] = None
    groupNumber: Optional[str] = None


class PatientModel(BaseModel):
    id : Optional[str] = None
    firstName: str
    middleName: Optional[str] = ""
    lastName: Optional[str] = ""
    gender: str
    dob: int
    phoneNo: Optional[str] = None
    alternativeNumber: Optional[str] = ""
    city: str
    zipCode: str
    address: str
    state: str
    country: str
    race: str
    ethnicity: str
    email: Optional[EmailStr] = ""
    height: Optional[str] = None
    weight: Optional[str] = None
    haveInsurance: bool
    isPrimaryMember: bool
    primaryMemberName: Optional[str] = None
    primaryMemberDob: Optional[datetime] = None
    haveSecondaryInsurance: bool
    secondaryInsuranceDetails: InsuranceDetail
    insuranceDetails: InsuranceDetail
    createAccount : bool
    _validate_first_name = validator('firstName', allow_reuse=True)(validate_name)
    _validate_middle_name = validator('middleName', allow_reuse=True)(validate_name)
    _validate_last_name = validator('lastName', allow_reuse=True)(validate_name)
    _validate_gender = validator('gender', allow_reuse=True)(validate_name)  
    _validate_city = validator('city', allow_reuse=True)(validate_name)
    _validate_state = validator('state', allow_reuse=True)(validate_name)
    _validate_country = validator('country', allow_reuse=True)(validate_name)
    _validate_zip_code = validator('zipCode', allow_reuse=True)(validate_zip_code)
    _validate_date_of_birth = validator('dob', allow_reuse=True)(validate_date_of_birth)
    _validate_phone_number = validator('phoneNo', allow_reuse=True)(validate_phone_number)


class PatientUpdateModel(BaseModel):
    id : Optional[str] = None
    firstName: str
    middleName: Optional[str] = None
    lastName: str
    gender: str
    dob: str
    phoneNo: str
    alternativeNumber: Optional[str] = ""
    city: str
    zipCode: str
    address: str
    state: str
    country: str
    haveInsurance: bool
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    email: Optional[EmailStr] = ""
    height: Optional[str] = None
    weight: Optional[str] = None
    secondaryInsuranceDetails: InsuranceDetail
    insuranceDetails: InsuranceDetail
    isPrimaryMember: bool
    primaryMemberName: Optional[str] = None
    primaryMemberDob: Optional[datetime] = None
    _validate_first_name = validator('firstName', allow_reuse=True)(validate_name)
    _validate_middle_name = validator('middleName', allow_reuse=True)(validate_name)
    _validate_last_name = validator('lastName', allow_reuse=True)(validate_name)
    _validate_gender = validator('gender', allow_reuse=True)(validate_name) 
    _validate_city = validator('city', allow_reuse=True)(validate_name)
    _validate_state = validator('state', allow_reuse=True)(validate_name)
    _validate_country = validator('country', allow_reuse=True)(validate_name)
    _validate_zip_code = validator('zipCode', allow_reuse=True)(validate_zip_code)
    _validate_date_of_birth = validator('dob', allow_reuse=True)(validate_date_of_birth)
    _validate_phone_number = validator('phoneNo', allow_reuse=True)(validate_phone_number)
