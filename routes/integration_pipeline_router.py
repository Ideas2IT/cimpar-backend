from fastapi import APIRouter, Request, Response, status, Body, Query, responses
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
async def hl7v2_vxu_v04(
    request: Request,
    raw_data: str =Body(..., media_type="text/plain"),
    icare_patient_id: Optional[str] = None
):
    try:
        raw_data = await request.body()
        logger.info("raw_data: %s" % raw_data)
        parsed_data = await convert_message(raw_data.decode("utf-8"))
        if not parsed_data.get("parsed", {}).get("parsed", None):
            raise Exception("Unable to convert the HL7 message, Please provide the valid HL7 data")
        parsed_data["parsed"]["parsed"]["icare_patient_id"] = icare_patient_id
        response = V04.run(parsed_data["parsed"]["parsed"])
        return response
    except Exception as e:
        logger.error(f"Error creating VXU V04: {str(e)}")
        logger.error(traceback.format_exc())
        error_response_data = {
            "error": "Unable to create Immunization",
            "details": str(e),
        }
        return responses.JSONResponse(
            content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get("/immunization/{patient_id}")
@permission_required("IMMUNIZATION", "READ")
async def find_immunizations_by_patient_id(
    request: Request, 
    patient_id: str,
    vaccine_name: Optional[str] = None,
    immunization_id: Optional[str] = None,
    page: int = Query(1, ge=1), 
    count: int = Query(10, ge=1, le=100)
    ):
    logger.info(f"Immunization for {patient_id} and vaccine for {vaccine_name}")
    if vaccine_name:
        return HL7ImmunizationClient.find_immunizations_by_patient_id(patient_id, vaccine_name, page, count)
    elif immunization_id:
        return HL7ImmunizationClient.get_immunizations_by_id(patient_id, immunization_id)
    return HL7ImmunizationClient.get_immunizations_by_patient_id(patient_id, page, count)
