from fastapi import APIRouter, Request, Form
import logging

from models.auth_validation import UserModel, TokenModel, RotateToken, ChangePassword
from controller.auth_controller import AuthClient
from utils.common_utils import bearer_token

router = APIRouter()
logger = logging.getLogger("log")


@router.post('/sign_up')
async def create_account(user_plan: UserModel):
    logger.info("Request Payload: %s" % user_plan)
    response = AuthClient.create(user_plan)
    logger.info("Response: %s" % response)
    return response


@router.post("/confirm/{token}")
async def confirm_account(token: str, password: str = Form(...)):
    logger.info("Request Payload: %s" % token)
    response = AuthClient.confirm_email(token, password)
    logger.info("Response: %s" % response)
    return response


@router.post("/reset/{email}")
async def reset_password(email: str):
    logger.info("Request Payload: %s" % email)
    response = AuthClient.reset_password(email)
    logger.info("Response: %s" % response)
    return response


@router.post('/login')
async def create_token(token: TokenModel):
    logger.info("Request Payload: %s" % token)
    response = AuthClient.create_token(token)
    logger.info("Response: %s" % response)
    return response


@router.post('/change_password')
async def change_password(change: ChangePassword):
    logger.info("Request Payload: %s" % change)
    response = AuthClient.change_password(change)
    logger.info("Response: %s" % response)
    return response


@router.post('/rotate_token')
async def rotate_token(token: RotateToken):
    logger.info("Request Payload: %s" % token)
    response = AuthClient.rotate_token(token)
    logger.info("Response: %s" % response)
    return response


@router.post('/logout')
async def logout(request: Request):
    auth_token = request.headers.get("Authorization")
    bearer_token.set(auth_token.split("Bearer ")[1])
    response = AuthClient.logout()
    logger.info("Response: %s" % response)
    return response

