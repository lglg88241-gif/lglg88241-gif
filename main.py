from fastapi import FastAPI, HTTPException # 👈 引入 HTTPException，用来优雅地报错
from pydantic import BaseModel, Field # 👈 引入 Pydantic 的 Field，它是校验神器！
import sqlite3
import logging 

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s | %(levelname)-8s | %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("EpicGameAPI")

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('epic_game.sqlite')
    conn.row_factory = sqlite3.Row 
    # 🌟 核心唤醒：告诉 SQLite，把外键约束和级联删除 (CASCADE) 给我打开！
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ==========================================
# 🛡️ 终极安保队长 Pydantic 升级版！
# ==========================================
class NewPlayer(BaseModel):
    # 限制名字长度：不能空，最多 20 个字符
    user_name: str = Field(..., min_length=1, max_length=20, description="玩家名称")
    # 🌟 核心防御：限制职业 ID 必须大等于 1，且小等于 3！
    class_id: int = Field(..., ge=1, le=3, description="职业ID (1:战士, 2:法师, 3:射手)")

CLASS_MAP = {
    1: "战士 (Warrior)",
    2: "法师 (Mage)",
    3: "射手 (Archer)"
}

@app.get("/")
def read_root():
    return {"message": "👑 欢迎来到 Epic Game API 数据中心!"}

# ==========================================
# 🌐 API 7: 视察公会大厅 (HTTP GET - 获取全员名单)
# URL 示例: GET /players/
# ==========================================
@app.get("/players/")
def get_all_players():
    logger.info("收到大厅视察请求: 正在拉取全服公会成员花名册...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 直接查询你之前写好的那个神级视图，不加 WHERE 条件，就是全表扫描！
        cursor.execute("SELECT * FROM v_player_details")
        
        # 🌟 核心魔法：fetchall() 会把查到的所有行，打包成一个列表 (List)
        players = cursor.fetchall()
        
        if players:
            # 列表推导式：把列表里的每一行数据，都优雅地转换成 Python 字典
            player_list = [dict(p) for p in players]
            
            logger.info(f"✅ 视察完毕：当前公会共有 {len(player_list)} 名正式成员。")
            return {
                "message": "👑 史诗公会花名册",
                "total_members": len(player_list),
                "members": player_list
            }
        else:
            logger.info("ℹ️ 大厅空无一人。")
            return {
                "message": "公会刚刚建立，还没有任何人加入哦~", 
                "total_members": 0,
                "members": []
            }
            
    except Exception as e:
        logger.error(f"❌ 花名册拉取失败：{e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，获取名单失败")
    finally:
        conn.close()
@app.get("/players/{player_name}")
def get_player(player_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_player_details WHERE user_name = ?", (player_name,))
    player = cursor.fetchone()
    conn.close()

    if player:
        return dict(player)
    else:
        # 使用 HTTPException 抛出标准的 404 错误
        raise HTTPException(status_code=404, detail=f"未找到名为 {player_name} 的玩家")

@app.post("/players/")
def create_player(player: NewPlayer):
    # 因为 Pydantic 已经挡住了所有非法输入，
    # 所以走到这一步的 class_id 绝对只有 1, 2, 3 这三种可能！
    class_name_str = CLASS_MAP[player.class_id]
    
    logger.info(f"收到合法注册请求: 玩家 '{player.user_name}', 职业: {class_name_str}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO players (user_name, class_id) VALUES (?, ?)", 
            (player.user_name, player.class_id)
        )
        new_player_id = cursor.lastrowid 
        
        cursor.execute(
            "INSERT INTO assets (owner_id, gold) VALUES (?, ?)", 
            (new_player_id, 50)
        )
        
        conn.commit()
        logger.info(f"🎉 注册大捷：'{player.user_name}' 入库成功！")
        
        return {
            "message": "🎉 注册成功！",
            "details": f"新进 {class_name_str} 【{player.user_name}】 已加入公会，并获得了 50 枚初始金币！"
        }
        
    except sqlite3.IntegrityError:
        conn.rollback()
        logger.error(f"❌ 注册拒绝：名字 '{player.user_name}' 冲突！")
        # 名字冲突属于前端传来的数据不合规，标准做法是抛出 400 错误
        raise HTTPException(status_code=400, detail="注册失败，该玩家名字已被占用！")
    finally:
        conn.close()


class GoldUpdate(BaseModel):
    # 限定增加的金币数量必须是正数，不能为负（防止黑客反向扣钱）
    add_gold: int = Field(..., gt=0, description="要增加的金币数量")

# ==========================================
# 🌐 API 4: 给玩家发金币 (HTTP PATCH - 局部更新)
# URL 示例: PATCH /players/Arthur/gold
# ==========================================
@app.patch("/players/{player_name}/gold")
def add_player_gold(player_name: str, update_data: GoldUpdate):
    logger.info(f"收到请求: 尝试为玩家 '{player_name}' 增加 {update_data.add_gold} 金币")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 先查出这个玩家的 ID，确保人存在
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        
        if not player:
            logger.warning(f"⚠️ 充值失败：找不到玩家 '{player_name}'")
            raise HTTPException(status_code=404, detail="查无此人，金币发放失败")
            
        player_id = player['player_id']
        
        # 2. 执行核心 SQL 动作：更新金币 (Update)
        # 这里的 UPDATE 语句精准对应了 CRUD 里的 U
        cursor.execute(
            "UPDATE assets SET gold = gold + ? WHERE owner_id = ?",
            (update_data.add_gold, player_id)
        )
        
        # 3. 提交事务
        conn.commit()
        logger.info(f"💰 充值成功：玩家 '{player_name}' 成功入账 {update_data.add_gold} 金币")
        
        # 4. (可选) 为了体验更好，把最新的金币余额查出来返回给前端
        cursor.execute("SELECT gold FROM assets WHERE owner_id = ?", (player_id,))
        new_balance = cursor.fetchone()['gold']
        
        return {
            "message": "充值成功！",
            "details": f"玩家 {player_name} 收到了 {update_data.add_gold} 金币，当前余额为: {new_balance} 金币"
        }
        
    except Exception as e:
        # 兜底报错
        conn.rollback()
        logger.error(f"❌ 充值异常：{e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，充值失败")
    finally:
        conn.close()
# ==========================================
# 🛡️ Pydantic: 定义前端发来的“武器”数据长什么样
# ==========================================
class NewWeapon(BaseModel):
    # 限制武器名字不能为空，且不能超过你在 SQL 里设定的 VARCHAR(50)
    item_name: str = Field(..., min_length=1, max_length=50, description="赐予玩家的武器名称")

# ==========================================
# 🌐 API 6: 给玩家发放神兵利器 (HTTP POST - 新增子资源)
# URL 示例: POST /players/Arthur/inventory
# ==========================================
@app.post("/players/{player_name}/inventory")
def grant_weapon(player_name: str, weapon: NewWeapon):
    logger.info(f"收到神明旨意: 准备为玩家 '{player_name}' 降下神器【{weapon.item_name}】")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 验明正身：先查出这个玩家的 ID
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        
        if not player:
            logger.warning(f"⚠️ 发放失败：世界线中不存在名为 '{player_name}' 的玩家")
            raise HTTPException(status_code=404, detail="查无此人，神器发放失败")
            
        player_id = player['player_id']
        
        # 2. 核心 SQL 动作：新增物品 (C - Create)
        # 向你在建表时完美设计的 inventory 表里插入数据
        cursor.execute(
            "INSERT INTO inventory (owner_id, item_name) VALUES (?, ?)",
            (player_id, weapon.item_name)
        )
        
        # 3. 提交事务
        conn.commit()
        logger.info(f"⚔️ 发放成功：玩家 '{player_name}' 拔出了 {weapon.item_name}！")
        
        return {
            "message": "神器降临！",
            "details": f"恭喜玩家 【{player_name}】 获得了史诗装备：『{weapon.item_name}』！"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 武器发放引发了时空乱流 (异常)：{e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，神器发放失败")
    finally:
        conn.close()

# ==========================================
# 🌐 API 5: 封禁/删除玩家 (终极瘦身版)
# ==========================================
@app.delete("/players/{player_name}")
def delete_player(player_name: str):
    logger.info(f"收到最高指令: 准备将玩家 '{player_name}' 踢出公会并销毁数据")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        
        if not player:
            logger.warning(f"⚠️ 封禁失败：根本找不到名为 '{player_name}' 的玩家")
            raise HTTPException(status_code=404, detail="查无此人，无法执行删除操作")
            
        player_id = player['player_id']
        
        # 🌟 架构师的优雅：因为有了 PRAGMA foreign_keys = ON 和你的 CASCADE，
        # 我们现在只需要这一行代码！数据库会自动把资产表、背包表里的相关数据瞬间清空！
        cursor.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
        
        conn.commit()
        logger.info(f"💀 封禁执行完毕：玩家 '{player_name}' 及其所有附属资产已被物理级联抹除！")
        
        return {
            "message": "封禁成功",
            "details": f"作弊玩家 【{player_name}】 及其所有资产已被永久删除。"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 封禁执行异常：{e}")
        raise HTTPException(status_code=500, detail="服务器内部错误，删除失败")
    finally:
        conn.close()