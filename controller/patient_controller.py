import logging
import traceback
from fastapi import Response, status, HTTPException
from fastapi.responses import JSONResponse

from aidbox.base import HumanName, Address, ContactPoint, Extension, Coding, Meta, Identifier, CodeableConcept
from aidbox.resource.patient import Patient_Contact, Patient_Communication

from constants import (
    PHONE_SYSTEM,
    EMAIL_SYSTEM,
    RACE_URL,
    TEXT,
    SYSTEM,
    ETHNICITY_URL,
    PATIENT_META_URL,
    IDENTIFIER_SYSTEM,
    IDENTIFIER_VALUE
)
from models.patient_validation import PatientModel, PatientUpdateModel
from HL7v2 import get_unique_patient_id_json, get_md5
from controller.auth_controller import AuthClient
from models.auth_validation import UserModel, User
from services.aidbox_resource_wrapper import Patient


logger = logging.getLogger("log")


class PatientClient:
    @staticmethod
    def create_patient(pat: PatientModel):
        try:
            patient_id = get_unique_patient_id_json(
                pat.first_name, pat.last_name, pat.date_of_birth
            )
            # As this is open API, and we won't get Token here, so using default AIDBOX API.
            from aidbox.resource.patient import Patient

            #####

            patient_id_update = get_md5(
                [pat.first_name, pat.last_name, pat.date_of_birth]
            )

            if Patient.get({"id": patient_id_update}):
                return HTTPException(
                    detail=f"Error: Patient with id {patient_id_update} already exists",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            patient = Patient(
                id=patient_id,
                name=[
                    HumanName(
                        family=pat.last_name, given=[pat.first_name, pat.middle_name]
                    )
                ],
                identifier=[Identifier(system=IDENTIFIER_SYSTEM, value=IDENTIFIER_VALUE)],
                gender=pat.gender,
                birthDate=pat.date_of_birth,
                contact=[
                    Patient_Contact(
                        telecom=[
                            ContactPoint(system=PHONE_SYSTEM, value=pat.phone_number),
                            ContactPoint(system=EMAIL_SYSTEM, value=pat.email),
                        ]
                    )
                ],
                address=[
                    Address(
                        city=pat.city,
                        postalCode=pat.zip_code,
                        text=pat.full_address,
                        state=pat.state,
                        country=pat.country,
                    )
                ],
                extension=[Extension(
                    url=RACE_URL,
                    extension=[
                        Extension(
                            url=TEXT,
                            valueString = pat.race,
                            valueCoding=Coding(
                                system=SYSTEM,
                                display=pat.race,
                            ),
                        )
                        ],
                    ),Extension(
                        url=ETHNICITY_URL,
                        extension=[
                            Extension(
                                url=TEXT,
                                valueString = pat.ethnicity,
                                valueCoding=Coding(
                                    system=SYSTEM,
                                    display=pat.ethnicity,
                                ),
                            )
                        ],
                    )
                ],
                communication=[Patient_Communication(language=CodeableConcept(coding=[Coding(system=PATIENT_META_URL, code=pat.height, display=pat.weight)]))]
            )
            patient.meta = Meta(
                profile = [PATIENT_META_URL]
            )
            patient.save()

            logger.debug("Patient saved successfully")
            response_data = {"id": patient.id, "created": True}
            if not User.get({"id": patient.id}):
                user = UserModel(email=pat.email, id=patient.id,
                                 name=pat.first_name + " " + pat.middle_name + " "+ pat.middle_name)
                response_data = AuthClient.create(user)
            logger.info(f"Added Successfully in DB: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Unable to create a patient: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create patient",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_patient_by_id(patient_id: str):
        try:
            patient_json = Patient.from_id(patient_id)
            patient = Patient(**patient_json)
            if patient:
                logger.info(f"Patient Found: {patient_id}")
                formatted_data = PatientClient.extract_patient_data(patient)
                return formatted_data
            return Response(
                content="Patient not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving patient: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve patient",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_all_patients():
        try:
            patients = Patient.get()
            if patients:
                logger.info(f"Patients Found: {len(patients)}")
                return patients
            return Response(
                content="Patients not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving patients: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve all patients",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def update_patient_by_id(pat: PatientUpdateModel, patient_id: str):
        try:
            patient = Patient(
                id=patient_id,
                name=[
                    HumanName(
                        family=pat.last_name, given=[pat.first_name, pat.middle_name]
                    )
                ],
                gender=pat.gender,
                birthDate=pat.date_of_birth,
                contact=[
                    Patient_Contact(
                        telecom=[
                            ContactPoint(system=PHONE_SYSTEM, value=pat.phone_number),
                            ContactPoint(system=EMAIL_SYSTEM, value=pat.email),
                        ]
                    )
                ],
                identifier=[Identifier(system=IDENTIFIER_SYSTEM, value=IDENTIFIER_VALUE)],
                address=[
                    Address(
                        city=pat.city,
                        postalCode=pat.zip_code,
                        text=pat.full_address,
                        state=pat.state,
                        country=pat.country,
                    )
                ],
                extension=[Extension(
                    url=RACE_URL,
                    extension=[
                        Extension(
                            url=TEXT,
                            valueString = pat.race,
                            valueCoding=Coding(
                                system=SYSTEM,
                                display=pat.race,
                            ),
                        )
                        ],
                    ),Extension(
                        url=ETHNICITY_URL,
                        extension=[
                            Extension(
                                url=TEXT,
                                valueString = pat.ethnicity,
                                valueCoding=Coding(
                                    system=SYSTEM,
                                    display=pat.ethnicity,
                                ),
                            )
                        ],
                    )
                ],
                communication=[Patient_Communication(language=CodeableConcept(coding=[Coding(system=PATIENT_META_URL, code=pat.height, display=pat.weight)]))]
            )
            patient.meta = Meta(
                profile = [PATIENT_META_URL]
            )
            patient.save()
            response_data = {"id": patient.id, "Updated": True}
            logger.info(f"Added Successfully in DB: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Unable to create a patient: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update patient",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def delete_patient_by_id(patient_id: str):
        try:
            patient = Patient(id=patient_id)
            if patient:
                logger.info(f"Deleting patient with id: {patient_id}")
                patient.delete()
                return {"message": f"Patient with id {patient_id} has been deleted."}
            return Response(
                content="Patient not found", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error : Unable to delete patient: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to delete patient",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def extract_patient_data(patient):
        extracted_data = {}

        # Extract id
        extracted_data["id"] = patient.id

        # Extract birthDate and convert to timestamp
        extracted_data["dob"] = patient.birthDate
        # extracted_data['dob'] = None
        # if patient.birthDate:
        #     # Convert birthDate to Unix timestamp (milliseconds)
        #     extracted_data['dob'] = int(datetime.fromisoformat(patient.birthDate).timestamp() * 1000)

        # Extract name components
        if patient.name:
            extracted_data["firstName"] = (
                patient.name[0].given[0] if patient.name[0].given else None
            )
            extracted_data["middleName"] = (
                patient.name[0].given[1] if len(patient.name[0].given) > 1 else None
            )
            extracted_data["lastName"] = patient.name[0].family
        else:
            extracted_data["firstName"] = None
            extracted_data["middleName"] = None
            extracted_data["lastName"] = None

        # Extract gender
        extracted_data["gender"] = patient.gender

        # Extract address components
        if patient.address:
            extracted_data["address"] = patient.address[0].text
            extracted_data["zipCode"] = patient.address[0].postalCode
            extracted_data["city"] = patient.address[0].city
            extracted_data["country"] = patient.address[0].country
            extracted_data["state"] = patient.address[0].state
        else:
            extracted_data["address"] = None
            extracted_data["zipCode"] = None
            extracted_data["city"] = None
            extracted_data["country"] = None
            extracted_data["state"] = None

        # Extract email and phoneNo from contact information
        if patient.contact:
            for telecom in patient.contact[0].telecom:
                if telecom.system == "email":
                    extracted_data["email"] = telecom.value
                elif telecom.system == "phone":
                    extracted_data["phoneNo"] = telecom.value
        else:
            extracted_data["email"] = None
            extracted_data["phoneNo"] = None

        # Extract race and ethnicity from extensions
        if patient.extension:
            for extension in patient.extension:
                if extension.url == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                    for inner_extension in extension.extension:
                        if inner_extension.url == "text":
                            extracted_data["race"] = inner_extension.valueString
                elif extension.url == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
                    for inner_extension in extension.extension:
                        if inner_extension.url == "text":
                            extracted_data["ethnicity"] = inner_extension.valueString
        else:
            extracted_data["race"] = None
            extracted_data["ethnicity"] = None

        # Extract Height and Weight from extensions
        if patient.communication:
            for communication in patient.communication:
                for coding in communication.language.coding:
                    extracted_data["height"] = coding.code
                    extracted_data["weight"] = coding.display
        else:
            extracted_data["height"] = None
            extracted_data["weight"] = None            

        # Extract lastUpdated timestamp
        extracted_data["lastUpdated"] = patient.meta.lastUpdated

        # Handle missing fields by defaulting to None
        default_fields = [
            "dob",
            "firstName",
            "middleName",
            "lastName",
            "gender",
            "address",
            "zipCode",
            "city",
            "country",
            "state",
            "email",
            "phoneNo",
            "race",
            "ethnicity",
            "height",
            "weight",
            "lastUpdated",
        ]
        for field in default_fields:
            if extracted_data.get(field) is None:
                extracted_data[field] = None

        return extracted_data
