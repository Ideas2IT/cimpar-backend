import logging
from fastapi import APIRouter, Request

from utils.common_utils import permission_required, user_id_context
from models.patient_validation import PatientModel, PatientUpdateModel
from controller.patient_controller import PatientClient


router = APIRouter()
logger = logging.getLogger("log")


@router.post("/patient")
#@permission_required("PATIENT", "WRITE")
async def patient_route(pat: PatientModel, request: Request):
    logger.info(f"Request Payload: {pat}")
    response = PatientClient.create_patient(pat)
    logger.info(f"Request Payload: {response}")
    return response


@router.get("/patients/{patient_id}")
@permission_required("PATIENT", "READ")
async def get_patient(patient_id: str, request: Request):
    logger.info(f"Patient ID:{patient_id}")
    return PatientClient.get_patient_by_id(patient_id)


@router.get("/patients")
@permission_required("PATIENT", "READ")
async def get_all_patients(request: Request):
    logger.info("Fetching all patients")
    return PatientClient.get_all_patients()


@router.put("/patients/{patient_id}")
@permission_required("PATIENT", "UPDATE")
async def update_patient(pat: PatientUpdateModel, patient_id: str, request: Request):
    logger.info(f"Updating patient ID:{pat}")
    return PatientClient.update_patient_by_id(pat, patient_id)


@router.delete("/patients/{patient_id}")
@permission_required("PATIENT", "DELETE")
async def delete_patient(patient_id: str, request: Request):
    logger.info(f"Deleting patient ID:{patient_id}")
    return PatientClient.delete_patient_by_id(patient_id)


@router.get("/profile")
@permission_required("PATIENT", "READ")
async def get_patient(request: Request):
    logger.info(f"Profile Patient ID:{user_id_context.get(None)}")
    return PatientClient.get_patient_by_id(user_id_context.get(None))


@router.get("master/{table_name}")
@permission_required("PATIENT", "READ")
async def get_master_value(table_name: str, request: Request):
    logger.info(f"master table {table_name}")
    return PatientClient.get_master_data(table_name)

