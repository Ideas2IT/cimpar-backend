import base64
import json
import logging
import contextvars
from datetime import datetime, timedelta

import requests
import os
from functools import wraps

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from fastapi import Request
from azure.communication.email import EmailClient
from fastapi import HTTPException
from typing import Type, TypeVar, Dict, Any

from HL7v2 import get_md5
from constants import FILE_SIZE, FILE_ETL_HOUR

T = TypeVar('T')

logger = logging.getLogger("log")

bearer_token = contextvars.ContextVar('bearer_token')
user_id_context = contextvars.ContextVar('user_id')
base = os.environ.get("AIDBOX_URL")

AZURE_COMMUNICATION_CONNECTION_STRING = os.environ.get("AZURE_COMMUNICATION_CONNECTION_STRING")
SENDER_EMAIL_ADDRESS = os.environ.get("SENDER_EMAIL_ADDRESS")


def decode_jwt_without_verification(token):
    # JWTs are split into three parts: header, payload, and signature
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid JWT token")

    payload = parts[1]

    # Base64 decode the header and payload
    payload_decoded = base64.urlsafe_b64decode(payload + '==')

    # Convert from bytes to string
    payload_str = payload_decoded.decode('utf-8')

    # Convert from string to dictionary
    payload_json = json.loads(payload_str)

    return payload_json


def create_request(endpoint, token, method="GET"):
    # Facing circular import if I call the AIDBOX API because of the bearer context variable.
    # So Adding the AIDBOX API call here alone for the permission checks
    url = f"{base}{endpoint}"
    headers = {'authorization': token}
    return requests.request(method, url, headers=headers)


def get_user(user_id: str, auth_token: str):
    response = create_request(method="GET", endpoint=f"/fhir/User/{user_id}", token=auth_token)
    return response.json() if response.status_code == 200 else False


def get_permission(permission_id: str, auth_token: str):
    response = create_request(method="GET", endpoint=f"/fhir/CimparPermission/{permission_id}",
                              token=auth_token)
    return response.json() if response.status_code == 200 else False


def get_privileges(privileges_id: str, auth_token: str):
    response = create_request(method="GET", endpoint=f"/fhir/CimparRole/{privileges_id}",
                              token=auth_token)
    return response.json() if response.status_code == 200 else False


def has_permission(user_id: str, resource: str, action: str, auth_token: str):
    role_id = None
    permission_id = get_md5([user_id, "PERMISSION"])
    permissions = get_permission(permission_id, auth_token)
    if permissions and permissions.get("cimpar_role", {}).get("id"):
        role_id = permissions["cimpar_role"]["id"]
    else:
        return False, role_id
    privileges_json = get_privileges(role_id, auth_token)
    privileges = privileges_json["permissions"][0]["endpoints"]
    for privilege in privileges:
        if (privilege["uri"] == "*" or privilege["uri"].upper() == resource.upper()) and \
                (action.lower() in privilege["action"] or "*" in privilege["action"]):
            return True, role_id
    return False, role_id


def permission_required(resource: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            auth_token = request.headers.get("Authorization")
            if not auth_token:
                raise HTTPException(status_code=403, detail="Authentication token is Mandatory")
            bearer_token.set(auth_token.split("Bearer ")[1])
            payload = decode_jwt_without_verification(auth_token)
            user_id = payload.get("sub")
            user_id_context.set(user_id)
            if not get_user(user_id, auth_token):
                raise HTTPException(status_code=401, detail="Permission denied")
            status, role = has_permission(user_id, resource, action, auth_token)
            if not status:
                raise HTTPException(status_code=403, detail="Permission denied")
            if role.lower() != "admin" and "patient_id" in kwargs:
                patient_id = kwargs.get("patient_id")
                if user_id != patient_id:
                    raise HTTPException(status_code=401, detail="Permission denied: Unauthorized Patient")
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def send_email(recipient_email, body):
    try:
        email_client = EmailClient.from_connection_string(AZURE_COMMUNICATION_CONNECTION_STRING)
        message = {
            "senderAddress": SENDER_EMAIL_ADDRESS,
            "recipients": {
                "to": [{"address": recipient_email}],
            },
            "content": {
                "subject": "Confirm your email address",
                "html": body,
            }
        }
        poller = email_client.begin_send(message)
        result = poller.result()
        logger.info("Email result: %s" % result)
        return True  # Email sent successfully
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


def generate_permission_id(user_id):
    return get_md5([user_id, "PERMISSION"])


def paginate(model: Type[T], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    try:
        query_params = {
            "_count": page_size,
            "_page": page,
            "_sort": "-lastUpdated"
        }
        response = model.get(query_params)
        if "entry" in response and response["entry"]:
            return {
                "data": response["entry"],
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_items": response["total"],
                    "total_pages": (int(response["total"]) // page_size) + 1
                }
            }
        else:
            return {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def azure_file_handler(container_name, blob_name, blob_data=None, fetch=False, delete=False):
    """
    Upload a file to Azure Blob Storage.

    Args:
        container_name (str): The name of the container.
        blob_name (str): The name of the blob.
        blob_data : The data to be uploaded
        fetch (bool): identifier whether to just fetch the URL of existing data
        delete (bool): identifier
    """
    blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("CONNECTION_STRING"))
    container_client = blob_service_client.get_container_client(container_name)
    if delete:
        blob_client = container_client.get_blob_client(blob_name)
        logger.info(f"Deleting the blob for URL: {blob_name}")
        return blob_client.delete_blob()

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=FILE_ETL_HOUR)
    )
    if fetch:
        logger.info(f"Fetching the blob for URL: {blob_name}")
        blob_list = container_client.list_blobs(name_starts_with=blob_name)
        # Iterate over the blobs and find the one you need
        name_list = []
        for each_blob in blob_list:
            name_list.append(each_blob.name)
            blob_client = container_client.get_blob_client(name_list[0])
            return f"{blob_client.url}?{sas_token}" if blob_client.exists() else False
        else:
            return False
    logger.info(f"Creating/ Updating the blob for URL: {blob_name}")
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(blob_data, overwrite=True)
    return f"{blob_client.url}?{sas_token}"


def validate_file_size(file_data):
    logger.info('Validating the size of the file to be uploaded')
    return False if round(len(file_data) / (1024 * 1024), 2) > FILE_SIZE else file_data


def get_file_extension(file_name):
    # os.path.splitext splits the file name into two parts: the base name and the extension
    _, file_extension = os.path.splitext(file_name)
    return file_extension

