import logging
import traceback
from fastapi import status
from fastapi.responses import JSONResponse

from utils.common_utils import paginate
from services.aidbox_resource_wrapper import Observation

logger = logging.getLogger("log")


class ObservationClient:
    @staticmethod
    def get_lab_result_by_id(patient_id: str, lab_result_id: str):
        try:
            lab_result = Observation.make_request(method="GET", endpoint=f"/fhir/Observation/{lab_result_id}?subject=Patient/{patient_id}")
            lab_result_json = lab_result.json()
            if lab_result.status_code == 404:
                logger.info(f"Lab Result Not Found: {patient_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            return lab_result_json
        except Exception as e:
            logger.error(f"Error retrieving Lab Result: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Lab Result",
                "details": str(e),
            }
            
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_all_lab_result(page, page_size):
        try:
            lab_result = paginate(Observation, page, page_size)
            if lab_result.get('total', 1) == 0:
                logger.info(f"Lab result found for: {len(lab_result)}")
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            return JSONResponse(
                    content=lab_result,
                    status_code=status.HTTP_200_OK
                )
        except Exception as e:
            logger.error(f"Error retrieving Lab Result: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Lab Result",
                "details": str(e),
            }
            
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_lab_result_by_name(patient_id: str, name: str, page: int, page_size: int):
        try:
            result = {}
            lab_result = Observation.make_request(method="GET", 
                endpoint=f"/fhir/Observation?subject=Patient/{patient_id}&.code.coding.0.display$contains={name}&_page={page}&_count={page_size}")
            lab_result_json = lab_result.json()
            result["data"] = lab_result_json
            result["current_page"] = page
            result["page_size"] = page_size
            result["total_items"] = lab_result_json.get('total', 0)
            result["total_pages"] = (int(lab_result_json["total"]) // page_size) + 1
            if lab_result_json.get('total', 0) == 0:
                logger.info(f"Lab Result Not Found: {name} and {patient_id}")
                return []
            return result
        except Exception as e:
            logger.error(f"Error retrieving Lab Result: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Lab Result",
                "details": str(e),
            }
            
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_lab_result_by_patient_id(patient_id: str, page: int, page_size: int):
        try:
            result = {}
            lab_result = Observation.make_request(method="GET", endpoint=f"/fhir/Observation?subject=Patient/{patient_id}&_page={page}&_count={page_size}")
            lab_result_json = lab_result.json()
            if lab_result_json.get('total', 0) == 0:
                logger.info(f"No labtest found for patient: {patient_id}")
                return []
            result["data"] = lab_result_json
            result["current_page"] = page
            result["page_size"] = page_size
            result["total_items"] = lab_result_json.get('total', 0)
            result["total_pages"] = (int(lab_result_json["total"]) // page_size) + 1
            return result
        except Exception as e:
            logger.error(f"Error retrieving Lab Result: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Lab Result",
                "details": str(e),
            }
            
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_lab_result(page: int, page_size: int, name: str, patient_id: str, ):
        if name:
            return ObservationClient.get_lab_result_by_name(patient_id ,name, page, page_size)
        return ObservationClient.get_lab_result_by_patient_id(patient_id, page, page_size)

