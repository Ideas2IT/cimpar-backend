from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import sys
import os
from os.path import abspath, dirname, join
from urllib.parse import urljoin
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

# Define the root path of your project
root_path = abspath(dirname(__file__))

# Ensure the integration_pipeline directory is in sys.path
integration_pipeline_path = join(root_path, 'integration-pipeline')
sys.path.insert(0, integration_pipeline_path)

from utils.middleware import add_trace_and_session_id, origins
from utils.logging_config import simple_logger
from utils.config import Logs
from routes import (insurance_routes, integration_pipeline_router, account_router, patient_routes,
                    encounter_routes, medication_routes, condition_allergy_routes, appointment_routes,
                    lab_result_routes, custom_message_router, service_history_routes, master_routers,
                    version_router)


# Load settings
app = FastAPI(docs_url=None)

CIMPAR_BE_VERSION = "1.0.8"

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

# Add the middleware
app.middleware("http")(add_trace_and_session_id)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the logger in the app stateadd_trace_and_session_id
app.state.logger = simple_logger

# Add the Router
app.include_router(account_router.router, prefix="/api", tags=["ACCOUNT"])
app.include_router(integration_pipeline_router.router, prefix="/api/HL7v2", tags=["AIDBOX_INTEGRATION"])
app.include_router(condition_allergy_routes.router, prefix="/api", tags=["ALLERGY_CONDITION"])
app.include_router(appointment_routes.router, prefix="/api", tags=["APPOINTMENT"])
app.include_router(custom_message_router.router, prefix="/api", tags=["CUSTOM_MESSAGE"])
app.include_router(encounter_routes.router, prefix="/api", tags=["ENCOUNTER"])
app.include_router(insurance_routes.router, prefix="/api", tags=["INSURANCE"])
app.include_router(lab_result_routes.router, prefix="/api", tags=["LAB_RESULT"])
app.include_router(master_routers.router, prefix="/api", tags=["MASTER"])
app.include_router(medication_routes.router, prefix="/api", tags=["MEDICATION"])
app.include_router(patient_routes.router, prefix="/api", tags=["PATIENT"])
app.include_router(service_history_routes.router, prefix="/api", tags=["SERVICE_HISTORY"])
app.include_router(version_router.router, prefix="/api", tags=["VERSION"])


@app.get("/api/documentation", include_in_schema=False)
async def get_documentation(request: Request):
    base_url = os.environ.get("BASE_URL", str(request.base_url))
    openapi_url = urljoin(base_url, "api/openapi.json")
    if os.environ.get("ENVIRONMENT").upper() in ("DEVELOPMENT", "QA"):
        return get_swagger_ui_html(openapi_url=openapi_url, title=os.environ.get("APP_DOC_ENVIRONMENT"))
    else:
        return Response(
            content=f"Production Environment documentation is disabled"
        )


@app.get("/api/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    if os.environ.get("ENVIRONMENT").upper() in ("DEVELOPMENT", "QA"):
        return app.openapi()
    else:
        return Response(
            content=f"Production Environment documentation is disabled"
        )


log_path = os.path.join(os.getcwd(), Logs.TAIL_PATH)
simple_logger = logging.getLogger("log")
if not os.path.exists(log_path):
    os.makedirs(log_path)
log_formatter = logging.Formatter(
    '%(asctime)s - %(pathname)20s:%(lineno)4s - %(funcName)20s() - %(levelname)s ## %(message)s')
handler = TimedRotatingFileHandler(log_path + "/" + Logs.FILE_NAME,
                                   when="d",
                                   interval=1,
                                   backupCount=10)
handler.setFormatter(log_formatter)
if not len(simple_logger.handlers):
    simple_logger.addHandler(handler)
simple_logger.setLevel(logging.DEBUG)

app.state.logger = simple_logger


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=os.environ.get("APP_DOC_ENVIRONMENT"),
        version=CIMPAR_BE_VERSION,
        description="Cimpar development API documentation for integrating and testing in the development environment",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []
    try:
        for error in errors:
            formatted_errors.append({
                "field": error['loc'][-1],
                "message": error['msg']
            })
    except Exception as e:
        simple_logger.error(f"Error in exception handler: {e}")
        formatted_errors = errors

    error_response_data = {
        "error": "Validation Error",
        "details": formatted_errors
    }
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response_data)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

