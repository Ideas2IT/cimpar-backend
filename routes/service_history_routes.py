import logging
from typing import Optional
from fastapi import APIRouter, Request

from utils.common_utils import permission_required
from controller.service_history_controller import ServiceHistoryClient

router = APIRouter()
logger = logging.getLogger("log")


@router.get("/service_history/{patient_id}/")
@permission_required("IMMUNIZATION", "READ")
async def get_service_history_by_id(
    request: Request,
    patient_id: str,
    page: int,
    count: int,
    all_service: Optional[bool] = None,
    immunization: Optional[bool] = None,
    lab_result: Optional[bool] = None,
    name: Optional[str] = None,
):
    logger.info(f"Service History ID:{patient_id}")
    return ServiceHistoryClient.get_service_history_by_id(
        patient_id, page, count, all_service, immunization, lab_result, name
    )
