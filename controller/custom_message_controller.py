import os
import json
import logging
import traceback
from pathlib import Path

from fastapi import status
from fastapi.responses import JSONResponse
from constants import MESSAGE_PATH

logger = logging.getLogger("log")


class CustomMessageClient:
    @staticmethod
    def get_custom_message():
        cwd = os.getcwd()
        relative_path = os.path.join(cwd, MESSAGE_PATH)
        logger.info(f"Reading message from file: {relative_path}")
        try:
            with open(relative_path, "r") as file:
                logger.info(f"Reading message from file: {relative_path}")
                data = json.load(file)
                logger.info(f"Message read from file: {data}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK, content=data
                )

        except Exception as e:
            logger.error(f"Error retrieving message: {str(e)}")
            logger.error(traceback.format_exc())
            responce = {"message": "Our Services"}   
            return JSONResponse(
                        content=responce, status_code=status.HTTP_200_OK
                    )

    @staticmethod
    def update_custom_message(new_message: str):
        cwd = os.getcwd()
        relative_path = os.path.join(cwd, MESSAGE_PATH)
        try:
            with open(relative_path, "r") as file:
                data = json.load(file)

            data["message"] = new_message

            with open(relative_path, "w") as file:
                json.dump(data, file, indent=4)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Message updated successfully."},
            )

        except Exception as e:
            logger.error(f"Error updating message: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update message",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
