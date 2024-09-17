import logging
from typing import Optional
from fastapi import APIRouter, Request

from utils.common_utils import permission_required
from controller.master_controller import MasterClient
from models.master_validation import MasterModel

router = APIRouter()
logger = logging.getLogger("log")


@router.get("/master/{table_name}")
@permission_required("MASTER", "READ_ALL")
async def get_master_value(table_name: str, request: Request):
    logger.info(f"master table {table_name}")
    return MasterClient.get_master_data(table_name)

@router.get("/master/data/{table_name}")
@permission_required("MASTER", "READ")
async def get_master_lab_test_value(table_name: str, request: Request, code: Optional[str] = "", display: Optional[str] = ""):
    logger.info(f"master table {table_name}")
    return MasterClient.fetch_lab_test(table_name, code, display)

@router.post("/master/{table_name}")
@permission_required("MASTER", "CREATE")
async def create_master_values(table_name: str, coding: MasterModel, request: Request):
    logger.info(f"master table {table_name}, values{coding}")
    return MasterClient.create_master_value(table_name, coding)

@router.put("/master/{table_name}")
@permission_required("MASTER", "UPDATE")
async def update_master_values(table_name: str, lab_id: str, coding: MasterModel, request: Request):
    logger.info(f"master table {table_name}, values{coding}")
    return MasterClient.update_master_value(table_name, lab_id, coding)

@router.delete("/master/{table_name}")
@permission_required("MASTER", "UPDATE")
async def delete_master_value(table_name: str, lab_id: str, request: Request):
    logger.info(f"master table {table_name}, lab_id {lab_id}")
    return MasterClient.delete_master_value(table_name, lab_id)