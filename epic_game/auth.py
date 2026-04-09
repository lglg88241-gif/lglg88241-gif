from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from typing import Annotated

from limiter import user_role_ctx


SECRET_KEY = "your-super-secret-key-12345-epic-game-api-is-awesome"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_password_hash(password: str):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str):
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _raise_business_error(message: str):
    from main import GameBusinessError

    raise GameBusinessError(message)


def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None:
            _raise_business_error("无效的登录凭证或令牌已过期")

        request.state.user_role = role
        user_role_ctx.set(role)
        return {"username": username, "role": role}
    except InvalidTokenError:
        _raise_business_error("无效的登录凭证或令牌已过期")


def get_current_admin(current_user: Annotated[dict, Depends(get_current_user)]):
    if current_user.get("role") != "admin":
        _raise_business_error("越权警告：只有公会管理员才能执行此操作")
    return current_user
