import logging
from fastapi import APIRouter, Request

from utils.common_utils import permission_required
from controller.version_controller import VersionClient
from models.version_validation import VersionUpdateModel

router = APIRouter()
logger = logging.getLogger("log")


@router.get("/version")
@permission_required("VERSION", "READ")
async def get_version(request: Request):
    logger.info(f"Request Payload: {request}")
    return VersionClient.get_version()


@router.put("/version")  
@permission_required("MESSAGE", "UPDATE")
async def update_version(message: VersionUpdateModel, request: Request):
    logger.info(f"Request Payload: {message}")
    return VersionClient.update_version(message)