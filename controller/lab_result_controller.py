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
    def get_lab_result_by_name(name: str):
        try:
            lab_result = Observation.make_request(method="GET", endpoint=f"/fhir/Observation?.code.coding.0.display$contains={name}")
            lab_result_json = lab_result.json()
            if lab_result.status_code == 404:
                logger.info(f"Lab Result Not Found: {name}")
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
    def get_lab_result_by_patient_id(patient_id: str):
        try:
            lab_result = Observation.make_request(method="GET", endpoint=f"/fhir/Observation?subject=Patient/{patient_id}")
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
