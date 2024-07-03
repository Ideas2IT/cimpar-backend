import logging
import traceback
from fastapi import Response, status
from fastapi.responses import JSONResponse

from aidbox.base import Reference, CodeableConcept, Coding, Annotation

from services.aidbox_service import AidboxApi
from services.aidbox_resource_wrapper import MedicationRequest
from services.aidbox_resource_wrapper import MedicationStatement
from models.medication_validation import MedicationCreateModel, MedicationUpdateModel
from constants import PATIENT_REFERENCE, INTEND, CURRENT_MEDICATION, OTHER_MEDICATION


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
            note=[Annotation(text=CURRENT_MEDICATION)],
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
            note=[Annotation(text=OTHER_MEDICATION)],
        )

    @staticmethod
    def create_medication(med: MedicationCreateModel, patient_id: str):
        try:
            medication_request = MedicationClient.create_medication_request(
                med, patient_id
            )
            medication_request.save()

            medication_statement = MedicationClient.create_medication_statement(
                med, patient_id
            )
            medication_statement.save()

            response_data = {
                "medication_request_id": medication_request.id,
                "medication_statement_id": medication_statement.id,
                "created": True,
            }
            logger.info(f"Added Successfully in DB: {response_data}")
            return response_data
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
            response_statement = MedicationStatement.make_request(
                method="GET",
                endpoint=f"/fhir/MedicationStatement/?subject=Patient/{patient_id}",
            )
            response_request = MedicationRequest.make_request(
                method="GET",
                endpoint=f"/fhir/MedicationRequest/?subject=Patient/{patient_id}",
            )
            statement = response_statement.json()
            request = response_request.json()

            if statement.get("total", 0) == 0:
                logger.info(f"No MedicationStatement found for patient: {patient_id}")
                return JSONResponse(
                    content={"error": "No MedicationStatement found for patient"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            if request.get("total", 0) == 0:
                logger.info(f"No MedicationRequest found for patient: {patient_id}")
                return JSONResponse(
                    content={"error": "No MedicationRequest found for patient"},
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return {"medication_request": request, "medication_statement": statement}

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

            if not med.request_id:
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
                    status=history_status,
                    intent=INTEND,
                    note=[Annotation(text=OTHER_MEDICATION)],
                )
                medication_request.save()
                result["medication_request_created_id"] = medication_request.id
            else:
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
                    status=current_status,
                    intent=INTEND,
                )
                medication_request.save()
                result["medication_request_updated_id"] = medication_request.id

            if not med.statement_id:
                create_med_statement = MedicationStatement(
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
                    note=[Annotation(text=CURRENT_MEDICATION)],
                )
                create_med_statement.save()
                result["medication_statement_created_id"] = create_med_statement.id
            else:
                medication_statement = MedicationStatement(
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
                    status=history_status,
                )
                medication_statement.save()
                result["medication_statement_updated_id"] = medication_statement.id

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
        medication_list = []
        try:
            medication_list_snomed = AidboxApi.make_request(
                method="GET",
                endpoint=f"/Concept?.display$contains={medication_name}&.system=http://snomed.info/sct",
            )
            logger.info(f"Medication List: {medication_list_snomed}")
            data = medication_list_snomed.json()
            entries = data.get("entry", [])

            for entry in entries:
                resource = entry.get("resource", {})
                system = resource.get("system", "")
                code = resource.get("code", "")
                display = resource.get("display", "")
                if display:
                    medication_info = {
                        "system": system,
                        "code": code,
                        "display": display,
                    }
                    medication_list.append(medication_info)
            if not medication_list_snomed:
                return Response(status_code=404, content="Medication not found")
            return medication_list
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
