import traceback
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from aidbox.base import API

from services.aidbox_service import AidboxApi
from models.master_validation import MasterModel
import logging

logger = logging.getLogger("log")


class MasterClient:

    table = {"race": "CimparRace", "state": "CimparState", "lab_test": "CimparLabTest",
             "ethnicity": "CimparEthnicity", "company": "CimparInsuranceCompany"}

    @staticmethod
    def get_master_data(table_name: str):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_values = AidboxApi.make_request(
                method="GET",
                endpoint=f"/fhir/{MasterClient.table[table_name]}?_sort=.display"
            )
            values = master_values.json()
            master_value = []
            for entry in values["entry"]:
                master_value.append(
                    {
                        "id": entry.get("resource", {}).get("id"),
                        "code": entry.get("resource", {}).get("code"),
                        "display": entry.get("resource", {}).get("display")
                    }
                )
            return master_value
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=f"Failed to fetch data: {str(e)}")

    @staticmethod
    def fetch_master_using_code(table_name: str, code: str):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_values = API.make_request(
                method="GET",
                endpoint=f"/fhir/{MasterClient.table[table_name]}?.code={code}"
            )
            values = master_values.json()
            master_value = {}
            if values and values["entry"]:
                master_value.update(
                    {
                        "id": values["entry"][0].get("resource", {}).get("id"),
                        "code": values["entry"][0].get("resource", {}).get("code"),
                        "display": values["entry"][0].get("resource", {}).get("display")
                    }
                )
            return master_value
        except Exception as e:
            logger.error(f"Unable to fetch the code: {e}")
            return {}
        

    @staticmethod
    def fetch_lab_test(table_name: str, code: str, display: str):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            lab_test_value = API.make_request(
                method="GET",
                endpoint=f"/{MasterClient.table[table_name]}?.display$contains={display}&.code$contains={code}"
            )
            values = lab_test_value.json()
            if lab_test_value.status_code == 200 and values.get('total') > 0:
                return MasterClient.extract_details(values)
            else:
                return []
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve detail",
                "details": str(e),
            }
            
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def fetch_values(table_name: str, coding: MasterModel):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            lab_test_value = API.make_request(
                method="GET",
                endpoint=f"/{MasterClient.table[table_name]}?.display$contains={coding.display}&.code$contains={coding.code}"
            )
            lab_display_value = API.make_request(
                method="GET",
                endpoint=f"/{MasterClient.table[table_name]}?.display$contains={coding.display}"
            )
            lab_code_value = API.make_request(
                method="GET",
                endpoint=f"/{MasterClient.table[table_name]}?.code$contains={coding.code}"
            )
            values = lab_test_value.json()
            code_values = lab_display_value.json()
            display_values = lab_code_value.json()
            if lab_test_value.status_code == 200 and values.get('total') > 0:
                return MasterClient.extract_details(values)
            elif lab_display_value.status_code == 200 and display_values.get('total') > 0:
                return MasterClient.extract_details(display_values)
            elif lab_code_value.status_code== 200 and code_values.get('total') > 0:
                return MasterClient.extract_details(code_values)
            else:
                return []
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve detail",
                "details": str(e),
            }
            
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        

    @staticmethod
    def create_master_value(table_name: str, coding: MasterModel):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_data = MasterClient.fetch_values(table_name, coding)
            if not master_data:
                lab_test_value = API.make_request(
                    method="POST",
                    endpoint=f"/{MasterClient.table[table_name]}",
                    json=coding.__dict__
                )
                return lab_test_value.json()
            else:
                return JSONResponse(
                content=f"Lab Test already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to save detail",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def update_master_value(table_name: str, lab_id: str, coding: MasterModel):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_data = MasterClient.fetch_values(table_name, coding)
            if not master_data:
                lab_test_value = API.make_request(
                    method="PATCH",
                    endpoint=f"/{MasterClient.table[table_name]}/{lab_id}",
                    json=coding.__dict__
                )
                return lab_test_value.json()
            else:
                return JSONResponse(
                content=f"Lab Test already exists",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to save detail",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def delete_master_value(table_name: str, lab_id: str):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            lab_test_value = API.make_request(
                method="DELETE",
                endpoint=f"/{MasterClient.table[table_name]}/{lab_id}"
            )
            return lab_test_value.json()
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to save detail",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def extract_details(detail):
        master_values = []
        if detail.get("entry"):
            for entry in detail["entry"]:
                resource = entry.get("resource", {})
                item = {
                    "id": resource.get("id"),
                    "code": resource.get("code"),
                    "display": resource.get("display")
                }
                master_values.append(item)
        return master_values
    






