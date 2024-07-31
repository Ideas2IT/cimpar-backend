import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timezone


def validate_date_of_birth(timestamp):
    try:
        utc_dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except (OverflowError, ValueError) as e:
        raise ValueError('Invalid DOB %s' %timestamp)
    return utc_dt


def validate_phone_number(phone_number: str) -> str:
    if not re.match(r'^\d{10}$', phone_number):
        raise ValueError('Phone number must be 10 digits')
    return phone_number


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
    id: Optional[str] = None
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
    createAccount: bool

    @field_validator('firstName', 'middleName', 'lastName', 'gender', 'city', 'state', 'country')
    def validate_name(cls, value):
        return validate_name(value)

    @field_validator('zipCode')
    def validate_zip_code(cls, value):
        return validate_zip_code(value)

    @field_validator('dob')
    def validate_date_of_birth(cls, value):
        return validate_date_of_birth(value)

    @field_validator('phoneNo')
    def validate_phone_number(cls, value):
        return validate_phone_number(value)


class PatientUpdateModel(BaseModel):
    firstName: str
    middleName: Optional[str] = ""
    lastName: Optional[str] = ""
    gender: str
    dob: int
    phoneNo: Optional[str] = None
    alternativeNumber: Optional[str] = ""
    city: Optional[str] = None
    zipCode: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    email: Optional[EmailStr] = ""
    height: Optional[str] = None
    weight: Optional[str] = None

    @field_validator('firstName', 'middleName', 'lastName', 'gender', 'city', 'state', 'country')
    def validate_name(cls, value):
        return validate_name(value)

    @field_validator('zipCode')
    def validate_zip_code(cls, value):
        return validate_zip_code(value)

    @field_validator('dob')
    def validate_date_of_birth(cls, value):
        return validate_date_of_birth(value)

    @field_validator('phoneNo')
    def validate_phone_number(cls, value):
        return validate_phone_number(value)