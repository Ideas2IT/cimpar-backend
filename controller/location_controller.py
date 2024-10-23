import logging
import traceback
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse

from aidbox.base import API

from models.location_validation import LocationModel, LocationDeleteClient


logger = logging.getLogger("log")


class LocationClient:

    table = {"location": "CimparLocation"}

    @staticmethod
    def create_location(table_name: str, loc: LocationModel):
        if table_name not in LocationClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="POST",
                endpoint=f"/{LocationClient.table[table_name]}",
                json={
                    "city": loc.city,
                    "state": loc.state,
                    "pincode": loc.pincode,
                    "service_center_name": loc.service_center_name,
                    "is_active": loc.is_active,
                },
            )
            values = master_value.json()
            if master_value.status_code == 201:
                values = master_value.json()
                return values
            else:
                logger.error(master_value.json())
                raise Exception("Unable to create")
        except Exception as e:
            logger.error(f"Unable to create: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to create: {e}",
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_by_id(table_name: str, location_id: str):
        if table_name not in LocationClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="GET",
                endpoint=f"/{LocationClient.table[table_name]}/{location_id}",
            )
            if master_value.status_code == 200:
                values = master_value.json()
                return values
            else:
                logger.error(master_value.json())
                raise Exception("Unable to fetch")
        except Exception as e:
            logger.error(f"Unable to fetch: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to fetch: {e}",
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_all_location(table_name: str, page: int, page_size: int, required_all: bool):
        if table_name not in LocationClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="GET",
                endpoint=f"/{LocationClient.table[table_name]}?&_sort=-lastUpdated&_page={page}&_count={page_size}",
            )
            if master_value.status_code == 200:
                values = master_value.json()
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
                elif required_all and values.get('total') > 0:
                    master_value = master_value.json()
                    master_data = LocationClient.active_extract_details(master_value)
                    result = {
                        "data": master_data
                    }
                    return result
                elif values.get('total') > 0 and not required_all:
                    master_value = master_value.json()
                    master_data = LocationClient.extract_details(master_value)
                    result = {
                        "data": master_data,
                        "pagination": {
                            "current_page": page,
                            "page_size": page_size,
                            "total_items": values.get('total'),
                            "total_pages": (int(values["total"]) + page_size - 1) // page_size
                        } 
                    }
                    return result
            else:
                logger.error(master_value.json())
                raise Exception("Unable to fetch")
        except Exception as e:
            logger.error(f"Unable to fetch: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to fetch: {e}",
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def update_by_id(table_name: str, location_id: str, loc: LocationModel):
        if table_name not in LocationClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="PUT",
                endpoint=f"/{LocationClient.table[table_name]}/{location_id}",
                json={
                    "city": loc.city,
                    "state": loc.state,
                    "pincode": loc.pincode,
                    "service_center_name": loc.service_center_name,
                    "is_active": loc.is_active,
                },
            )
            values = master_value.json()
            if master_value.status_code == 200:
                values = master_value.json()
                return values
            else:
                logger.error(master_value.json())
                raise Exception("Unable to update")
        except Exception as e:
            logger.error(f"Unable to update: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to update: {e}",
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
        

    @staticmethod
    def delete_by_id(table_name: str, location_id: str, loc: LocationDeleteClient):
        if table_name not in LocationClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="PATCH",
                endpoint=f"/{LocationClient.table[table_name]}/{location_id}",
                json={"is_active": loc.is_active},
            )
            if master_value.status_code == 200:
                values = master_value.json()
                return values
            else:
                logger.error(master_value.json())
                raise Exception("Unable to delete")
        except Exception as e:
            logger.error(f"Unable to delete: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to delete: {e}",
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def extract_details(detail):
        master_values = []
        if detail.get("entry"):
            for entry in detail["entry"]:
                resource = entry.get("resource", {})
                item = {
                    "id": resource.get("id"),
                    "city": resource.get("city"),
                    "state": resource.get("state"),
                    "pincode": resource.get("pincode"),
                    "service_center_name": resource.get("service_center_name"),
                    "is_active": resource.get("is_active"),
                }
                master_values.append(item)
        return master_values
    
    @staticmethod
    def active_extract_details(detail):
        master_values = []
        if detail.get("entry"):
            for entry in detail["entry"]:
                if entry.get("resource", {}).get("is_active"):
                    resource = entry.get("resource", {})
                    item = {
                        "id": resource.get("id"),
                        "city": resource.get("city"),
                        "state": resource.get("state"),
                        "pincode": resource.get("pincode"),
                        "service_center_name": resource.get("service_center_name"),
                        "is_active": resource.get("is_active"),
                    }
                    master_values.append(item)
            return master_values


