import logging
from fastapi import APIRouter, Request, Query
from typing import Optional, List

from utils.common_utils import permission_required
from models.appointment_validation import AppoinmentModel, StatusModel
from controller.appointment_controller import AppointmentClient

router = APIRouter()
logger = logging.getLogger("log")


@router.post("/appointment/{patient_id}")
@permission_required("APPOINTMENT", "CREATE")
async def create_appointment(patient_id: str, app: AppoinmentModel, request: Request):
    logger.info(f"Request Payload: {patient_id}")
    return AppointmentClient.create_appointment(patient_id, app)


@router.get("/appointment/{patient_id}/{appointment_id}")
@permission_required("APPOINTMENT", "READ")
async def get_by_id(
        request: Request,
        patient_id: Optional[str] = None,
        appointment_id: Optional[str] = None,
    ):
    logger.info("Fetching all appointment")
    return AppointmentClient.get_by_id(
        patient_id,
        appointment_id
    )


@router.get("/appointment")
@permission_required("APPOINTMENT", "ALL_READ")
async def get_appointment(
        request: Request,
        patient_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        service_name: Optional[str] = None,
        page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    logger.info(f"fetching values")
    return AppointmentClient.get_appointment(patient_name, start_date, end_date, service_name, page, page_size)
