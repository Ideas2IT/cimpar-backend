import logging
from typing import Optional
from fastapi import APIRouter, Request, Query

from utils.common_utils import permission_required
from controller.service_history_controller import ServiceHistoryClient

router = APIRouter()
logger = logging.getLogger("log")


@router.get("/service_history/{patient_id}/")
@permission_required("IMMUNIZATION", "READ")
async def get_service_history_by_id(
    request: Request,
    patient_id: str,
    service_type = None,
    search_name: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    logger.info(f"Service History ID:{patient_id}")
    return ServiceHistoryClient.get_service_history(
        patient_id, service_type, search_name, page, page_size
    )
