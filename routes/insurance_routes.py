from fastapi import APIRouter, Request, Form, UploadFile, File, status
import logging

from starlette.responses import JSONResponse

from models.insurance_validation import CoverageModel
from utils.common_utils import permission_required, validate_file_size, get_file_extension
from controller.insurance_controller import CoverageClient
from typing import Optional


router = APIRouter()

logger = logging.getLogger("log")


@router.post('/insurance/{patient_id}')
@permission_required("INSURANCE", "CREATE")
async def insurance_route(
        patient_id: str,
        request: Request,
        insurance_type: str = Form(...),
        groupNumber: str = Form(None),
        policyNumber: str = Form(None),
        providerName: str = Form(None),
        file: Optional[UploadFile] = File(None, description="Optional file upload"),
):
    # Create CoverageModel instance from form data
    ins_plan = CoverageModel(
        insurance_type=insurance_type,
        groupNumber=groupNumber,
        policyNumber=policyNumber,
        providerName=providerName
    )
    logger.info(f"Request Payload: {ins_plan}")
    file_data = None
    file_extension = None
    if file:
        file_data = await file.read()
        file_extension = get_file_extension(file.filename)
        if not validate_file_size(file_data):
            return JSONResponse(
                content="File size should be less than 5 MB", status_code=status.HTTP_400_BAD_REQUEST
            )
    response = CoverageClient.create_coverage_insurance(ins_plan, patient_id, file_data, file_extension)
    logger.info("Response: %s" % response)
    return response


@router.get('/insurance/{patient_id}')
@permission_required("INSURANCE", "READ")
async def get_insurance_by_patient_id(patient_id: str, request: Request):
    logger.info(f"Request Patient_id: {patient_id}")
    return CoverageClient.get_coverage_by_patient_id(patient_id)


@router.get('/insurance/{patient_id}/{insurance_id}')
@permission_required("INSURANCE", "READ")
async def get_insurance_by_id(patient_id: str, insurance_id: str, request: Request):
    logger.info(f"Request Patient_id: {patient_id}")
    return CoverageClient.get_coverage_by_id(patient_id, insurance_id)


@router.put('/insurance/{patient_id}')
@permission_required("INSURANCE", "UPDATE")
async def update_insurance(
        patient_id: str,
        request: Request,
        insurance_type: str = Form(...),
        groupNumber: Optional[str] = Form(None),
        policyNumber: Optional[str] = Form(None),
        providerName: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(None, description="Optional file upload"),
        insurance_id: Optional[str] = None):
    # Create CoverageModel instance from form data
    update_insurance_data = CoverageModel(
        insurance_type=insurance_type,
        groupNumber=groupNumber,
        policyNumber=policyNumber,
        providerName=providerName
    )
    file_data = None
    file_extension = None
    if file:
        file_data = await file.read() if file else None
        file_extension = get_file_extension(file.filename)
        if not validate_file_size(file_data):
            return JSONResponse(
                content="File size should be less than 5 MB", status_code=status.HTTP_400_BAD_REQUEST
            )
    logger.info(f"Request Patient_id: {patient_id}")
    return CoverageClient.update_by_insurance_id(patient_id, update_insurance_data, insurance_id, file_data, file_extension)


@router.delete('/insurance/{patient_id}/{insurance_id}')
@permission_required("INSURANCE", "DELETE")
async def delete_insurance(insurance_id: str, patient_id: str, request: Request):
    logger.info(f"Request Patient_id: {insurance_id}")
    return CoverageClient.delete_by_insurance_id(insurance_id, patient_id)

@router.delete('/insurance/file')
@permission_required("INSURANCE", "DELETE")
async def delete_file_insurance(container_name, blob_name, request: Request):
    logger.info(f"Deleting file encounter:{container_name} and {blob_name}")
    return CoverageClient.delete_file(container_name, blob_name)

