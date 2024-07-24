import logging
from fastapi import APIRouter, Request

from utils.common_utils import permission_required
from controller.custom_message_controller import CustomMessageClient


router = APIRouter()
logger = logging.getLogger("log")

@router.get("/custom_message")
@permission_required("MESSAGE", "READ")
async def get_custom_message(request: Request):
    logger.info(f"Request Payload: {request}")
    return CustomMessageClient.get_custom_message()


@router.post("/custom_message/{messge}")  
@permission_required("MESSAGE", "CREATE")
async def update_custom_message(message: str, request: Request):
    logger.info(f"Request Payload: {message}")
    return CustomMessageClient.update_custom_message(message)