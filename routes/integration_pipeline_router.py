from fastapi import APIRouter, Request, Response, status, Body, Query
import logging
from typing import Optional
from aidbox.base import API
import traceback
import json

from HL7v2.ORU import R01
from HL7v2.VXU import V04
from utils.common_utils import permission_required
from controller.hl7_immunization_controller import HL7ImmunizationClient

router = APIRouter()
logger = logging.getLogger("log")


async def convert_message(message):
    response = API.make_request(
        endpoint="/hl7in/ADT", method="POST", json={"message": message}
    )
    response.raise_for_status()
    return response.json()


async def request_wrapper(raw_data, action):
    try:
        parsed_data = await convert_message(raw_data.decode("utf-8"))
        response = action(parsed_data["parsed"]["parsed"])
        return response
    except Exception as e:
        response = json.dumps({'error': str(e)}).encode('utf-8')
        logger.error("Unable to add the record: %s" % response)
        logger.error(traceback.format_exc())
        return Response(content=response, status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/ORU_R01")
async def hl7v2_oru_r01(request: Request, raw_data: str =Body(..., media_type="text/plain")):
    raw_data = await request.body()
    logger.info("raw_data: %s" % raw_data)
    response = await request_wrapper(raw_data, R01.run)
    logger.info("response: %s" % response)
    return response


@router.post("/VXU_V04")
async def hl7v2_vxu_v04(request: Request, raw_data: str =Body(..., media_type="text/plain")):
    raw_data = await request.body()
    logger.info("raw_data: %s" % raw_data)
    response = await request_wrapper(raw_data, V04.run)
    return response


@router.get("/immunization/{patient_id}")
@permission_required("IMMUNIZATION", "READ")
async def get_immunizations_by_patient_id(patient_id: str, request: Request):
    logger.info(f"Patient ID: {patient_id}")
    return HL7ImmunizationClient.get_immunizations_by_patient_id(patient_id)


@router.get("/immunization/{patient_id}/{immunization_id}")
@permission_required("IMMUNIZATION", "READ")
async def get_immunizations_id(patient_id: str, immunization_id: str, request: Request):
    logger.info(f"Patient ID: {patient_id}")
    return HL7ImmunizationClient.get_immunizations_by_id(patient_id, immunization_id)


@router.get("/immunization")
@permission_required("IMMUNIZATION", "READ")
async def get_immunization(request: Request, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), name: Optional[str] = None):
    logger.info(f"Immunization name: {name}")
    return HL7ImmunizationClient.get_immunization(name, page, page_size)



