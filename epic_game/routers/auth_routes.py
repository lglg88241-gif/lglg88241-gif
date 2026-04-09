import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_access_token, verify_password
from database import get_db_connection
from limiter import limiter


logger = logging.getLogger("EpicGameAPI")
router = APIRouter(tags=["认证中心"])


def _raise_business_error(message: str):
    from main import GameBusinessError

    raise GameBusinessError(message)


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    logger.info(f"登录请求: '{form_data.username}'")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT password_hash, role FROM players WHERE user_name = ?",
            (form_data.username,),
        )
        user_record = cursor.fetchone()

        if not user_record or not verify_password(form_data.password, user_record["password_hash"]):
            _raise_business_error("用户名或密码错误")

        access_token = create_access_token(
            data={"sub": form_data.username, "role": user_record["role"]}
        )
        logger.info(f"登录成功：已颁发令牌给 '{form_data.username}' (身份: {user_record['role']})")

        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        conn.close()
