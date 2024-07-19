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

    def process_immunization(immunization):
        immunization_entries = []
        if not immunization:
            return []
        for entry in immunization.get("immunizations", {}).get("entry", []):
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
        return immunization_entries

    def process_lab_result(service_history):
        service_history_entries = []
        if not service_history:
            return []
        for entry in service_history.get("entry", []):
            service_display = (
                entry.get("resource", {})
                .get("code", {})
                .get("coding", [{}])[0]
                .get("display")
            )
            resource_id = entry.get("resource", {}).get("id")
            occurrence_date = entry.get("resource", {}).get("effectiveDateTime")
            if service_display or occurrence_date:
                service_history_entries.append(
                    {
                        "Id": resource_id,
                        "Category": "Lab Result",
                        "ServiceFor": service_display,
                        "DateOfService": occurrence_date,
                    }
                )
        return service_history_entries
        
    def create_final_values(service_history, immunization):
        processed_immunization = ServiceHistoryClient.process_immunization(immunization)
        processed_lab_result = ServiceHistoryClient.process_lab_result(service_history)
        if processed_immunization and processed_lab_result:
            combined_entries = processed_immunization + processed_lab_result
        elif processed_immunization:
            combined_entries = processed_immunization
        elif processed_lab_result:
            combined_entries = processed_lab_result
        else:
            combined_entries = []
        return combined_entries

