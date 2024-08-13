import logging
import traceback
from fastapi import status
from fastapi.responses import JSONResponse

from aidbox.base import Period, CodeableConcept, Reference, Coding, CodeableConcept
from aidbox.resource.encounter import Encounter_Participant, Encounter_Location, Encounter_Hospitalization

from constants import (
    PATIENT_REFERENCE,
    CLASS_DISPLAY,
    ENCOUNTER_TYPE_SYSTEM,
    ENCOUNTER_TYPE_CODE,
    TREATMENT_SUMMARY_SYSTEM,
    TREATMENT_SUMMARY_CODE,
    ENCOUNTER_STATUS,
    CLASS_CODE,
    VISIT_HISTORY_CONTAINER,
    DELETED
)
from models.encounter_validation import EncounterModel, EncounterUpdateModel
from services.aidbox_resource_wrapper import Encounter
from utils.common_utils import paginate

from utils.common_utils import azure_file_handler, delete_file_azure

logger = logging.getLogger("log")


class EncounterClient:
    @staticmethod
    def create_encounter(enc: EncounterModel, patient_id):
        try:
            result = {}
            encounter = Encounter(
                status=ENCOUNTER_STATUS,
                class_=Coding(code=CLASS_CODE, display=CLASS_DISPLAY),
                type=[
                    CodeableConcept(
                        coding=[
                            Coding(
                                system=ENCOUNTER_TYPE_SYSTEM,
                                code=ENCOUNTER_TYPE_CODE,
                                display=enc.follow_up_care,
                            )
                        ],
                        text=enc.follow_up_care,
                    )
                ],
                period=Period(start=enc.admission_date, end=enc.discharge_date),
                subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                reasonCode=[CodeableConcept(text=enc.reason)],
                participant=[Encounter_Participant(individual=Reference(display=enc.primary_care_team))],
                location=[Encounter_Location(location=Reference(display=enc.phone_number))],
                serviceProvider=Reference(display=enc.location),
                serviceType=CodeableConcept(
                    coding=[
                        Coding(
                            system=ENCOUNTER_TYPE_SYSTEM,
                            code=ENCOUNTER_TYPE_CODE,
                            display=enc.activity_notes,
                        )
                    ],
                    text=enc.activity_notes,
                ),
                hospitalization=Encounter_Hospitalization(
                    specialCourtesy=[
                        CodeableConcept(
                            coding=[
                                Coding(
                                    system=TREATMENT_SUMMARY_SYSTEM,
                                    code=TREATMENT_SUMMARY_CODE,
                                    display=enc.treatment_summary,
                                )
                            ],
                            text=enc.treatment_summary,
                        )
                    ],
                )
            )
            encounter.save()
            result["id"] = encounter.id
            result["created"] = True
            logger.info(f"Added Successfully in DB: {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating visit history {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create visit history",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_encounter_by_patient_id(patient_id: str, page: int, count: int):
        try:
            result = {}
            encounter = Encounter.make_request(
                method="GET",
                endpoint=f"/fhir/Encounter/?subject=Patient/{patient_id}&_page={page}&_count={count}&_sort=-lastUpdated"
            )
            encounter_data = encounter.json()
            if encounter_data.get('total', 0) == 0:
                logger.info(f"No encounters found for patient: {patient_id}")
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            for encounter_values in encounter_data['entry']:
                logger.info(f"identifying blob data for URL: {patient_id}/{encounter_values['resource']['id']}")
                file_url = azure_file_handler(container_name=VISIT_HISTORY_CONTAINER,
                                              blob_name=f"{patient_id}/{encounter_values['resource']['id']}",
                                              fetch=True)
                encounter_values['resource']['file_url'] = file_url if file_url else False
            result["data"] = encounter_data
            result["current_page"] = page
            result["page_size"] = count
            result["total_items"] = encounter_data.get('total', 0)
            result["total_pages"] = (int(encounter_data["total"]) + count - 1) // count
            return result
        except Exception as e:
            logger.error(f"Error retrieving encounters: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve visit history",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_encounter_by_id(patient_id: str, encounter_id: str):
        try:
            encounter = Encounter.make_request(method="GET",
                                               endpoint=f"/fhir/Encounter/{encounter_id}?subject=Patient/{patient_id}")
            if encounter.status_code == 404 or encounter.status_code == 410:
                logger.info(f"Encounter Not Found: {encounter_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            encounter_json = encounter.json()
            if 'id' in encounter_json and encounter_json['id'] != DELETED:
                logger.info(f"identifying blob data for URL: {patient_id}/{encounter_id}")
                file_url = azure_file_handler(container_name=VISIT_HISTORY_CONTAINER,
                                              blob_name=f"{patient_id}/{encounter_id}",
                                              fetch=True)
                encounter_json['file_url'] = file_url if file_url else False
            return encounter_json
        except Exception as e:
            logger.error(f"Error retrieving encounters: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve visit history for this patient",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def update_by_patient_id(patient_id: str, encounter_id: str, enc: EncounterUpdateModel, upload_file, file_extension=None):
        try:
            result = {}
            response = Encounter.make_request(method="GET",
                                              endpoint=f"/fhir/Encounter/{encounter_id}?subject=Patient/{patient_id}")
            existing_encounter = response.json()
            if response.status_code == 404:
                logger.info(f"Encounter Not Found: {encounter_id}")
                return JSONResponse(
                    content={"error": "Patient you have provided was not matched with visit history"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            if existing_encounter.get("subject", {}).get("reference") == f"Patient/{patient_id}":
                encounter = Encounter(
                    id=encounter_id,
                    status=ENCOUNTER_STATUS,
                    class_=Coding(code=CLASS_CODE, display=CLASS_DISPLAY),
                    type=[
                        CodeableConcept(
                            coding=[
                                Coding(
                                    system=ENCOUNTER_TYPE_SYSTEM,
                                    code=ENCOUNTER_TYPE_CODE,
                                    display=enc.follow_up_care,
                                )
                            ],
                            text=enc.follow_up_care,
                        )
                    ],
                    period=Period(start=enc.admission_date, end=enc.discharge_date),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    reasonCode=[CodeableConcept(text=enc.reason)],
                    participant=[Encounter_Participant(individual=Reference(display=enc.primary_care_team))],
                    location=[Encounter_Location(location=Reference(display=enc.phone_number))],
                    serviceProvider=Reference(display=enc.location),
                    serviceType=CodeableConcept(
                        coding=[
                            Coding(
                                system=ENCOUNTER_TYPE_SYSTEM,
                                code=ENCOUNTER_TYPE_CODE,
                                display=enc.activity_notes,
                            )
                        ],
                        text=enc.activity_notes,
                    ),
                    hospitalization=Encounter_Hospitalization(
                        specialCourtesy=[
                            CodeableConcept(
                                coding=[
                                    Coding(
                                        system=TREATMENT_SUMMARY_SYSTEM,
                                        code=TREATMENT_SUMMARY_CODE,
                                        display=enc.treatment_summary,
                                    )
                                ],
                                text=enc.treatment_summary,
                            )
                        ],
                    )
                )
                encounter.save()
                result["encounter"] = encounter.id
                logger.info(f"Updated Successfully in DB: {patient_id}")
                result["updated"] = True
                return result
            return JSONResponse(
                content={"error": "patient_id you have provided was not matched with visit history"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unable to update encounter: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update visit history",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_all_encounters(page, page_size):
        try:
            encounters = paginate(Encounter, page, page_size)
            if encounters.get('total', 1) == 0:
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            logger.info(f"Encounters Found {len(encounters)}")
            return JSONResponse(
                content=encounters,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error retrieving encounters: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve visit history",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def delete_by_encounter_id(patient_id: str, encounter_id: str):
        try:
            encounter = Encounter.make_request(method="GET",
                                               endpoint=f"/fhir/Encounter/{encounter_id}?subject=Patient/{patient_id}")
            existing_encounter = encounter.json()
            if encounter.status_code == 404:
                logger.info(f"Encounter Not Found: {encounter_id}")
                return JSONResponse(
                    content={"error": "Patient provided was not matched with visit history"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            if existing_encounter.get("subject", {}).get(
                    "reference") == f"Patient/{patient_id}" and existing_encounter.get('id') == encounter_id:
                existing_encounter['class_'] = existing_encounter.pop('class')
                delete_data = Encounter(**existing_encounter)
                delete_data.delete()
                if 'id' in existing_encounter and existing_encounter['id'] != DELETED:
                    logger.info(f"identifying blob data for URL: {patient_id}/{encounter_id}")
                    file_url = azure_file_handler(container_name=VISIT_HISTORY_CONTAINER,
                                                  blob_name=f"{patient_id}/{encounter_id}",
                                                  fetch=True)
                    if file_url:
                        azure_file_handler(container_name=VISIT_HISTORY_CONTAINER,
                                           blob_name=f"{patient_id}/{encounter_id}",
                                           delete=True)
                return {"encounter": encounter_id, "deleted": True}
            return JSONResponse(
                content={"error": "patient provided was not matched with visit history"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unable to delete encounter: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to delete visit history",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def delete_file(blob_name):
        try:
            container_name =  VISIT_HISTORY_CONTAINER
            if container_name and blob_name:
                response = delete_file_azure(container_name, blob_name)
                logger.error(f"delete response {response}")
                if response:
                    return {f"File deleted for {blob_name}"}
        except Exception as e:
            logger.error(f"Unable to delete file: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to delete file",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )