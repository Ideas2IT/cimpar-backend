from fastapi import status
import logging
import traceback
from fastapi.responses import JSONResponse

from aidbox.base import Reference, CodeableConcept, Coding
from aidbox.resource.coverage import Coverage_Class

from constants import GROUP_SYSTEM, GROUP_CODE,PATIENT_REFERENCE
from services.aidbox_resource_wrapper import Coverage 
from models.insurance_validation import CoverageModel, CoverageUpdateModel


logger = logging.getLogger("log")


class CoverageClient:
    @staticmethod
    def create_coverage(coverage: CoverageModel, patient_id: str):
        try:
            response_coverage = Coverage.make_request(method="GET", endpoint=f"/fhir/Coverage/?beneficiary=Patient/{patient_id}")
            existing_coverages = response_coverage.json() if response_coverage else {}

            patient_id_occurrences = sum(1 for entry in existing_coverages.get('entry', []) if entry['resource']['beneficiary']['reference'] == f"Patient/{patient_id}")

            if patient_id_occurrences >= 3:
                logger.error(f"A patient can only have 3 insurance")
                return JSONResponse(
                    content="A patient can only have 3 insurance", status_code=status.HTTP_200_OK
                )

            insurance_plan = Coverage(
                status=coverage.status,
                beneficiary=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                subscriberId=coverage.policy_number,
                payor=[Reference(display=coverage.provider_name)],
                class_=[
                    Coverage_Class(
                        type=CodeableConcept(coding=[Coding(system=GROUP_SYSTEM, code=GROUP_CODE)]),
                        value=coverage.group_number,
                )],
                order=coverage.insurance_type
            )
            insurance_plan.save()
            response_data = {"id": insurance_plan.id, "created": True}
            logger.info(f"Added Successfully in DB: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Unable to create a insurance_plan: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_coverage_by_patient_id(patient_id: str):
        try:
            response_coverage = Coverage.make_request(method="GET", endpoint=f"/fhir/Coverage/?beneficiary=Patient/{patient_id}")
            coverage = response_coverage.json() 
            
            if coverage.get('total', 0) == 0:
                logger.info(f"No Coverage found for patient: {patient_id}")
                return JSONResponse(
                    content={"error": "No Coverage found for patient"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            return {"coverage": coverage}
        except Exception as e:
            logger.error(f"Unable to get coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_coverage_by_id(patient_id: str, insurance_id: str):
        try:
            response_coverage = Coverage.make_request(method = "GET", endpoint= f"/fhir/Coverage/{insurance_id}?beneficiary=Patient/{patient_id}")
            coverage = response_coverage.json()

            if response_coverage.status_code == 404:
                logger.info(f"Coverage Not Found: {patient_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            return {"coverage": coverage}
        except Exception as e:
            logger.error(f"Unable to get coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def update_by_insurance_id(patient_id: str, insurance_id: str, updated_coverage: CoverageUpdateModel):
        try:
            response_coverage = Coverage.make_request(method="GET", endpoint= f"/fhir/Coverage/{insurance_id}?beneficiary=Patient/{patient_id}")
            coverage = response_coverage.json() 
            if response_coverage.status_code == 404:
                logger.info(f"Coverage Not Found: {patient_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            if coverage.get("id") == insurance_id and coverage.get("beneficiary", {}).get("reference") == f"Patient/{patient_id}":    
                insurance_plan = Coverage(
                    id=insurance_id,
                    status=updated_coverage.status,
                    beneficiary=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    subscriberId=updated_coverage.policy_number,
                    payor=[Reference(display=updated_coverage.provider_name)],
                    class_=[
                        Coverage_Class(
                            type=CodeableConcept(coding=[Coding(system=GROUP_SYSTEM, code=GROUP_CODE)]),
                            value=updated_coverage.group_number,
                        )],
                    order=updated_coverage.insurance_type
                )
                insurance_plan.save()
                response_data = {"id": insurance_plan.id, "updated": True}
                logger.info(f"Added Updated in DB: {response_data}")
                return response_data
            error_response_data = { 
                "error": "No insurance matches for this patient"
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Unable to update coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def delete_by_insurance_id(insurance_id: str, patient_id: str):
        try:
            response_coverage = Coverage.make_request(method="GET", endpoint=f"/fhir/Coverage/{insurance_id}?beneficiary=Patient/{patient_id}")
            existing_coverage = response_coverage.json() if response_coverage else {}
            if response_coverage.status_code == 404:
                logger.info(f"Coverage Not Found: {patient_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )

            if existing_coverage.get("id") == insurance_id and existing_coverage.get("beneficiary", {}).get("reference") == f"Patient/{patient_id}":
                delete_data = Coverage(**existing_coverage)
                delete_data.delete()
                return {"deleted": True, "patient_id": patient_id}
            error_response_data = { 
                "error": "No insurance matches for this patient"
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unable to delete coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to delete Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

