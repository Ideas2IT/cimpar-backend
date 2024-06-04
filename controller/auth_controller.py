from fastapi import Response, status, HTTPException
import logging
import traceback

from models.auth_validation import (
    UserModel, TokenModel,
    User, AccessPolicy, UserLink, CimparRole, CimparPermission
)
from services.aidbox_service import AidboxApi
from HL7v2 import get_md5

logger = logging.getLogger("log")


class AuthClient:
    @staticmethod
    def create(user: UserModel):
        try:
            logger.info("Creating the user: %s" % user)
            user_id = get_md5([user.email])
            if user.role.lower() == "admin":
                raise Exception("Not allowed to crate the admin role through API: %s" % user.role)
            cimpar_role = CimparRole.get({"id": user.role})
            if not cimpar_role:
                raise Exception("Given Role is not available with us %s" % user.role)
            if User.get({"id": user_id}):
                raise Exception("User Already Exist %s" % user.email)
            if len(cimpar_role) < 0:
                raise Exception("Unable to fetch the roles.")
            create_user = User(id=user_id, email=user.email, password=user.password)
            create_user.save()
            # Create access policy in Aidbox
            access_policy = AccessPolicy(
                engine="allow",
                link=[UserLink(resourceType="User", id=user_id)]
            )
            access_policy.save()
            # Create Permission
            role_response = CimparPermission(
                id=get_md5([user_id, "PERMISSION"]),
                user_id=UserLink(resourceType="User", id=user_id),
                cimpar_role=UserLink(resourceType="CimparRole", id=user.role)
            )
            role_response.save()
            return {"id": user_id, "email": user.email}
        except Exception as e:
            logger.error(f"Unable to create a user: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_token(token: TokenModel):
        try:
            logger.info("Creating the access token: %s" % token)
            user_id = get_md5([token.username])
            if not User.get({"id": user_id}):
                raise Exception("Given User Not Exist %s" % token.username)
            response = AidboxApi.api_open_request(method="POST", endpoint="/auth/token", json=token.__dict__)
            response.raise_for_status()
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            resp = response.json()
            return {"access_token": resp["access_token"]}
        except Exception as e:
            logger.error(f"Unable to create a token: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(content=str(e), status_code=status.HTTP_400_BAD_REQUEST)

