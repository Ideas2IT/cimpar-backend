import logging
from fastapi import APIRouter, Request, Query

from utils.common_utils import permission_required
from models.location_validation import LocationModel
from controller.location_controller import LocationClient, LocationDeleteClient

router = APIRouter()
logger = logging.getLogger("log")


@router.post("/location")
@permission_required("LOCATION", "CREATE")
async def create_location(request: Request, table_name: str, loc: LocationModel):
    logger.info(f"Location for:{loc.service_center_name}")
    return LocationClient.create_location(table_name, loc)


@router.get("/location/{location_id}")
@permission_required("LOCATION", "GET")
async def get_by_id(
    request: Request, 
    table_name: str,
    location_id: str
):
    logger.info(f"Fetch Location:{location_id}")
    return LocationClient.get_by_id(table_name, location_id)


@router.get("/location")
@permission_required("LOCATION", "ALL_READ")
async def get_all_location(
    request: Request,
    table_name: str,
    required_all: bool,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),

):
    logger.info(f"Fetch Location")
    return LocationClient.get_all_location(table_name, page, page_size, required_all)


@router.put("location/{location_id}")
@permission_required("LOCATION", "UPDATE")
async def update_by_id(
    request: Request, 
    table_name: str,
    location_id: str, 
    loc: LocationModel
):
    logger.info(f"Fetch Location:{location_id}")
    return LocationClient.update_by_id(table_name, location_id, loc)


@router.delete("location/{location_id}")
@permission_required("LOCATION", "DELETE")
async def delete_by_id(
    request: Request, 
    table_name: str,
    location_id: str,
    location: LocationDeleteClient
):
    logger.info(f"Fetch Location:{location_id}")
    return LocationClient.delete_by_id(table_name, location_id, location)