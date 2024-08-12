import os
import json
import logging
import traceback

from fastapi import status
from fastapi.responses import JSONResponse

from constants import VERSION_PATH
from models.version_validation import VersionUpdateModel

logger = logging.getLogger("log")

class VersionClient:
    @staticmethod
    def get_version():
        cwd = os.getcwd()
        relative_path = os.path.join(cwd, VERSION_PATH)
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
    def update_version(data: VersionUpdateModel):
        cwd = os.getcwd()
        relative_path = os.path.join(cwd, VERSION_PATH)
        try:
            with open(relative_path, "r") as file:
                value = json.load(file)
            if data.andriod :
                value["android"] = data.andriod 
            if data.ios:
                value["ios"] = data.ios
            with open(relative_path, "w") as file:
                json.dump(value, file, indent=4)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Version updated successfully."},
            )
        except Exception as e:
            logger.error(f"Error updating version: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update version",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )
