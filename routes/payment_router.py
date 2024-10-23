import logging
from fastapi import APIRouter, Request

from utils.common_utils import permission_required
from models.payment_validation import PaymentCreateModel, paymentUpdateModel
from controller.payment_controller import PaymentClient

router = APIRouter()
logger = logging.getLogger("log")


@router.post("/payment/{patient_id}")
@permission_required("PAYMENT", "CREATE")
async def create_payment(request: Request, table_name: str, pay: PaymentCreateModel):
    logger.info(f"Payment for:{pay.patient_id}")
    return PaymentClient.create_payment(table_name, pay)


@router.get("/payment/{payment_id}")
@permission_required("PAYMENT", "GET")
async def get_by_id(request: Request, table_name: str, payment_id: str):
    logger.info(f"Fetch Payment:{payment_id}")
    return PaymentClient.get_by_id(table_name, payment_id)


@router.get("/payment")
@permission_required("PAYMENT", "ALL_READ")
async def get_all_payment(
    request: Request,
    table_name: str,
):
    logger.info(f"Fetch Payment:{table_name}")
    return PaymentClient.get_all_payment(table_name)


@router.put("payment/{payment_id}")
@permission_required("PAYMENT", "UPDATE")
async def update_by_id(
    request: Request, table_name: str, payment_id: str, pay: paymentUpdateModel
):
    logger.info(f"Fetch Payment:{payment_id}")
    return PaymentClient.update_by_id(table_name, payment_id, pay)


@router.delete("payment/{payment_id}")
@permission_required("PAYMENT", "DELETE")
async def delete_by_id(request: Request, table_name: str, payment_id: str):
    logger.info(f"Fetch Payment:{payment_id}")
    return PaymentClient.delete_by_id(table_name, payment_id)
