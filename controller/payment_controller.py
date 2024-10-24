import logging
import traceback
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse

from aidbox.base import API

from models.payment_validation import PaymentCreateModel, paymentUpdateModel


logger = logging.getLogger("log")


class PaymentClient:
    table = {"payment": "CimparPayment"}

    @staticmethod
    def create_payment(table_name: str, pay: PaymentCreateModel):
        if table_name not in PaymentClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="POST",
                endpoint=f"/{PaymentClient.table[table_name]}",
                json={
                    "patient_id": pay.patient_id,
                    "appointment_id": pay.appointment_id,
                    "payment_amount": pay.payment_amount,
                    "stripe_id": pay.stripe_id,
                    "details": pay.details,
                    "patient_email": pay.patient_email,
                    "transaction_status": pay.transaction_status,
                    "payment_date": pay.payment_date,
                },
            )
            values = master_value.json()
            if master_value.status_code == 201:
                values = master_value.json()
                return values
            else:
                logger.error(master_value.json())
                logger.error(table_name)
                raise Exception("Unable to create")
        except Exception as e:
            logger.error(f"Unable to create: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to create: {e}",
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_by_id(table_name: str, payment_id: str):
        if table_name not in PaymentClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="GET",
                endpoint=f"/{PaymentClient.table[table_name]}/{payment_id}",
            )
            if master_value.status_code == 200:
                master_data = master_value.json()
                return master_data
            else:
                logger.error(master_value.json())
                logger.error(table_name)
                raise Exception("Unable to retrive data")
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve detail",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_all_payment(table_name: str):
        if table_name not in PaymentClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="GET",
                endpoint=f"/{PaymentClient.table[table_name]}/?&_sort=-lastUpdated",
            )
            if master_value.status_code == 200:
                master_data = master_value.json()
                return master_data.get("entry")
            else:
                logger.error(master_value.json())
                logger.error(table_name)
                raise Exception("Unable to retrive data")
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve detail",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def update_by_id(table_name: str, payment_id: str, pay: paymentUpdateModel):
        if table_name not in PaymentClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="PUT",
                endpoint=f"/{PaymentClient.table[table_name]}/{payment_id}",
                json={
                    "patient_id": pay.patient_id,
                    "appointment_id": pay.appointment_id,
                    "payment_amount": pay.payment_amount,
                    "stripe_id": pay.stripe_id,
                    "details": pay.details,
                    "patient_email": pay.patient_email,
                    "transaction_status": pay.transaction_status,
                    "payment_date": pay.payment_date,
                },
            )
            if master_value.status_code == 200:
                values = master_value.json()
                return values
            else:
                logger.error(master_value.json())
                logger.error(table_name)
                raise Exception("Unable to create")
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": str(e),
                "details": f"Unable to fetch the details: {e}",
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def delete_by_id(table_name: str, payment_id: str):
        if table_name not in PaymentClient.table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Kindly, verify the name.",
            )
        try:
            master_value = API.make_request(
                method="DELETE",
                endpoint=f"/{PaymentClient.table[table_name]}/{payment_id}",
            )
            if master_value.status_code == 200:
                master_data = master_value.json()
                return master_data
            else:
                logger.error(master_value.json())
                logger.error(table_name)
                raise Exception("Unable to retrive data")
        except Exception as e:
            logger.error(f"Unable to fetch the details: {e}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve detail",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
