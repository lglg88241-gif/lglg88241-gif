import logging
import time

import jwt
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from jwt.exceptions import InvalidTokenError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from auth import ALGORITHM, SECRET_KEY
from limiter import limiter, user_role_ctx


class GameBusinessError(Exception):
    pass


from routers import auth_routes, players


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Epic Game API",
    description="史诗公会全栈后台管理系统",
    version="2.0.0",
)


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(GameBusinessError)
async def handle_game_business_error(request: Request, exc: GameBusinessError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "code": "BUSINESS_ERROR",
            "message": str(exc),
        },
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"请求 {request.method} {request.url.path} 耗时: {process_time:.4f} 秒")
    return response


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
