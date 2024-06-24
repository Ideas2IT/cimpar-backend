import logging
from fastapi import APIRouter, Request

from models.encounter_validation import EncounterModel, EncounterUpdateModel
from controller.encounter_controller import EncounterClient
from utils.common_utils import permission_required


router = APIRouter()
logger = logging.getLogger("log")


@router.post("/encounter/{patient_id}")
@permission_required("ENCOUNTER", "WRITE")
async def create_encounter(encounter: EncounterModel, patient_id, request: Request):
    logger.info(f"Request Payload: {encounter}")
    response = EncounterClient.create_encounter(encounter, patient_id)
    logger.info(f"Response Payload: {response}")
    return response


@router.get("/encounter/{patient_id}")
@permission_required("ENCOUNTER", "READ")
async def get_encounter_by_patient_id(patient_id: str, request: Request):
    logger.info(f"Encounter ID:{patient_id}")
    return EncounterClient.get_encounter_by_patient_id(patient_id)


@router.get("/encounter/{patient_id}/{encounter_id}")
@permission_required("ENCOUNTER", "READ")
async def get_encounter_by_id(patient_id: str, encounter_id: str, request: Request):
    logger.info(f"Fetching encounter with Patient ID: {patient_id} and Encounter ID: {encounter_id}")
    return EncounterClient.get_encounter_by_id(patient_id, encounter_id)


@router.get("/encounter")
@permission_required("ENCOUNTER", "READ")
async def get_all_encounters(request: Request):
    logger.info("Fetching all encounters")
    return EncounterClient.get_all_encounters()


@router.put("/encounter/{patient_id}/{encounter_id}")
@permission_required("ENCOUNTER", "EDIT")
async def update_encounter(patient_id: str, encounter_id: str, encounter: EncounterUpdateModel, request: Request):
    logger.info(f"Updating encounter ID:{patient_id}")
    return EncounterClient.update_by_patient_id(patient_id, encounter_id, encounter)


@router.delete("/encounter/{patient_id}/{encounter_id}")
@permission_required("ENCOUNTER", "DELETE")
async def delete_encounter(patient_id: str, encounter_id: str, request: Request):
    logger.info(f"Deleting encounter ID:{patient_id}")
    return EncounterClient.delete_by_encounter_id(patient_id, encounter_id)

