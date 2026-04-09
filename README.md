# Epic Game API

一个基于 FastAPI 和 SQLite 的练习项目，主要包含：

- `epic_game/`：游戏公会管理 API
- 根目录下多个 `run_*.py`：用于演示 SQLite 常见操作的独立脚本

## 项目结构

```text
.
├─ epic_game/
│  ├─ auth.py
│  ├─ database.py
│  ├─ epic_game.sql
│  ├─ epic_game.sqlite
│  ├─ fix_pwd.py
│  ├─ limiter.py
│  ├─ main.py
│  ├─ schemas.py
│  ├─ upgrade_role.py
│  └─ routers/
│     ├─ auth_routes.py
│     └─ players.py
├─ migrate.py
├─ run_all_joins.py
├─ run_constraints.py
├─ run_ddl.py
├─ run_dml_group.py
├─ run_dml_joins.py
├─ run_functions.py
├─ run_indexes.py
├─ run_optimization.py
├─ run_security.py
├─ run_sql.py
├─ run_sql_file.py
├─ run_subqueries.py
├─ run_transactions.py
└─ run_views.py
```

## 功能概览

### API 模块

- 玩家注册
- 用户登录并签发 JWT
- 普通用户查询玩家列表和玩家详情
- 管理员发金币、发武器、删除玩家
- 基于 `slowapi` 的请求限流
- 基于 `fastapi-cache2` 的接口级内存缓存
- 基于中间件的全局接口耗时统计
- 统一的业务异常拦截与标准化 JSON 错误响应
  说明：当前项目中手工编写的业务逻辑报错已统一收口到 `GameBusinessError`

### 当前限流规则

- `POST /login`：`5/minute`
- `POST /players/`：`3/minute`
- `GET /players/`：`10/minute`
- `GET /players/{player_name}`：`10/minute`

查询接口对管理员做了豁免：

- 系统会先从 Bearer Token 中解析角色
- 在请求进入路由前通过中间件把角色写入请求上下文
- 当角色为 `admin` 时，`GET /players/` 和 `GET /players/{player_name}` 不受上述查询限流影响

### SQLite 练习脚本

- 建表、增删改查
- DDL 结构变更
- 分组、连接、子查询、函数、视图
- 索引、约束、事务、性能优化、安全示例

## 环境要求

- Python 3.10+
- SQLite 3

建议先创建虚拟环境，再安装依赖：

```bash
pip install fastapi uvicorn bcrypt pyjwt python-multipart slowapi fastapi-cache2
```

如果你要使用 FastAPI 的 `TestClient` 做测试，还需要：

```bash
pip install httpx
```

## 数据库说明

API 使用的数据库文件是：

```text
epic_game/epic_game.sqlite
```

当前代码已经改成基于文件位置解析数据库路径，所以：

- 从仓库根目录启动可以正常连接数据库
- 从 `epic_game/` 目录启动也可以正常连接数据库
- `migrate.py` 和 `epic_game/fix_pwd.py` 也不再依赖当前工作目录

## 初始化数据库

如果你需要重新初始化：

```bash
cd epic_game
sqlite3 epic_game.sqlite < epic_game.sql
cd ..
python migrate.py
python epic_game/fix_pwd.py
```

说明：

- `epic_game/epic_game.sql`：创建表、视图并插入初始数据
- `migrate.py`：补充 `password_hash`
- `epic_game/fix_pwd.py`：把已有玩家密码统一重置为 `123456`

## 启动 API

在项目根目录执行：

```bash
uvicorn epic_game.main:app --reload --app-dir epic_game
```

启动后可访问：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 认证说明

登录接口：

```http
POST /login
```

该接口使用表单提交用户名和密码，成功后返回 Bearer Token。

Swagger 中可以先调用 `/login`，再点击右上角 `Authorize`，填入：

```text
Bearer <your_access_token>
```

## 主要接口

### 公开接口

- `POST /players/`：注册新玩家
- `POST /login`：用户登录

### 需要登录

- `GET /players/`：分页获取玩家列表
- `GET /players/{player_name}`：获取单个玩家详情

### 需要管理员权限

- `PATCH /players/{player_name}/gold`：给玩家增加金币
- `POST /players/{player_name}/inventory`：发放装备
- `DELETE /players/{player_name}`：删除玩家

## 示例请求

注册玩家：

```json
{
  "user_name": "new_player",
  "password": "123456",
  "class_id": 1
}
```

增加金币：

```json
{
  "add_gold": 100
}
```

发放装备：

```json
{
  "item_name": "Dragon Blade"
}
```

## 当前默认账号

根据当前数据库内容：

- 管理员：`Arthur`
- 普通用户示例：`Lancelot`

如果你执行过 `epic_game/fix_pwd.py`，这些已有账号的密码会被统一重置为：

```text
123456
```

## 独立脚本说明

根目录下的 `run_*.py` 脚本主要用于演示不同 SQL 主题，例如：

```bash
python run_sql.py
python run_ddl.py
python run_views.py
```

这些脚本更适合学习和实验，不属于 API 服务启动的必需步骤。

## 当前实现注意点

- `SECRET_KEY` 当前直接写在 `epic_game/auth.py` 中，生产环境应改为环境变量
- 数据库仍然是本地 SQLite，适合练习和小规模测试
- 限流是进程内生效的，单机开发环境没问题，但不适合作为生产级分布式限流方案

## 后续可改进方向

- 增加 `requirements.txt`
- 增加自动化测试
- 把鉴权密钥和配置移到环境变量
- 使用正式迁移工具替代手动脚本
- 为限流增加更明确的错误响应格式和测试用例
