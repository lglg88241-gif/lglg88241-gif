from fastapi import FastAPI
import logging
from routers import players, auth_routes

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
app.include_router(auth_routes.router)
app.include_router(players.router)

@app.get("/")
def read_root():
    return {"message": "👑 欢迎来到 Epic Game API 数据中心 (模块化重构版)!"}