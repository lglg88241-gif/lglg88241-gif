# Epic Game API

一个基于 FastAPI 和 SQLite 的练习项目，包含两部分内容：

- `epic_game/`：一个带登录鉴权和角色权限控制的游戏公会管理 API
- 根目录下多个 `run_*.py`：用于演示 SQLite 常见操作的独立脚本

## 项目结构

```text
.
├─ epic_game/
│  ├─ main.py
│  ├─ auth.py
│  ├─ database.py
│  ├─ schemas.py
│  ├─ epic_game.sql
│  └─ routers/
│     ├─ auth_routes.py
│     └─ players.py
├─ migrate.py
├─ run_sql.py
├─ run_ddl.py
├─ run_dml_group.py
├─ run_dml_joins.py
├─ run_all_joins.py
├─ run_subqueries.py
├─ run_functions.py
├─ run_views.py
├─ run_indexes.py
├─ run_constraints.py
├─ run_transactions.py
├─ run_optimization.py
├─ run_security.py
└─ run_sql_file.py
```

## 功能概览

### API 模块

- 玩家注册
- 用户登录并签发 JWT
- 普通用户查询玩家列表和玩家详情
- 管理员为玩家发金币
- 管理员发放武器
- 管理员删除玩家

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
pip install fastapi uvicorn bcrypt pyjwt python-multipart
```

## 初始化数据库

API 使用 `epic_game.sqlite` 作为数据库文件。

1. 进入 `epic_game` 目录。
2. 执行 SQL 初始化脚本。
3. 如有需要，再执行迁移脚本补充密码字段。

示例：

```bash
cd epic_game
sqlite3 epic_game.sqlite < epic_game.sql
cd ..
python migrate.py
python epic_game/fix_pwd.py
```

说明：

- `epic_game/epic_game.sql` 会创建表、视图并插入初始数据
- `migrate.py` 会为 `players` 表补充 `password_hash`
- `epic_game/fix_pwd.py` 会把已有玩家密码统一重置为 `123456`

如果你的数据库已经是最新结构，可以跳过后两步。

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

该接口使用表单提交用户名和密码。登录成功后会返回 Bearer Token。

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

## 独立脚本说明

根目录下的 `run_*.py` 脚本默认操作 `my_first_db.sqlite` 或项目数据库，用于演示不同 SQL 主题。可直接运行，例如：

```bash
python run_sql.py
python run_ddl.py
python run_views.py
```

这些脚本更适合学习和实验，不属于 API 服务启动的必需步骤。

## 当前实现注意点

- `SECRET_KEY` 目前直接写在 `epic_game/auth.py` 中，生产环境应改为环境变量
- 数据库连接目前使用 SQLite 本地文件，适合练习和小规模测试
- 仓库中部分输出文案存在编码显示问题，不影响主要逻辑阅读

## 后续可改进方向

- 增加 `requirements.txt`
- 增加自动化测试
- 用 Alembic 或自定义版本管理替代手动迁移
- 将密钥和数据库路径提取到配置文件或环境变量
