from fastapi import FastAPI, Request
import logging
import jwt
from jwt.exceptions import InvalidTokenError
from routers import players, auth_routes
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from auth import ALGORITHM, SECRET_KEY
from limiter import limiter, user_role_ctx

# 1. 启动全局日志
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s | %(levelname)-8s | %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 2. 实例化应用
app = FastAPI(
    title="Epic Game API",
    description="史诗公会全栈后台管理系统",
    version="2.0.0"
)

# 3. 接入各个“部门”的路由表
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def attach_user_role(request: Request, call_next):
    request.state.user_role = None
    user_role_ctx.set(None)

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
            request.state.user_role = role
            user_role_ctx.set(role)
        except InvalidTokenError:
            pass

    return await call_next(request)

app.include_router(auth_routes.router)
app.include_router(players.router)

@app.get("/")
def read_root():
    return {"message": "👑 欢迎来到 Epic Game API 数据中心 (模块化重构版)!"}
