import logging
from fastapi import APIRouter, Request

from models.condition_validation import ConditionModel, ConditionUpdateModel
from utils.common_utils import permission_required
from controller.condition_allergy_controller import ConditionClient


router = APIRouter()
logger = logging.getLogger("log")


@router.post("/condition_allergy/{patient_id}")
@permission_required("CONDITION", "WRITE")
async def create_condition_allergy(condition: ConditionModel, request: Request):
    logger.info(f"Request Payload: {condition}")
    response = ConditionClient.create_condition_allergy(condition)
    logger.info(f"Response Payload: {response}")
    return response


@router.get("/condition_allergy/{patient_id}")
@permission_required("CONDITION", "READ")
async def get_condition_allergy(patient_id: str, request: Request):
    response = ConditionClient.get_condition_by_patient_id(patient_id)
    logger.info(f"Response Payload: {response}")
    return response


@router.put("/condition_allergy/{patient_id}")
@permission_required("CONDITION", "UPDATE")
async def update_condition_allergy(patient_id: str, condition: ConditionUpdateModel, request: Request):
    logger.info(f"Request Payload: {condition}")
    response = ConditionClient.update_by_patient_id(patient_id, condition)
    logger.info(f"Response Payload: {response}")
    return response


@router.get("/condition_allergy/{allergy_name}")
@permission_required("CONDITION", "READ")
async def get_allergy_list(allergy_name: str, request: Request):
    if len(allergy_name) <= 2:
        logger.info("Allergy name must be at least 2 characters long.")
        return None
    logger.info(f"Allergy Name:{allergy_name}")
    return ConditionClient.get_allergy_list(allergy_name)