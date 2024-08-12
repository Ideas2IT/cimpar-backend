import json
import logging
from typing import Optional, List
from fastapi import APIRouter, Request, Query, Form, UploadFile, File, status

from starlette.responses import JSONResponse

from constants import VISIT_HISTORY_CONTAINER
from models.encounter_validation import EncounterModel, EncounterUpdateModel
from controller.encounter_controller import EncounterClient
from utils.common_utils import (
    permission_required,
    validate_file_size,
    get_file_extension,
    azure_file_handler,
    generate_random_number,
    delete_file_azure
)

router = APIRouter()
logger = logging.getLogger("log")


@router.post("/encounter/{patient_id}")
@permission_required("ENCOUNTER", "CREATE")
async def create_encounter(
        request: Request,
        patient_id: str,
        location: str = Form(...),
        phone_number: str = Form(...),
        admission_date: str = Form(...),
        discharge_date: str = Form(...),
        reason: str = Form(...),
        primary_care_team: str = Form(...),
        treatment_summary: str = Form(...),
        follow_up_care: str = Form(...),
        activity_notes: str = Form(...),
        file: List[Optional[UploadFile]] = None
):
    # Create EncounterModel instance from form data
    encounter = EncounterModel(
        location=location,
        phone_number=phone_number,
        admission_date=admission_date,
        discharge_date=discharge_date,
        reason=reason,
        primary_care_team=primary_care_team,
        treatment_summary=treatment_summary,
        follow_up_care=follow_up_care,
        activity_notes=activity_notes
    )
    logger.info(f"Request Payload: {encounter}")
    response = EncounterClient.create_encounter(encounter, patient_id)
    response["file_url"] = False
    if file:
        if "id" in response and response["id"]:
            response["file_url"] = []
            count = 0
            for each_file in file:
                count += 1
                file_data = await each_file.read() if each_file else None
                file_extension = get_file_extension(each_file.filename)
                if not validate_file_size(file_data):
                    return JSONResponse(
                        content="File size should be less than 5 MB", status_code=status.HTTP_400_BAD_REQUEST
                    )
                file_path_name = f'{patient_id}/{response["id"]}_{count}{file_extension}'
                logger.info(f'Inserting blob data for path: {file_path_name}')
                blob_url = azure_file_handler(container_name=VISIT_HISTORY_CONTAINER,
                                              blob_name=file_path_name,
                                              blob_data=file_data)
                response["file_url"].append(blob_url)
    logger.info(f"Response Payload: {response}")
    return response


@router.get("/encounter/{patient_id}")
@permission_required("ENCOUNTER", "READ")
async def get_encounter_by_patient_id(
        request: Request,
        patient_id: str,
        page: int = Query(1, ge=1),
        count: int = Query(10, ge=1, le=100)
):
    logger.info(f"Encounter ID:{patient_id}")
    return EncounterClient.get_encounter_by_patient_id(patient_id, page, count)


@router.get("/encounter/{patient_id}/{encounter_id}")
@permission_required("ENCOUNTER", "READ")
async def get_encounter_by_id(patient_id: str, encounter_id: str, request: Request):
    logger.info(f"Fetching encounter with Patient ID: {patient_id} and Encounter ID: {encounter_id}")
    return EncounterClient.get_encounter_by_id(patient_id, encounter_id)


@router.get("/encounter")
@permission_required("ENCOUNTER", "ALL_READ")
async def get_all_encounters(request: Request, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    logger.info("Fetching all encounters")
    return EncounterClient.get_all_encounters(page, page_size)


@router.put("/encounter/{patient_id}/{encounter_id}")
@permission_required("ENCOUNTER", "UPDATE")
async def update_encounter(
        patient_id: str,
        encounter_id: str,
        request: Request,
        location: str = Form(...),
        phone_number: str = Form(...),
        admission_date: str = Form(...),
        discharge_date: str = Form(...),
        reason: str = Form(...),
        primary_care_team: str = Form(...),
        treatment_summary: str = Form(...),
        follow_up_care: str = Form(...),
        activity_notes: str = Form(...),
        file: List[Optional[UploadFile]] = None,
):
    # Create EncounterModel instance from form data
    encounter = EncounterUpdateModel(
        location=location,
        phone_number=phone_number,
        admission_date=admission_date,
        discharge_date=discharge_date,
        reason=reason,
        primary_care_team=primary_care_team,
        treatment_summary=treatment_summary,
        follow_up_care=follow_up_care,
        activity_notes=activity_notes
    )
    file_details = {}
    response = EncounterClient.update_by_patient_id(patient_id, encounter_id, encounter, file_details)
    response["file_url"] = False
    if file:
        if "encounter" in response:
            response["file_url"] = []
            for each_file in file:
                count = generate_random_number()
                file_data = await each_file.read() if each_file else None
                file_extension = get_file_extension(each_file.filename)
                if not validate_file_size(file_data):
                    return JSONResponse(
                        content="File size should be less than 5 MB", status_code=status.HTTP_400_BAD_REQUEST
                    )
                file_path_name = f'{patient_id}/{response["encounter"]}_{count}{file_extension}'
                logger.info(f'Inserting blob data for path: {file_path_name}')
                blob_url = azure_file_handler(container_name=VISIT_HISTORY_CONTAINER,
                                              blob_name=file_path_name,
                                              blob_data=file_data)
                response["file_url"].append(blob_url)
    logger.info(f"Updating encounter ID:{patient_id}")
    return response


@router.delete("/encounter/{patient_id}/{encounter_id}")
@permission_required("ENCOUNTER", "DELETE")
async def delete_encounter(patient_id: str, encounter_id: str, request: Request):
    logger.info(f"Deleting encounter ID:{patient_id}")
    return EncounterClient.delete_by_encounter_id(patient_id, encounter_id)


@router.delete("/encounter/file")
@permission_required("ENCOUNTER", "DELETE")
async def delete_file_encounter(container_name, blob_name, request: Request):
    logger.info(f"Deleting file encounter:{container_name} and {blob_name}")
    return EncounterClient.delete_file(container_name, blob_name)




