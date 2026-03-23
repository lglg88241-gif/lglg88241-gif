from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import logging
from database import get_db_connection
from auth import verify_password, create_access_token

logger = logging.getLogger("EpicGameAPI")
router = APIRouter(tags=["认证中心"]) # 标签用于在 Swagger 中分类

@router.post("/login")
# 💡 核心变化：使用 OAuth2PasswordRequestForm 完美对接 Swagger UI 的小锁头
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    logger.info(f"🛡️ 登录请求: '{form_data.username}'")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM players WHERE user_name = ?", (form_data.username,))
        user_record = cursor.fetchone()
        
        if not user_record or not verify_password(form_data.password, user_record["password_hash"]):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
            
        access_token = create_access_token(data={"sub": form_data.username})
        logger.info(f"✅ 登录成功：已颁发令牌给 '{form_data.username}'")
        
        # 必须返回 access_token 和 token_type 字段，Swagger 锁头才能识别
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        conn.close()