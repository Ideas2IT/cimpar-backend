import time
import traceback
import logging
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from aidbox.base import API

from services.aidbox_service import AidboxApi
from models.master_validation import (
    MasterModel, 
    DeleteMasterModel
)
from constants import TIME_THRESHOLD

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
            if master_values.status_code == 200:
                values = master_values.json()
            else:
                logger.error(table_name)
                logger.error(master_values.status_code)
                logger.error(master_values.json())
                raise Exception("Unable to fetch data")
            master_value = []

            for index, entry in enumerate(values.get("entry", [])):
                start_time = time.time() 
                if entry.get("resource", {}).get("is_active"):
                    master_value.append(
                        {
                            "id": entry.get("resource", {}).get("id"),
                            "code": entry.get("resource", {}).get("code"),
                            "display": entry.get("resource", {}).get("display")
                        }
                    )
                end_time = time.time() 
                processing_time = end_time - start_time
                logger.info(f"Processed entry {index} in {processing_time:.5f} seconds")
                if processing_time > TIME_THRESHOLD:
                    logger.warning(f"Entry {index} took too long: {processing_time:.2f} seconds")
            return master_value if master_value else []
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=f"Failed to fetch data: {str(e)}")


    @staticmethod
    def fetch_master_data(table_name: str, code: str, display: str, page: str, page_size: str):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            result = {}
            master_values = API.make_request(
                method="GET",
                endpoint=f"/{MasterClient.table[table_name]}?&_page={page}&_count={page_size}&.display$contains={display}&.code$contains={code}"
                f"&_sort=-lastUpdated"
            )
            if master_values.status_code == 200:
                values = master_values.json()
                if values.get('total') == 0:
                    result = {
                        "data": [],
                        "pagination": {
                            "current_page": page,
                            "page_size": page_size,
                            "total_items": values.get('total'),
                            "total_pages": (int(values["total"]) + page_size - 1) // page_size
                        } 
                    }
                    return result
                elif values.get('total') > 0:
                    master_value = MasterClient.extract_details(values)
                    result = {
                        "data": master_value,
                        "pagination": {
                            "current_page": page,
                            "page_size": page_size,
                            "total_items": values.get('total'),
                            "total_pages": (int(values["total"]) + page_size - 1) // page_size
                        } 
                    }
                    return result
                else:
                    logger.error(table_name)
                    logger.error(master_values.status_code)
                    logger.error(master_values.json())
                    raise Exception(f"Unable to retrive data")
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
    def fetch_data(table_name: str, coding: MasterModel):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kindly, verify the name.")
        try:
            endpoint = f"/{MasterClient.table[table_name]}"
            if coding.code and coding.display:
                endpoint = endpoint+f"?.display$contains={coding.display}&.code$contains={coding.code}"
            elif coding.display:
                endpoint = endpoint+f"?.display$contains={coding.display}"
            elif coding.code:
                endpoint = endpoint+f"?.code$contains={coding.code}"
            master_value = API.make_request(method="GET", endpoint=endpoint)
            if master_value.status_code == 200:
                values = master_value.json()
                if values.get('total') > 0:
                    master_data = MasterClient.extract_details(values)
                    return master_data if master_data else []
            else:
                logger.error(coding)
                logger.error(table_name)
                raise Exception("Unable to retrive data")
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
    def create_master_entries(table_name: str, coding: MasterModel):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_data = MasterClient.fetch_data(table_name, coding)
            if master_data:
                if not master_data[0]['is_active']:
                    master_value = API.make_request(
                        method="PATCH",
                        endpoint=f"/{MasterClient.table[table_name]}/{master_data[0]['id']}",
                        json={"is_active": coding.is_active}
                    )
                    if master_value.status_code == 200:
                        return master_value.json()
                    else:
                        logger.error(master_value.status_code)
                        logger.error(master_value.json())
                        raise Exception("Unable to create")
                else:
                    logger.error(master_data)
                    raise Exception("Lab Test already exists")
            else:
                master_value = API.make_request(
                    method="POST",
                    endpoint=f"/{MasterClient.table[table_name]}",
                    json=coding.__dict__
                )
                return master_value.json()  
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to fetch the details: {e}",
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def update_master_data(table_name: str, resource_id: str, coding: MasterModel):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            if coding:
                master_value = API.make_request(
                    method="PATCH",
                    endpoint=f"/{MasterClient.table[table_name]}/{resource_id}",
                    json=coding.__dict__
                )
                if master_value.status_code == 200:
                    return master_value.json() 
                else:
                    logger.error(master_value.status_code)
                    logger.error(master_value.json())
                    raise Exception("Unable to update")
            else:
                logger.error(coding)
                raise Exception("Unable to update")
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
    def delete_master_data(table_name: str, resource_id: str, active: DeleteMasterModel):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_data = API.make_request(
                method="PATCH",
                endpoint=f"/{MasterClient.table[table_name]}/{resource_id}",
                json=active.__dict__

            )
            return master_data.json()
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
                    "display": resource.get("display"),
                    "is_active": resource.get("is_active")
                }
                master_values.append(item)
        return master_values
    
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
