import logging
from fastapi import APIRouter, Request
from typing import Optional


from utils.common_utils import permission_required
from models.appointment_validation import AppoinmentModel
from controller.appointment_controller import AppointmentClient


router = APIRouter()
logger = logging.getLogger("log")


@router.post("/appointment/{patient_id}")
@permission_required("APPOINTMENT", "WRITE")
async def create_appointment(patient_id: str, app: AppoinmentModel, request: Request):
    logger.info(f"Request Payload: {patient_id}")
    return AppointmentClient.create_appointment(patient_id, app)


@router.get("/appointment")
@permission_required("APPOINTMENT", "READ")
async def get_all_appointment(request: Request):
    logger.info("Fetching all appointment")
    return AppointmentClient.get_all_appointment()


@router.get("/appointment/{patient_id}/{appointment_id}")
@permission_required("APPOINTMENT", "READ")
async def get_by_id(
    request: Request,
    patient_id: Optional[str] = None,
    appointment_id: Optional[str] = None,
    current_medication_id: Optional[str] = None,
    other_medication_id: Optional[str] = None,
    allergy_id: Optional[str] = None,
):
    logger.info("Fetching all appointment")
    return AppointmentClient.get_by_id(
        patient_id,
        appointment_id,
        current_medication_id,
        other_medication_id,
        allergy_id,
    )

@router.get("/appointments/patient_name/{appointment_by_name}")
@permission_required("APPOINTMENT", "READ")
async def get_by_patient_name(name: str, request: Request):
    logger.info(f"fetch appointment for {name}")
    return AppointmentClient.get_by_patient_name(name)


@router.get("/appointments/date_range/{appointment_by_date}")
@permission_required("APPOINTMENT", "READ")
async def get_appointment_by_date(state_date: str, end_date: str, request: Request):
    logger.info(f"fetch appointment between {state_date} and {end_date}")
    return AppointmentClient.get_appointment_by_date(state_date, end_date)

