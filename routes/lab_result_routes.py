import logging
from fastapi import APIRouter, Request, Query

from controller.lab_result_controller import ObservationClient
from utils.common_utils import permission_required


router = APIRouter()
logger = logging.getLogger("log")


@router.post("/observation/{patient_id}/{lab_result_id}")
@permission_required("OBSERVATION", "READ")
async def get_lab_result_by_id(patient_id: str, lab_result_id: str, request: Request):
    logger.info(f"Lab Result ID:{patient_id}")
    return ObservationClient.get_lab_result_by_id(patient_id, lab_result_id)


@router.get("/observation")
@permission_required("OBSERVATION", "READ")
async def get_all_lab_result(request: Request, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    logger.info("Fetching all lab results")
    return ObservationClient.get_all_lab_result(page, page_size)


@router.get("/med_name/observation/{name}")
@permission_required("OBSERVATION", "READ")
async def get_lab_result_by_name(name: str, request: Request):
    logger.info(f"Lab Result Name:{name}")
    return ObservationClient.get_lab_result_by_name(name)


@router.get("/observation/{patient_id}")
@permission_required("OBSERVATION", "READ")
async def get_lab_result_by_patient_id(patient_id: str, request: Request):
    logger.info(f"Service History ID:{patient_id}")
    return ObservationClient.get_lab_result_by_patient_id(patient_id)