import logging
from fastapi import APIRouter, Request

from utils.common_utils import permission_required
from models.medication_validation import MedicationCreateModel, MedicationUpdateModel
from controller.medication_controller import MedicationClient


router = APIRouter()
logger = logging.getLogger("log")


@router.post("/medication/{patient_id}", response_model=dict)
@permission_required("MEDICATION", "WRITE")
async def create_medication(med: MedicationCreateModel, patient_id: str, request: Request):
    logger.info(f"Medication: {med}")
    return MedicationClient.create_medication(med, patient_id)


@router.get("/medication/{patient_id}")
@permission_required("MEDICATION", "READ")
async def get_medication_by_patient_id(patient_id: str, request: Request):
    logger.info(f"Patient ID: {patient_id}")
    return MedicationClient.get_medication_by_patient_id(patient_id)


@router.put("/medication/{patient_id}")
@permission_required("MEDICATION", "UPDATE")
async def update_medication(updated_medication: MedicationUpdateModel, patient_id: str, request: Request):
    logger.info(f"Updated Medication: {updated_medication}")
    return MedicationClient.update_medication_by_patient_id(patient_id, updated_medication)


@router.get("/master/medication/{medication_name}")
@permission_required("MEDICATION", "READ")
async def get_medications_list(medication_name: str, request: Request):
    if len(medication_name) <= 2:
        logger.info("Medication name must be at least 2 characters long.")
        return None
    logger.info(f"Medication Name:{medication_name}")
    return MedicationClient.get_medications(medication_name)