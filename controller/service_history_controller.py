from fastapi import status
from fastapi.responses import JSONResponse
import logging
import traceback

from controller.lab_result_controller import ObservationClient
from controller.hl7_immunization_controller import HL7ImmunizationClient

logger = logging.getLogger("log")


class ServiceHistoryClient:
    @staticmethod
    def get_service_history_by_id(patient_id: str, all_service: bool = False, immunization: bool = False, lab_result: bool = False):
        try:
            service_history = ObservationClient.get_lab_result_by_patient_id(patient_id)
            immuzation = HL7ImmunizationClient.get_immunizations_by_patient_id(
                patient_id
            )
            if all_service:
                return ServiceHistoryClient.create_final_values(
                    service_history, immuzation
                )
        
            if lab_result:
                return ServiceHistoryClient.process_service_history(service_history)
            
            if immunization:
                return ServiceHistoryClient.process_immunization(immuzation)
        

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

    def process_service_history(service_history):
        service_history_entries = []
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
        combined_entries = ServiceHistoryClient.process_immunization(
            immunization
        ) + ServiceHistoryClient.process_service_history(service_history)
        return combined_entries
