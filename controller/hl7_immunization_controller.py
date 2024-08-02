from fastapi import status
from fastapi.responses import JSONResponse
import logging
import traceback
import requests
import os

from utils.common_utils import paginate
from services.aidbox_resource_wrapper import Immunization

logger = logging.getLogger("log")


class HL7ImmunizationClient:

    def __init__(self):
        self.base_url = os.environ.get("AIDBOX_URL")
        self.token = requests.auth.HTTPBasicAuth(os.environ.get("AIDBOX_CLIENT_USERNAME"),
                                                 os.environ.get("AIDBOX_CLIENT_PASSWORD"))

    def create_immunization(self, vx04_content):
        try:
            url = self.base_url + "/HL7v2/VXU_V04"
            response_data = requests.post(url, data=vx04_content, auth=self.token)
            logger.info(f"Added Successfully in DB: {response_data}")
            if response_data.status_code == 200:
                return {"status_code": 201, "data": "Record created Successfully"}
            raise Exception("Unable to create the record")
        except Exception as e:
            logger.error(f"Unable to create a Immunization: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create Immunization",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_immunizations_by_patient_id(patient_id: str, page: int, count: int):
        try:
            result = {}
            response_immunization = Immunization.make_request(
                method="GET",
                endpoint=f"/fhir/Immunization?patient=Patient/{patient_id}&_page={page}&_count={count}"
                         f"&_sort=-lastUpdated"
            )
            immunizations = response_immunization.json()
            if immunizations.get('total', 0) == 0:
                logger.info(f"No Immunization found for patient: {patient_id}")
                return []
            result["immunizations"] = immunizations
            result["current_page"] = page
            result["page_size"] = count
            result["total_items"] = immunizations.get('total', 0)
            result["total_pages"] = (int(immunizations["total"]) // count) + 1
            return result
        except Exception as e:
            logger.error(f"Unable to get immunization data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Immunization",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_immunizations_by_id(patient_id: str , immunization_id: str):
        try:
            response_immunization = Immunization.make_request(
                method="GET",
                endpoint=f"/fhir/Immunization/{immunization_id}?patient=Patient/{patient_id}&_sort=-lastUpdated"
            )
            immunizations = response_immunization.json()
            if response_immunization.status_code == 404:
                logger.info(f"Immunization Not Found: {response_immunization}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )          
            return {"immunizations": immunizations}
        except Exception as e:
            logger.error(f"Unable to get immunization data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Immunization",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_all_immunizations(page, page_size):
        try:
            response_immunization = paginate(Immunization, page, page_size)
            if not response_immunization:
                return JSONResponse(
                    status_code=status.HTTP_200_OK, 
                    content=[]
                )
            return {"immunizations": response_immunization}
        except Exception as e:
            logger.error(f"Unable to get immunization data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Immunizations",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_by_vaccine_name(name: str, page:int, count:int):
        try:
            result = {}
            response_immunization = Immunization.make_request(method="GET", endpoint=f"/fhir/Immunization/?.vaccineCode.coding.0.display$contains={name}&_page={page}&_count={count}")
            immunizations = response_immunization.json()
            if immunizations.get('total', 0) == 0:
                logger.info(f"No Immunization found for name: {name}")
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            result["immunizations"] = immunizations
            result["current_page"] = page
            result["page_size"] = count
            result["total_items"] = immunizations.get('total', 0)
            result["total_pages"] = (int(immunizations["total"]) // count) + 1
            return result
        except Exception as e:
            logger.error(f"Unable to get immunization data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Immunization",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        

    @staticmethod
    def get_immunization(name:str, page:int, page_size:int):
        if name:
            return HL7ImmunizationClient.get_by_vaccine_name(name, page, page_size)
        return HL7ImmunizationClient.get_all_immunizations(page, page_size)

    @staticmethod
    def find_immunizations_by_patient_id(patient_id: str, name: str, page:int, count:int):
        try:
            result = {}
            response_immunization = Immunization.make_request(
                method="GET",
                endpoint=f"/fhir/Immunization?patient=Patient/{patient_id}&.vaccineCode.coding.0.display$contains={name}"
                         f"&_page={page}&_count={count}&_sort=-lastUpdated")
            immunizations = response_immunization.json()
            if immunizations.get('total', 0) == 0:
                logger.info(f"No Immunization found for name: {name} and patient {patient_id}")
                return []
            result["data"] = immunizations
            result["current_page"] = page
            result["page_size"] = count
            result["total_items"] = immunizations.get('total', 0)
            result["total_pages"] = (int(immunizations["total"]) // count) + 1
            return result
        except Exception as e:
            logger.error(f"Unable to get immunization data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Immunization",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    
