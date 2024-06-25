import base64
import json
import logging
import contextvars
import requests
import os
from functools import wraps
from fastapi import HTTPException, Request
from azure.communication.email import EmailClient

from HL7v2 import get_md5

logger = logging.getLogger("log")

bearer_token = contextvars.ContextVar('bearer_token')
user_id_context = contextvars.ContextVar('user_id')
base = os.environ.get("AIDBOX_URL")


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
    permission_id = get_md5([user_id, "PERMISSION"])
    permissions = get_permission(permission_id, auth_token)
    if permissions and permissions.get("cimpar_role", {}).get("id"):
        role_id = permissions["cimpar_role"]["id"]
    else:
        return False
    privileges_json = get_privileges(role_id, auth_token)
    privileges = privileges_json["permissions"][0]["endpoints"]
    for privilege in privileges:
        if (privilege["uri"] == "*" or privilege["uri"].upper() == resource.upper()) and \
                (action.lower() in privilege["action"] or "*" in privilege["action"]):
            return True
    return False


def permission_required(resource: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            auth_token = request.headers.get("Authorization")
            bearer_token.set(auth_token.split("Bearer ")[1])
            if not auth_token:
                raise HTTPException(status_code=403, detail="Permission denied: Missing auth_token")
            payload = decode_jwt_without_verification(auth_token)
            user_id = payload.get("sub")
            user_id_context.set(user_id)
            if not get_user(user_id, auth_token):
                raise HTTPException(status_code=403, detail="Permission denied")
            if not has_permission(user_id, resource, action, auth_token):
                raise HTTPException(status_code=403, detail="Permission denied")
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def send_email(recipient_email, body):
    try:
        SENDER_EMAIL_ADDRESS = "DoNotReply@22ed3f1f-75c9-4d5a-9601-788742ad3bf5.azurecomm.net"
        AZURE_COMMUNICATION_CONNECTION_STRING = "your_connection_string"
        email_client = EmailClient.from_connection_string(AZURE_COMMUNICATION_CONNECTION_STRING)
        message = {
            "senderAddress": SENDER_EMAIL_ADDRESS,
            "recipients":  {
                "to": [{"address": recipient_email}],
            },
            "content": {
                "subject": "Confirm your email address",
                "plainText": body,
            }
        }

        poller = email_client.begin_send(message)
        result = poller.result()

        return True  # Email sent successfully

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


def generate_permission_id(user_id):
    return get_md5([user_id, "PERMISSION"])

