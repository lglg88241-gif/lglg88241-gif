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