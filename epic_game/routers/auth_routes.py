from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import logging
from database import get_db_connection
from auth import verify_password, create_access_token
from limiter import limiter

logger = logging.getLogger("EpicGameAPI")
router = APIRouter(tags=["认证中心"]) # 标签用于在 Swagger 中分类

@router.post("/login")
@limiter.limit("5/minute")
# 💡 核心变化：使用 OAuth2PasswordRequestForm 完美对接 Swagger UI 的小锁头
def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    logger.info(f"🛡️ 登录请求: '{form_data.username}'")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 👈 修改 SQL：顺便把 role 也查出来
        cursor.execute("SELECT password_hash, role FROM players WHERE user_name = ?", (form_data.username,))
        user_record = cursor.fetchone()
        
        if not user_record or not verify_password(form_data.password, user_record["password_hash"]):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
            
        # 🌟 把角色信息 (role) 打包刻进 JWT 荧光印章里！
        access_token = create_access_token(data={
            "sub": form_data.username, 
            "role": user_record["role"]
        })
        logger.info(f"✅ 登录成功：已颁发令牌给 '{form_data.username}' (身份: {user_record['role']})")
        
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        conn.close()
