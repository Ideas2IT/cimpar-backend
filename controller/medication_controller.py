import traceback
import logging
from fastapi import Response, status
from fastapi.responses import JSONResponse

from aidbox.base import Reference, CodeableConcept, Coding

from constants import PATIENT_REFERENCE, INTEND
from services.aidbox_service import AidboxApi
from models.medication_validation import MedicationCreateModel, MedicationUpdateModel
from services.aidbox_resource_wrapper import MedicationRequest 
from services.aidbox_resource_wrapper import MedicationStatement 


logger = logging.getLogger("log")


class MedicationClient:

    @staticmethod
    def create_medication_statement(med: MedicationCreateModel):

        current_status = "active" if med.statement_approved == True else "unknown"

        return MedicationStatement(
            medicationCodeableConcept=CodeableConcept(coding=[Coding(system=concept.system, code=concept.code, display=concept.display) for concept in med.request]),            
            subject=Reference(reference=f"{PATIENT_REFERENCE}/{med.patient_id}"),
            status=current_status
        )
    
    @staticmethod
    def create_medication_request(med: MedicationCreateModel):

        history_status = "active" if med.request_approved == True else "unknown"

        return MedicationRequest(
            medicationCodeableConcept=CodeableConcept(coding=[Coding(system=concept.system, code=concept.code, display=concept.display) for concept in med.statement]),
            subject=Reference(reference=f"{PATIENT_REFERENCE}/{med.patient_id}"),
            status=history_status,
            intent=INTEND,
        )


    @staticmethod
    def create_medication(med : MedicationCreateModel):
        try:

            medication_request = MedicationClient.create_medication_request(med)
            medication_request.save()

            medication_statement = MedicationClient.create_medication_statement(med)
            medication_statement.save()

            response_data = {
                "medication_request_id": medication_request.id,
                "medication_statement_id": medication_statement.id,
                "created": True
            }
            logger.info(f"Added Successfully in DB: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Unable to create a medication request and statement: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create medication",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_medication_by_patient_id(patient_id: str):
        try:
            response_statement = MedicationStatement.make_request(method = "GET", endpoint= f"/fhir/MedicationStatement/?subject=Patient/{patient_id}")
            response_request = MedicationRequest.make_request(method = "GET", endpoint= f"/fhir/MedicationRequest/?subject=Patient/{patient_id}")

            if not response_statement:
                return Response(status_code=404, content="Medication statement not found")
            medication_statement = response_statement.json() 

            if not response_request:
                return Response(status_code=404, content="Medication request not found")
            medication_request = response_request.json()

            return {"medication_statement": medication_statement, "medication_request": medication_request}
        except Exception as e:
            logger.error(f"Unable to get a medication data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve medication",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @staticmethod
    def update_medication_by_patient_id(med:MedicationUpdateModel):
        try:
            current_status = "active" if med.statement_approved == True else "unknown"
            history_status = "active" if med.request_approved == True else "unknown"

            medication_request = MedicationRequest(  
                id = med.request_id,    
                medicationCodeableConcept=CodeableConcept(coding=[Coding(system=concept.system, code=concept.code, display=concept.display) for concept in med.request]),            
                subject=Reference(reference=f"{PATIENT_REFERENCE}/{med.patient_id}"),
                status=current_status,
                intent=INTEND
            )
            medication_request.save()
            
            medication_statement = MedicationStatement(  
                id = med.statement_id,    
                medicationCodeableConcept=CodeableConcept(coding=[Coding(system=concept.system, code=concept.code, display=concept.display) for concept in med.statement]),
                subject=Reference(reference=f"{PATIENT_REFERENCE}/{med.patient_id}"),
                status=history_status,
            )

            medication_statement.save()

            logger.info(f"Updated in DB")
            return {f"medication_request": medication_request.id, "medication_statement": medication_statement.id}
        except Exception as e:
            logger.error(f"Unable to create a medication request and statement: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                content={f"Error: Unable to Updating Medication"}, status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_medications(medication_name: str):
        try:
            medication_list_snomed = AidboxApi.make_request(
                method="GET",
                endpoint=f"/Concept?.display$contains={medication_name}&.system=http://snomed.info/sct",
            )
            logger.info(f"Medication List: {medication_list_snomed}")
            if not medication_list_snomed:
                return Response(status_code=404, content="Medication not found")
            return {
                "medication_list": medication_list_snomed.json()
            }
        except Exception as e:
            logger.error(f"Unable to get medication list: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update medication",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )