from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Annotated
import logging
import sqlite3
from database import get_db_connection
from schemas import NewPlayer, GoldUpdate, NewWeapon
# 🌟 确保引入了两种安检员：普通安检员(User) 和 霸道保安(Admin)
from auth import get_password_hash, get_current_user, get_current_admin 
from limiter import is_admin_exempt, limiter

logger = logging.getLogger("EpicGameAPI")
router = APIRouter(prefix="/players", tags=["公会大厅 (玩家管理)"])

CLASS_MAP = {1: "战士 (Warrior)", 2: "法师 (Mage)", 3: "射手 (Archer)"}

# ==========================================
# 🔒 [已上锁] 获取全服名单 (需要普通登录)
# ==========================================
@router.get("/")
@limiter.limit("10/minute", exempt_when=is_admin_exempt)
def get_all_players(
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1, 
    size: int = 10
):
    skip = (max(1, page) - 1) * min(100, size)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM v_player_details LIMIT ? OFFSET ?", (size, skip))
        players = [dict(p) for p in cursor.fetchall()]
        return {"message": f"欢迎回来，{current_user['username']}！这是公会花名册", "pagination": {"page": page, "size": size}, "members": players}
    finally:
        conn.close()

# ==========================================
# 🔒 [已上锁] 查看单个玩家详细信息 (需要普通登录)
# ==========================================
@router.get("/{player_name}")
@limiter.limit("10/minute", exempt_when=is_admin_exempt)
def get_player(
    request: Request,
    player_name: str,
    current_user: Annotated[dict, Depends(get_current_user)] # 👈 加锁
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_player_details WHERE user_name = ?", (player_name,))
    player = cursor.fetchone()
    conn.close()
    if player: return dict(player)
    raise HTTPException(status_code=404, detail="查无此人")

# ==========================================
# 🌐 [开放] 注册新玩家 (绝对不能上锁，否则没人能注册了)
# ==========================================
@router.post("/")
@limiter.limit("3/minute")
def create_player(request: Request, player: NewPlayer):
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

# ==========================================
# 👑 [终极门禁] 发金币 (经济大权：必须是 Admin！)
# ==========================================
@router.patch("/{player_name}/gold")
def add_player_gold(
    player_name: str, 
    update_data: GoldUpdate,
    admin_user: Annotated[dict, Depends(get_current_admin)] # 👈 换成超级保安！
):
    current_user_name = admin_user["username"]
    logger.info(f"💰 财务总监 '{current_user_name}' 正在为玩家 '{player_name}' 拨款 {update_data.add_gold} 金币")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player: raise HTTPException(status_code=404, detail="查无此人")
        
        cursor.execute("UPDATE assets SET gold = gold + ? WHERE owner_id = ?", (update_data.add_gold, player['player_id']))
        conn.commit()
        return {"message": f"充值成功，发放 {update_data.add_gold} 金币 (操作人: {current_user_name})"}
    finally:
        conn.close()

# ==========================================
# 👑 [终极门禁] 发武器 (神兵天降：必须是 Admin！)
# ==========================================
@router.post("/{player_name}/inventory")
def grant_weapon(
    player_name: str, 
    weapon: NewWeapon,
    admin_user: Annotated[dict, Depends(get_current_admin)] # 👈 换成超级保安！
):
    current_user_name = admin_user["username"]
    logger.info(f"⚔️ 军械库主管 '{current_user_name}' 正在为玩家 '{player_name}' 锻造神器 【{weapon.item_name}】")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player: raise HTTPException(status_code=404, detail="查无此人")
            
        cursor.execute("INSERT INTO inventory (owner_id, item_name) VALUES (?, ?)", (player['player_id'], weapon.item_name))
        conn.commit()
        return {"message": f"玩家 {player_name} 获得了 {weapon.item_name} (操作人: {current_user_name})"}
    finally:
        conn.close()

# ==========================================
# 👑 [终极门禁] 封禁玩家 (严格校验：必须是 Admin！)
# ==========================================
@router.delete("/{player_name}")
def delete_player(
    player_name: str, 
    admin_user: Annotated[dict, Depends(get_current_admin)] # 👈 唯一一个使用霸道保安的接口！
):
    current_user_name = admin_user["username"]
    logger.warning(f"🚨 管理员 '{current_user_name}' 正在执行封禁指令：目标 '{player_name}'")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player: raise HTTPException(status_code=404, detail="查无此人")
            
        cursor.execute("DELETE FROM players WHERE player_id = ?", (player['player_id'],))
        conn.commit()
        return {"message": f"管理员 {current_user_name} 已封禁玩家 {player_name}"}
    finally:
        conn.close()
