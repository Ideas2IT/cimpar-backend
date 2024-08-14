from fastapi import status
from fastapi.responses import JSONResponse
import logging
import traceback

from services.aidbox_service import AidboxApi
from controller.appointment_controller import AppointmentClient
from constants import UPCOMING_APPOINTMENT
logger = logging.getLogger("log")


class ServiceHistoryClient:
    @staticmethod
    def get_service_history(patient_id: str, service_type, name, page, count):
        try:
            if service_type is not None and service_type.lower() == "lab_result":
                final_response = ServiceHistoryClient.custom_query_with_pagination(
                    "filteredObservation", patient_id, name, page, count
                )
                if int(page) == 1 and not name:
                    response = AppointmentClient.get_appointment_by_patient_id(patient_id, UPCOMING_APPOINTMENT)
                    final_response["data"] = response + final_response.get("data", [])
            elif service_type is not None and service_type.lower() == "immunization":
                final_response = ServiceHistoryClient.custom_query_with_pagination(
                    "filteredImmunization", patient_id, name, page, count
                )
            else:
                final_response = ServiceHistoryClient.custom_query_with_pagination(
                    "filteredImmunizationObservation", patient_id, name, page, count
                )
                if int(page) == 1 and not name:
                    response = AppointmentClient.get_appointment_by_patient_id(patient_id, UPCOMING_APPOINTMENT)
                    final_response["data"] = response + final_response.get("data", [])
            return JSONResponse(
                content=final_response,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error retrieving Service History: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Service History",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def process_immunization(service_history):
        immunization_entries = []
        if not service_history:
            return []
        immunizations = service_history.get("immunizations", {})
        current_page = service_history.get("current_page", 0)
        page_size = service_history.get("page_size", 0)
        total_items = service_history.get("total_items", 0)
        total_pages = service_history.get("total_pages", 0)

        for entry in immunizations.get("entry", []):
            vaccine_display = (
                entry.get("resource", {})
                .get("vaccineCode", {})
                .get("coding", [{}])[0]
                .get("display")
            )
            resource_id = entry.get("resource", {}).get("id")
            occurrence_date = entry.get("resource", {}).get("occurrenceDateTime")
            if vaccine_display or occurrence_date:
                immunization_entries.append(
                    {
                        "Id": resource_id,
                        "Category": "Immunization",
                        "ServiceFor": vaccine_display,
                        "DateOfService": occurrence_date,
                    }
                )

        return {
            "data": immunization_entries,
            "current_page": current_page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }

    @staticmethod
    def process_lab_result(service_history):
        service_history_entries = []
        if not service_history:
            return []
        
        for entry in service_history.get("data", {}).get("entry", []):
            resource = entry.get("resource", {})
            service_display = (
                resource.get("code", {})
                .get("coding", [{}])[0]
                .get("display")
            )
            resource_id = resource.get("id")
            occurrence_date = resource.get("effectiveDateTime")
            if service_display or occurrence_date:
                service_history_entries.append(
                    {
                        "Id": resource_id,
                        "Category": "LabResult",
                        "ServiceFor": service_display,
                        "DateOfService": occurrence_date,
                    }
                )
        
        return {
            "data": service_history_entries,
            "current_page": service_history.get('current_page', 1),
            "page_size": service_history.get('page_size'),
            "total_items": service_history.get('total_items'),
            "total_pages": service_history.get('total_pages')
        }

    @staticmethod
    def create_final_values(service_history, immunization):
        processed_immunization = ServiceHistoryClient.process_immunization(immunization)
        processed_lab_result = ServiceHistoryClient.process_lab_result(service_history)
        if not isinstance(processed_immunization, list):
            processed_immunization = processed_immunization if processed_immunization else []
        if not isinstance(processed_lab_result, list):
            processed_lab_result = processed_lab_result if processed_lab_result else []
        combined_entries = {**processed_immunization, **processed_lab_result}
        return combined_entries

    @staticmethod
    def extract_immunization_entries(data):
        immunization_entries = []
        current_page = data.get("current_page", 0)
        page_size = data.get("page_size", 0)
        total_items = data.get("total_items", 0)
        total_pages = data.get("total_pages", 0)
        for entry in data.get("data", {}).get("entry", []):
            vaccine_display = (
                entry.get("resource", {})
                .get("vaccineCode", {})
                .get("coding", [{}])[0]
                .get("display")
            )
            resource_id = entry.get("resource", {}).get("id")
            occurrence_date = entry.get("resource", {}).get("occurrenceDateTime")
            if vaccine_display or occurrence_date:
                immunization_entries.append(
                    {
                        "Id": resource_id,
                        "Category": "Immunization",
                        "ServiceFor": vaccine_display,
                        "DateOfService": occurrence_date,
                    }
                )
        return {
            "data": immunization_entries,
            "current_page": current_page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }

    @staticmethod
    def extract_lab_result(service_history):
        imaging_history_entries = []
        if not service_history:
            return []
        
        for entry in service_history.get("data", {}).get("entry", []):
            resource = entry.get("resource", {})
            service_display = (
                resource.get("code", {})
                .get("coding", [{}])[0]
                .get("display")
            )
            resource_id = resource.get("id")
            occurrence_date = resource.get("effectiveDateTime")
            if service_display or occurrence_date:
                imaging_history_entries.append(
                    {
                        "Id": resource_id,
                        "Category": "LabResult",
                        "ServiceFor": service_display,
                        "DateOfService": occurrence_date,
                    }
                )
        
        return {
            "data": imaging_history_entries,
            "current_page": service_history.get('current_page', 1),
            "page_size": service_history.get('page_size'),
            "total_items": service_history.get('total_items'),
            "total_pages": service_history.get('total_pages')
        }

    @staticmethod
    def custom_query_with_pagination(query_name: str, patient_id: str, search: str, page: int, page_size: int):
        limit = page_size
        offset = (page - 1) * page_size
        response_name = AidboxApi.make_request(
            method="GET",
            endpoint=f"/$query/{query_name}?patient_id={patient_id}&search={search}&limit={limit}&offset={offset}"
        )
        data = response_name.json()
        count_res = AidboxApi.make_request(
            method="GET",
            endpoint=f"/$query/{query_name}Count?patient_id={patient_id}&search={search}"
        )
        count_resp = count_res.json()
        total_count = count_resp["data"][0]["count"]
        formatted_data = [
            {
                "resource": {
                    "id": item["id"],
                    "record_type": item["record_type"],
                    **item["resource"]
                }
            } for item in data.get('data', [])
        ]
        final_response = {
            "data": formatted_data,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count // page_size) + (1 if total_count % page_size != 0 else 0)
            }
        }
        return final_response

