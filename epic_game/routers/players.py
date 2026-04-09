import logging
import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_cache.decorator import cache

from auth import get_current_admin, get_current_user, get_password_hash
from database import get_db_connection
from limiter import is_admin_exempt, limiter
from schemas import GoldUpdate, NewPlayer, NewWeapon


logger = logging.getLogger("EpicGameAPI")
router = APIRouter(prefix="/players", tags=["公会大厅 (玩家管理)"])


def _raise_player_not_found(player_name: str) -> None:
    from main import GameBusinessError

    raise GameBusinessError(f"玩家 '{player_name}' 不存在")


@router.get("/")
@limiter.limit("10/minute", exempt_when=is_admin_exempt)
@cache(expire=60)
def get_all_players(
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = 1,
    size: int = 10,
):
    skip = (max(1, page) - 1) * min(100, size)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        logger.info("真实触发了业务逻辑：正在查询数据库...")
        cursor.execute("SELECT * FROM v_player_details LIMIT ? OFFSET ?", (size, skip))
        players = [dict(p) for p in cursor.fetchall()]
        return {
            "message": f"欢迎回来，{current_user['username']}！这是公会花名册",
            "pagination": {"page": page, "size": size},
            "members": players,
        }
    finally:
        conn.close()


@router.get("/{player_name}")
@limiter.limit("10/minute", exempt_when=is_admin_exempt)
def get_player(
    request: Request,
    player_name: str,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM v_player_details WHERE user_name = ?", (player_name,))
    player = cursor.fetchone()
    conn.close()
    if player:
        return dict(player)
    _raise_player_not_found(player_name)


@router.post("/")
@limiter.limit("3/minute")
def create_player(request: Request, player: NewPlayer):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_pwd = get_password_hash(player.password)
        cursor.execute(
            "INSERT INTO players (user_name, class_id, password_hash) VALUES (?, ?, ?)",
            (player.user_name, player.class_id, hashed_pwd),
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
def add_player_gold(
    player_name: str,
    update_data: GoldUpdate,
    admin_user: Annotated[dict, Depends(get_current_admin)],
):
    current_user_name = admin_user["username"]
    logger.info(
        f"财务总监 '{current_user_name}' 正在为玩家 '{player_name}' 发放 {update_data.add_gold} 金币"
    )

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player:
            _raise_player_not_found(player_name)

        cursor.execute(
            "UPDATE assets SET gold = gold + ? WHERE owner_id = ?",
            (update_data.add_gold, player["player_id"]),
        )
        conn.commit()
        return {
            "message": f"充值成功，发放 {update_data.add_gold} 金币 (操作人: {current_user_name})"
        }
    finally:
        conn.close()


@router.post("/{player_name}/inventory")
def grant_weapon(
    player_name: str,
    weapon: NewWeapon,
    admin_user: Annotated[dict, Depends(get_current_admin)],
):
    current_user_name = admin_user["username"]
    logger.info(
        f"军械库主管 '{current_user_name}' 正在为玩家 '{player_name}' 发放装备 '{weapon.item_name}'"
    )

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player:
            _raise_player_not_found(player_name)

        cursor.execute(
            "INSERT INTO inventory (owner_id, item_name) VALUES (?, ?)",
            (player["player_id"], weapon.item_name),
        )
        conn.commit()
        return {"message": f"玩家 {player_name} 获得了 {weapon.item_name} (操作人: {current_user_name})"}
    finally:
        conn.close()


@router.delete("/{player_name}")
def delete_player(
    player_name: str,
    admin_user: Annotated[dict, Depends(get_current_admin)],
):
    current_user_name = admin_user["username"]
    logger.warning(f"管理员 '{current_user_name}' 正在执行封禁指令，目标: '{player_name}'")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id FROM players WHERE user_name = ?", (player_name,))
        player = cursor.fetchone()
        if not player:
            _raise_player_not_found(player_name)

        cursor.execute("DELETE FROM players WHERE player_id = ?", (player["player_id"],))
        conn.commit()
        return {"message": f"管理员 {current_user_name} 已封禁玩家 {player_name}"}
    finally:
        conn.close()
