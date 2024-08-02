import logging
import traceback
from fastapi import status
from fastapi.responses import JSONResponse

from aidbox.base import Reference, CodeableConcept, Coding, Annotation

from services.aidbox_service import AidboxApi
from services.aidbox_resource_wrapper import MedicationRequest
from services.aidbox_resource_wrapper import MedicationStatement
from models.medication_validation import MedicationCreateModel, MedicationUpdateModel
from constants import PATIENT_REFERENCE, INTEND, CURRENT, OTHER


logger = logging.getLogger("log")


class MedicationClient:
    @staticmethod
    def create_medication_statement(med: MedicationCreateModel, patient_id: str):
        current_status = "active" if med.statement_approved == True else "unknown"

        return MedicationStatement(
            medicationCodeableConcept=CodeableConcept(
                coding=[
                    Coding(
                        system=concept.system,
                        code=concept.code,
                        display=concept.display,
                    )
                    for concept in med.statement
                ]
            ),
            subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
            status=current_status,
            note=[Annotation(text=CURRENT)],
        )

    @staticmethod
    def create_medication_request(med: MedicationCreateModel, patient_id: str):
        history_status = "active" if med.request_approved == True else "unknown"

        return MedicationRequest(
            medicationCodeableConcept=CodeableConcept(
                coding=[
                    Coding(
                        system=concept.system,
                        code=concept.code,
                        display=concept.display,
                    )
                    for concept in med.request
                ]
            ),
            subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
            status=history_status,
            intent=INTEND,
            note=[Annotation(text=OTHER)],
        )

    @staticmethod
    def create_medication(med: MedicationCreateModel, patient_id: str):
        try:
            result = {}
            response_statement = MedicationStatement.make_request(
                    method="GET",
                    endpoint=f"/fhir/MedicationStatement/?subject=Patient/{patient_id}",
                )
            statement = response_statement.json()
            result["is_current_medication_exist"] = True if statement.get("total", 0) > 0 else False

            response_request = MedicationRequest.make_request(
                    method="GET",
                    endpoint=f"/fhir/MedicationRequest/?subject=Patient/{patient_id}",
                )
            request = response_request.json()
            result["is_other_medication_exist"] = True if request.get("total", 0) > 0 else False

            if med.request_approved and not result["is_other_medication_exist"]:
                medication_request = MedicationClient.create_medication_request(
                    med, patient_id
                )
                medication_request.save()
                result["other_medication_id"] = medication_request.id
            result["is_other_medication_exist"] = True

            if med.statement_approved and not result["is_current_medication_exist"]:
                medication_statement = MedicationClient.create_medication_statement(
                    med, patient_id
                )
                medication_statement.save()
                result["current_medication_id"] = medication_statement.id
            result["is_current_medication_exist"] = True
            result["created"] = True
            logger.info(f"Added Successfully in DB: {result}")

            return result
        except Exception as e:
            logger.error(
                f"Unable to create a medication request and statement: {str(e)}"
            )
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create medication",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_medication_by_patient_id(patient_id: str):
        try:
            result = {}
            response_statement = MedicationStatement.make_request(
                method="GET",
                endpoint=f"/fhir/MedicationStatement/?subject=Patient/{patient_id}&_sort=-lastUpdated",
            )
            response_request = MedicationRequest.make_request(
                method="GET",
                endpoint=f"/fhir/MedicationRequest/?subject=Patient/{patient_id}&_sort=-lastUpdated",
            )
            statement = response_statement.json()
            request = response_request.json()

            result["is_current_medication_exist"] = statement.get("total", 0) > 0
            result["current_medication"] = statement if result["is_current_medication_exist"] else []

            result["is_other_medication_exist"] = request.get("total", 0) > 0
            result["other_medication"] = request if result["is_other_medication_exist"] else []

            return result

        except Exception as e:
            logger.error(f"Unable to get a medication data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve medication",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def update_medication_by_patient_id(patient_id: str, med: MedicationUpdateModel):
        try:
            result = {} 

            current_status = "active" if med.statement_approved else "unknown"
            history_status = "active" if med.request_approved else "unknown"

            response_statement = MedicationStatement.make_request(
                    method="GET",
                    endpoint=f"/fhir/MedicationStatement/?subject=Patient/{patient_id}",
                )
            statement = response_statement.json()
            result["is_current_medication_exist"] = True if statement.get("total", 0) > 0 else False

            if not med.statement_approved:
                statement = response_statement.json()
                if response_statement.status_code == 404:
                    logger.info(f"Medication Not Found: {patient_id}")
                    return JSONResponse(
                        content={"Medication not found for patient"},
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                for entry in statement["entry"]:
                    resource = entry["resource"]
                    response_statement_data = MedicationStatement(**resource)
                    response_statement_data.delete()
                    result["medication_statement"] = "deleted"
            elif med.statement_id:
                create_med_statement = MedicationStatement(
                    id=med.statement_id,
                    medicationCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            ) for concept in med.statement
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    status=current_status,
                    note=[Annotation(text=CURRENT)],
                )
                create_med_statement.save()
                result["medication_statement_id"] = create_med_statement.id
            elif not med.statement_id and not result["is_current_medication_exist"]:
                medication_statement = MedicationStatement(
                    medicationCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            ) for concept in med.statement
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    status=history_status,
                    note=[Annotation(text=CURRENT)],
                )
                medication_statement.save()
                result["medication_statement_id"] = medication_statement.id

            response_request = MedicationRequest.make_request(
                    method="GET",
                    endpoint=f"/fhir/MedicationRequest/?subject=Patient/{patient_id}",
                )
            request = response_request.json()
            result["is_other_medication_exist"] = True if request.get("total", 0) > 0 else False

            if not med.request_approved:
                if response_request.status_code == 404:
                    logger.info(f"Medication Not Found: {patient_id}")
                    return JSONResponse(
                        content={"Medication not found for patient"},
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                for entry in request["entry"]:
                    resource = entry["resource"]
                    response_request_data = MedicationRequest(**resource)
                    response_request_data.delete()
                    result["medication_request"] = "deleted"
            elif med.request_id:
                medication_request = MedicationRequest(
                    id=med.request_id,
                    medicationCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            ) for concept in med.request
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    status=history_status,
                    intent=INTEND,
                    note=[Annotation(text=OTHER)],
                )
                medication_request.save()
                result["medication_request_id"] = medication_request.id
            elif not med.request_id and not result["is_other_medication_exist"]:
                medication_request = MedicationRequest(
                    medicationCodeableConcept=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                                ) for concept in med.request
                            ]
                        ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    status=current_status,
                    intent=INTEND,
                    note=[Annotation(text=OTHER)],
                )
                medication_request.save()
                result["medication_request_id"] = medication_request.id
            
            logger.info("Updated in DB")
            return result
        except Exception as e:
            logger.error(f"Unable to create a medication request and statement: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update medication",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def get_medications(medication_name: str):
        try:
            medication_list_snomed = AidboxApi.make_request(
                method="GET",
                endpoint=f"/fhir/Concept?.display$contains={medication_name}&.system=http://www.nlm.nih.gov/research/umls/rxnorm",
            )
            logger.info(f"Medication List: {medication_list_snomed}")
            data = medication_list_snomed.json()
            entries = data.get("entry", [])
            medications = [MedicationClient.extract_medication_info(entry) for entry in entries]
            return medications
        except Exception as e:
            logger.error(f"Unable to get medication list: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to get medication",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
        

    @staticmethod
    def get_medical_condition(medical_condition_name: str):
        try: 
            medical_condition = AidboxApi.make_request(
                method="GET",
                endpoint=f"/Concept?.display$contains={medical_condition_name}&.system=http://snomed.info/sct",
            )
            data = medical_condition.json()
            entries = data.get("entry", [])
            medical_condition_values = [MedicationClient.extract_medication_info(entry) for entry in entries]
            return medical_condition_values
        except Exception as e:
            logger.error(f"Unable to get medication list: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to get medication",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_404_NOT_FOUND
            )
        
    @staticmethod
    def extract_medication_info(entry):
        resource = entry.get("resource", {})
        medication_info = {
            "id": resource.get("id", ""),
            "system": resource.get("system", ""),
            "code": resource.get("code", ""),
            "display": resource.get("display", "")
        }
        return medication_info if medication_info["display"] else None
    