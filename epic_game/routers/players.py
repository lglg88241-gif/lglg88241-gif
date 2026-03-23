from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
import logging
import sqlite3
from database import get_db_connection
from schemas import NewPlayer, GoldUpdate, NewWeapon
from auth import get_password_hash, get_current_user

logger = logging.getLogger("EpicGameAPI")
router = APIRouter(prefix="/players", tags=["公会大厅 (玩家管理)"])

CLASS_MAP = {1: "战士 (Warrior)", 2: "法师 (Mage)", 3: "射手 (Archer)"}

@router.get("/")
def get_all_players(page: int = 1, size: int = 10):
    skip = (max(1, page) - 1) * min(100, size)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM v_player_details LIMIT ? OFFSET ?", (size, skip))
        players = [dict(p) for p in cursor.fetchall()]
        return {"message": "👑 史诗公会花名册", "pagination": {"page": page, "size": size}, "members": players}
    finally:
        conn.close()

@router.get("/{player_name}")
def get_player(player_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_player_details WHERE user_name = ?", (player_name,))
    player = cursor.fetchone()
    conn.close()
    if player: return dict(player)
    raise HTTPException(status_code=404, detail="查无此人")

@router.post("/")
def create_player(player: NewPlayer):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_pwd = get_password_hash(player.password)
        cursor.execute(
            "INSERT INTO players (user_name, class_id, password_hash) VALUES (?, ?, ?)", 
            (player.user_name, player.class_id, hashed_pwd)
        )
        new_player_id = cursor.lastrowid 
        cursor.execute("INSERT INTO assets (owner_id, gold) VALUES (?, ?)", (new_player_id, 50))
        conn.commit()
        return {"message": f"🎉 {player.user_name} 注册成功！"}
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="名字已被占用！")
    finally:
        conn.close()

@router.patch("/{player_name}/gold")
def add_player_gold(player_name: str, update_data: GoldUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player: raise HTTPException(status_code=404, detail="查无此人")
        
        cursor.execute("UPDATE assets SET gold = gold + ? WHERE owner_id = ?", (update_data.add_gold, player['player_id']))
        conn.commit()
        return {"message": f"充值成功，发放 {update_data.add_gold} 金币"}
    finally:
        conn.close()

@router.post("/{player_name}/inventory")
def grant_weapon(player_name: str, weapon: NewWeapon):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player: raise HTTPException(status_code=404, detail="查无此人")
            
        cursor.execute("INSERT INTO inventory (owner_id, item_name) VALUES (?, ?)", (player['player_id'], weapon.item_name))
        conn.commit()
        return {"message": f"玩家 {player_name} 获得了 {weapon.item_name}"}
    finally:
        conn.close()

# 🌟 终极上锁：只有带了有效令牌的人，才能调用 DELETE！
@router.delete("/{player_name}")
def delete_player(
    player_name: str, 
    current_user: Annotated[str, Depends(get_current_user)] # 👈 这就是门禁卡！
):
    logger.warning(f"🚨 管理员 '{current_user}' 正在执行封禁指令：目标 '{player_name}'")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player: raise HTTPException(status_code=404, detail="查无此人")
            
        cursor.execute("DELETE FROM players WHERE player_id = ?", (player['player_id'],))
        conn.commit()
        return {"message": f"管理员 {current_user} 已封禁玩家 {player_name}"}
    finally:
        conn.close()