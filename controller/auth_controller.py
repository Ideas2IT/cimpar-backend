from fastapi import Response, status, HTTPException
from fastapi.responses import JSONResponse
import logging
import traceback
from aidbox.base import API
from datetime import datetime, timedelta, timezone
import uuid
import os


from models.auth_validation import (
    UserModel, TokenModel, RotateToken, User, AccessPolicy, CimparRole, CimparPermission, ChangePassword, UserToken
)
from models.patient_validation import PatientModel
from services.aidbox_service import AidboxApi
from utils.common_utils import generate_permission_id, send_email

logger = logging.getLogger("log")


class AuthClient:
    @staticmethod
    def create(user: UserModel, pat: PatientModel):
        try:
            print("pat", pat)
            logger.info("Creating the user: %s" % user)
            user_id = user.id
            if user.role.lower() == "admin":
                raise Exception("Not allowed to crate the admin role through API: %s" % user.role)
            cimpar_role = CimparRole.get({"id": user.role})
            if not cimpar_role:
                raise Exception("Given Role is not available with us %s" % user.role)
            if User.get({"id": user_id}):
                raise Exception("User Already Exist %s" % user.email)
            if len(cimpar_role) < 0:
                raise Exception("Unable to fetch the roles.")
            user_existing = API.make_request(method="GET", endpoint=f"/User/?.email={user.email}")
            if user_existing.json()["total"] != 0:
                raise Exception("Given User Already Exist %s" % user.email)
            create_user = User(id=user_id, email=user.email, inactive=True)
            create_user.save()
            # Create Permission
            role_response = CimparPermission(
                id=generate_permission_id(user_id),
                user_id={"resourceType": "User", "id": user_id},
                cimpar_role={"resourceType": "CimparRole", "id": user.role}
            )
            role_response.save()
            # Create User Token to set the password
            token = uuid.uuid4()
            user_token = UserToken(
                user_id=user_id,
                token=str(token),
                token_expiration=(datetime.now(timezone.utc) + timedelta(hours=48)).isoformat() + 'Z'
            )
            user_token.save()
            confirm_link = os.path.join(os.environ.get("SET_PASSWORD_URL"), str(token))
            image_host = os.environ.get("IMAGE_HOST")
            if pat.createAccount:
                with open('templates/email.html', 'r', encoding='utf-8') as file:
                    email_template = file.read()
                email_body = email_template.replace('{{name}}', user.name).replace(
                    '{{email}}', user.email).replace('{{confirm_link}}', confirm_link).replace(
                    '{{host}}', image_host)
                # Email send
                if not send_email(user.email, email_body):
                    raise Exception("Failed to send confirmation email")
                return {
                    "id": user_id,
                    "email": user.email,
                    #"token": token,
                    "message": "Signup successful! Check your email to set your password."
                }
        except Exception as e:
            logger.error(f"Unable to create a user: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to delete patient",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def confirm_email(token: str, password: str):
        try:
            # Retrieve token from Aidbox
            response = API.make_request(method="GET", endpoint=f"/UserToken/?.token={token}")
            response.raise_for_status()
            token_entry = response.json()['entry'][0]['resource'] if response.json()['entry'] else None

            if not token_entry or datetime.fromisoformat(token_entry['token_expiration'][:-1]) < datetime.now(timezone.utc):
                raise Exception("The confirmation link is invalid or has expired.")

            user_id = token_entry['user_id']

            # Update user password in Aidbox
            user_update_data = {
                "password": password,
                "inactive": False
            }
            response = API.make_request(method="PATCH", endpoint=f"/User/{user_id}", json=user_update_data)
            response.raise_for_status()

            # Create access policy in Aidbox to grant permission to AIDBOX resources
            access_policy = AccessPolicy(
                engine="allow",
                link=[{"resourceType": "User", "id": user_id}]
            )
            access_policy.save()

            # Delete the token from Aidbox
            response = API.make_request(method="DELETE", endpoint=f"/UserToken/{token_entry['id']}")
            response.raise_for_status()

            return {"message": "Your email has been confirmed and password has been set successfully!"}

        except Exception as e:
            logger.error(f"Unable to confirm a token: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to confirm a token",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def create_token(token: TokenModel):
        try:
            resp = None
            # logger.info("Creating the access token: %s" % token)
            # res = API.make_request(method="GET", endpoint=f"/User?.email={token.username}", json=token.__dict__)
            # if res.json()["total"] == 0:
            #     raise Exception("Given User Not Exist %s" % token.username)
            response = AidboxApi.open_request(method="POST", endpoint="/auth/token", json=token.__dict__)
            response.raise_for_status()
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            resp = response.json()
            user_id = resp.get("userinfo", {}).get("id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID not available"
                )
            permission_id = generate_permission_id(user_id)
            perm_res = API.make_request(method="GET", endpoint=f"/CimparPermission/{permission_id}")
            if perm_res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User Permission not available"
                )
            resp["role"] = perm_res.json()["cimpar_role"]["id"]
            return resp
        except Exception as e:
            logger.error(f"Unable to create a token: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create a token",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def rotate_token(token: RotateToken):
        try:
            response = AidboxApi.open_request(method="POST", endpoint="/auth/token", json=token.__dict__)
            response.raise_for_status()
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            resp = response.json()
            return resp
        except Exception as e:
            logger.error(f"Unable to Refresh a token: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to Refresh a token",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def change_password(change: ChangePassword):
        try:
            token = TokenModel(username=change.username, password=change.old_password,
                               client_id=change.client_id, grant_type=change.grant_type)
            resp = AuthClient.create_token(token)
            user_email = resp.get("userinfo", {}).get("email")
            user_id = resp.get("userinfo", {}).get("id")
            if not user_email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Username or password is incorrect."
                )
            password_data = {
                "password": change.new_password,
            }
            response = API.make_request(method="PATCH", endpoint=f"/User/{user_id}", json=password_data)
            response.raise_for_status()
            return {"message": "Password updated successfully"}
        except Exception as e:
            logger.error(f"Unable to change the password: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=f"Unable to change the password: {str(e)}")

    @staticmethod
    def reset_password(email):
        try:
            # Verify if the user exists
            user = API.make_request(method="GET", endpoint=f"/User/?.email={email}")
            if user.json()["total"] == 0:
                raise Exception("User not found")
            user_json = user.json()["entry"][0]["resource"]
            # Check if 24 hours have passed since the last password update
            last_update = datetime.fromisoformat(user_json['meta']['lastUpdated'][:-1]).replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - last_update < timedelta(hours=24):
                raise Exception("Password reset can only be requested 24 hours after the last user update/change")
            # Check for existing valid reset token
            token_response = API.make_request(method="GET", endpoint=f"/UserToken/?.user_id={user_json['id']}")
            if token_response.json()["total"] != 0:
                token_entry = token_response.json()["entry"][0]["resource"]
                token_expiration = datetime.fromisoformat(token_entry['token_expiration'][:-1]).replace(
                    tzinfo=timezone.utc)
                if token_expiration > datetime.now(timezone.utc):
                    raise Exception("A password reset link has already been sent and is still valid. "
                                    "Please check your email.")
                # Delete the expired token
                API.make_request(method="DELETE", endpoint=f"/UserToken/{token_entry['id']}")
            # Create a reset token
            token = uuid.uuid4()
            reset_url = f"/api/confirm/{token}"
            token_expiration = (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat() + 'Z'
            user_token = UserToken(
                user_id=user_json["id"],
                token=str(token),
                token_expiration=token_expiration,
                confirm_url=reset_url
            )
            user_token.save()
            # Send reset email
            email_body = f"Click this link to reset your password: {reset_url}"
            if not send_email(email, email_body):
                raise Exception("Failed to send password reset email")

            return {
                "message": "Password reset email sent",
                "confirm_url": reset_url
            }

        except Exception as e:
            logger.error(f"Unable to request password reset: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to request password reset",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def logout():
        try:
            response = AidboxApi.make_request(method="DELETE", endpoint="/Session")
            response.raise_for_status()
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            resp = response.json()
            return resp
        except Exception as e:
            logger.error(f"Unable to delete the session: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to delete the session",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

