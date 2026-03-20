from fastapi import FastAPI
import sqlite3

app = FastAPI()

def get_db_connection():
    # 连接你亲手设计的史诗公会数据库
    conn = sqlite3.connect('epic_game.sqlite')
    # 让查询结果像字典一样好用
    conn.row_factory = sqlite3.Row 
    return conn

@app.get("/")
def read_root():
    return {"message": "👑 欢迎来到 Epic Game API 数据中心!"}

# 使用了 Path Parameter (路径参数: player_name)
@app.get("/players/{player_name}")
def get_player(player_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ⚠️ 完美结合你学过的 SQL 防注入技术 (?) 和复杂视图 (v_player_details)
    cursor.execute(
        "SELECT * FROM v_player_details WHERE user_name = ?", 
        (player_name,)
    )
    player = cursor.fetchone()
    conn.close()

    if player:
        # FastAPI 会自动把查到的数据转成 JSON 格式
        return dict(player)
    else:
        return {"error": f"未找到名为 {player_name} 的玩家"}