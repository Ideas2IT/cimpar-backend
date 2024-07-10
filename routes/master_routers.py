import logging
from fastapi import APIRouter, Request
from utils.common_utils import permission_required
from controller.master_controller import MasterClient

router = APIRouter()
logger = logging.getLogger("log")


@router.get("master/{table_name}")
@permission_required("MASTER", "READ")
async def get_master_value(table_name: str, request: Request):
    logger.info(f"master table {table_name}")
    return MasterClient.get_master_data(table_name)