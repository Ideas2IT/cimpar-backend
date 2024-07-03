import logging
import traceback
from fastapi import status
from fastapi.responses import JSONResponse

from aidbox.base import Period,  CodeableConcept, Reference, Coding
from aidbox.resource.encounter import Encounter_Participant, Encounter_Location

from constants import PATIENT_REFERENCE, CLASS_DISPLAY, ENCOUNTER_TYPE_SYSTEM, ENCOUNTER_TYPE_CODE
from models.encounter_validation import EncounterModel, EncounterUpdateModel
from services.aidbox_resource_wrapper import Encounter 


logger = logging.getLogger("log")


class EncounterClient:
    @staticmethod
    def create_encounter(enc: EncounterModel, patient_id):
        try:
            encounter = Encounter(
                status=enc.status,
                class_=Coding(code=enc.class_code, display=CLASS_DISPLAY),
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
                location=[Encounter_Location(location=Reference(display=enc.location))],
            )
            encounter.save()
            response_data = {"id": encounter.id, "created": True}
            logger.info(f"Added Successfully in DB: {response_data}")
            return response_data
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
    def get_encounter_by_patient_id(patient_id: str):
        try:
            encounter = Encounter.make_request(method="GET", endpoint=f"/fhir/Encounter/?subject=Patient/{patient_id}")
            encounter_data = encounter.json()
            if encounter_data.get('total', 0) == 0:
                logger.info(f"No encounters found for patient: {patient_id}")
                return JSONResponse(
                    content={"error": "No encounter found"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            return encounter_data
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
            encounter = Encounter.make_request(method="GET", endpoint=f"/fhir/Encounter/{encounter_id}?subject=Patient/{patient_id}")
            if encounter.status_code == 404:
                logger.info(f"Encounter Not Found: {encounter_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            encounter_json = encounter.json()
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
    def update_by_patient_id(patient_id: str, encounter_id: str, enc: EncounterUpdateModel):
        try:
            response = Encounter.make_request(method="GET", endpoint=f"/fhir/Encounter/{encounter_id}?subject=Patient/{patient_id}")
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
                    status=enc.status,
                    class_=Coding(code=enc.class_code, display=CLASS_DISPLAY),
                    period=Period(start=enc.admission_date, end=enc.discharge_date),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    reasonCode=[CodeableConcept(text=enc.reason)],
                    participant=[Encounter_Participant(individual=Reference(display=enc.primary_care_team))],
                    location=[Encounter_Location(location=Reference(display=enc.location))],
                    )
                encounter.save()
                logger.info(f"Updated Successfully in DB: {patient_id}")
                return {"updated": True, "encounter": encounter.id}    

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
    def get_all_encounters():
        try:
            encounters = Encounter.get()
            if encounters:
                logger.info(f"Encounters Found {len(encounters)}")
                return encounters
            return JSONResponse(
                content={"Error retrieving encounters"}, status_code=status.HTTP_404_NOT_FOUND
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

    # @staticmethod
    # def delete_by_encounter_id(patient_id: str, encounter_id: str):
    #     try:
    #         encounter = Encounter.make_request(method="GET", endpoint=f"/fhir/Encounter/{encounter_id}?subject=Patient/{patient_id}")
    #         existing_encounter = encounter.json()
    #         if encounter.status_code == 404:
    #             logger.info(f"Encounter Not Found: {encounter_id}")
    #             return JSONResponse(
    #                 content={"error": "Patient you have provided was not matched with visit history"},
    #                 status_code=status.HTTP_404_NOT_FOUND
    #             )
    #         if existing_encounter.get("subject", {}).get("reference") == f"Patient/{patient_id}" and existing_encounter.get('id') == encounter_id:
    #             print(existing_encounter)
    #             print("type", type(existing_encounter))
    #             delete_data = Encounter(**existing_encounter)
    #             delete_data.delete()
    #             return {"deleted": True, "encounter": encounter_id}
    #         return JSONResponse(
    #         content={"error": "patient you have provided was not matched with visit history"},
    #         status_code=status.HTTP_404_NOT_FOUND
    #         )
    
    #     except Exception as e:
    #         logger.error(f"Unable to delete encounter: {str(e)}")
    #         logger.error(traceback.format_exc())
    #         error_response_data = {
    #             "error": "Unable to delete visit history",
    #             "details": str(e),
    #         }
    
    #         return JSONResponse(
    #             content=error_response_data,
    #             status_code=status.HTTP_400_BAD_REQUEST
    #         )

    @staticmethod
    def delete_by_patient_id(patient_id: str, encounter_id: str):
        try:
            encounter = Encounter.make_request(method="GET", endpoint=f"/fhir/Encounter/?subject=Patient/{patient_id}")
            print(encounter.json())
            existing_encounter = encounter.json() if encounter else {}
            if existing_encounter.get("total", 0) > 0:
                for item in existing_encounter["entry"]:
                    if item['resource']['id'] == encounter_id:
                        print(item)
                        delete_data = Encounter(**item["resource"])
                        delete_data.delete()
                return {"deleted": True, "encounter": encounter.json()}
            else:
                error_response_data = {
                    "error": "No visit history for this patient"
                }
                return JSONResponse(
                    content=error_response_data,
                    status_code=status.HTTP_400_BAD_REQUEST
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
