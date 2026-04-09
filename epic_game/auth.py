import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from limiter import user_role_ctx

SECRET_KEY = "your-super-secret-key-12345-epic-game-api-is-awesome"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 告诉 FastAPI 小锁头去哪里申请令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_password_hash(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🌟 升级 1：安检员现在会同时读取用户名和角色
def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="无效的登录凭证或令牌已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role") # 👈 提取令牌里的身份牌
        
        if username is None:
            raise credentials_exception
            
        # 返回一个包含丰富信息的字典
        request.state.user_role = role
        user_role_ctx.set(role)
        return {"username": username, "role": role}
    except InvalidTokenError:
        raise credentials_exception
# 🌟 升级 2：新设“管理员专属安检通道”
def get_current_admin(current_user: Annotated[dict, Depends(get_current_user)]):
    # 如果查出你的身份不是 admin，直接一脚踢飞，返回 403 权限不足！
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="🚨 越权警告：只有公会管理员才能执行此神圣指令！")
    return current_user
