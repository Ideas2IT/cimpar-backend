import logging
import traceback
from fastapi import Request, status
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()
logger = logging.getLogger("log")


class ExceptionHandlers:
    @staticmethod
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail}")
        logger.error(traceback.format_exc())
        error_response_data = {
            "error": "HTTP Exception",
            "details": exc.detail,
        }
        return JSONResponse(content=error_response_data, status_code=exc.status_code)

    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation Error: {exc.errors()}")
        logger.error(traceback.format_exc())
        error_response_data = {
            "error": "Validation Error",
            "details": exc.errors(),
        }
        return JSONResponse(content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected Error: {str(exc)}")
        logger.error(traceback.format_exc())
        error_response_data = {
            "error": "Unexpected Error",
            "details": str(exc),
        }
        return JSONResponse(content=error_response_data, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Register the exception handlers
app.add_exception_handler(HTTPException, ExceptionHandlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, ExceptionHandlers.validation_exception_handler)
app.add_exception_handler(Exception, ExceptionHandlers.generic_exception_handler)
