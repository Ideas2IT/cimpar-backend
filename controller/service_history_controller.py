from fastapi import status
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import traceback

from controller.lab_result_controller import ObservationClient
from controller.hl7_immunization_controller import HL7ImmunizationClient

logger = logging.getLogger("log")


class ServiceHistoryClient:
    @staticmethod
    def get_service_history_by_id(patient_id: str, page: int, count: int, all_service: bool = False, immunization: bool = False, lab_result: bool = False, name: Optional[str] = None):
        try:
            if lab_result:
                service_history = ObservationClient.get_lab_result_by_patient_id(patient_id, page, count)
            if immunization:
                immuzation = HL7ImmunizationClient.get_immunizations_by_patient_id(patient_id, page, count)
            if all_service:
                service_history = ObservationClient.get_lab_result_by_patient_id(patient_id, page, count)
                immuzation = HL7ImmunizationClient.get_immunizations_by_patient_id(patient_id, page, count)
                return ServiceHistoryClient.create_final_values(service_history, immuzation)
            if lab_result and not immunization:
                if not service_history:  
                    return {}
                else:
                    return ServiceHistoryClient.process_lab_result(service_history)
            if immunization and not lab_result:
                if not immuzation:  
                    return {}
                else:
                    return ServiceHistoryClient.process_immunization(immuzation)
            if lab_result and immunization:
                processed_lab_result = ServiceHistoryClient.process_lab_result(service_history) if service_history else []
                processed_immunization = ServiceHistoryClient.process_immunization(immuzation) if immuzation else []
                return processed_lab_result + processed_immunization
            if name:
                test_by_name = ObservationClient.get_lab_result_by_name(patient_id, name, page, count)
                vaccine_by_name = HL7ImmunizationClient.find_immunizations_by_patient_id(patient_id, name, page, count)
                processed_results = {}
                if test_by_name:
                    processed_lab_results = ServiceHistoryClient.extract_lab_result(test_by_name) 
                    processed_results.update(processed_lab_results)
                if vaccine_by_name:
                    processed_immunization_results = ServiceHistoryClient.extract_immunization_entries(vaccine_by_name)
                    processed_results.update(processed_immunization_results)
                return processed_results if processed_results else []
            return {}

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

    def process_immunization(service_history):
        immunization_entries = []
        if not service_history:
            return {}
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

    def process_lab_result(service_history):
        service_history_entries = []
        if not service_history:
            return {}
        
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
    
        
    def create_final_values(service_history, immunization):
        processed_immunization = ServiceHistoryClient.process_immunization(immunization)
        processed_lab_result = ServiceHistoryClient.process_lab_result(service_history)
        
        if not processed_immunization and not processed_lab_result:
            return {}
        if not processed_immunization:
            return processed_lab_result
        if not processed_lab_result:
            return processed_immunization
        combined_data = processed_immunization.get('data', []) + processed_lab_result.get('data', [])
        combined_result = {
            'data': combined_data,
            'current_page': processed_lab_result.get('current_page'),
            'page_size': processed_lab_result.get('page_size'),
            'total_items': processed_lab_result.get('total_items'),
            'total_pages': processed_lab_result.get('total_pages')
        }

        return combined_result    

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
    

    def extract_lab_result(service_history):
        imaging_history_entries = []
        if not service_history:
            return {}
        
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

