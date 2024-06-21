from fastapi import APIRouter, Request
import logging

from models.insurance_validation import CoverageModel, CoverageUpdateModel
from utils.common_utils import permission_required
from controller.insurance_controller import CoverageClient


router = APIRouter()
logger = logging.getLogger("log")


@router.post('/insurance')
async def insurance_route(ins_plan: CoverageModel, request: Request):
    logger.info(f"Request Payload: {ins_plan}")
    response = CoverageClient.create_coverage(ins_plan)
    logger.info("Response: %s" % response)
    return response


@router.get('/insurance/{patient_id}')
@permission_required("INSURANCE", "READ")
async def get_insurance_by_patient_id(patient_id: str, request: Request):
    logger.info(f"Request Patient_id: {patient_id}")
    return CoverageClient.get_coverage_by_patient_id(patient_id)


@router.put('/insurance/{patient_id}')
@permission_required("INSURANCE", "UPDATE")
async def update_insurance(patient_id: str, updated_insurance: CoverageUpdateModel, request: Request):
    logger.info(f"Request Patient_id: {patient_id}")
    return CoverageClient.update_by_patient_id(patient_id, updated_insurance)


@router.delete('/insurance/{patient_id}')
@permission_required("INSURANCE", "DELETE")
async def delete_insurance(patient_id: str, request: Request):
    logger.info(f"Request Patient_id: {patient_id}")
    return CoverageClient.delete_by_patient_id(patient_id)
