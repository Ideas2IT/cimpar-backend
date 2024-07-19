from fastapi import status
from fastapi.responses import JSONResponse
import logging
import traceback

from controller.lab_result_controller import ObservationClient
from controller.hl7_immunization_controller import HL7ImmunizationClient

logger = logging.getLogger("log")


class ServiceHistoryClient:
    @staticmethod
    def get_service_history_by_id(patient_id: str, page: int, count: int, all_service: bool = False, immunization: bool = False, lab_result: bool = False):
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
                    return []
                else:
                    return ServiceHistoryClient.process_lab_result(service_history)
            if immunization and not lab_result:
                if not immuzation:  
                    return []
                else:
                    return ServiceHistoryClient.process_immunization(immuzation)
            if lab_result and immunization:
                processed_lab_result = ServiceHistoryClient.process_lab_result(service_history) if service_history else []
                processed_immunization = ServiceHistoryClient.process_immunization(immuzation) if immuzation else []
                return processed_lab_result + processed_immunization

            return [] 
        

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
        
    def create_final_values(service_history, immunization):
        processed_immunization = ServiceHistoryClient.process_immunization(immunization)
        processed_lab_result = ServiceHistoryClient.process_lab_result(service_history)
        if not isinstance(processed_immunization, list):
            processed_immunization = [processed_immunization] if processed_immunization else []
        if not isinstance(processed_lab_result, list):
            processed_lab_result = [processed_lab_result] if processed_lab_result else []
        combined_entries = processed_immunization + processed_lab_result
        return combined_entries

