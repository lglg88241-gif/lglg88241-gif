import sqlite3

def upgrade_db_for_rbac():
    print("⏳ 正在为数据库引入 RBAC 角色系统...")
    conn = sqlite3.connect('epic_game.sqlite')
    cursor = conn.cursor()
    
    try:
        # 1. 强行塞入 role 字段，所有老玩家默认都是普通 'user'
        cursor.execute("ALTER TABLE players ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
        
        # 2. 钦定管理员！(假设你的主号叫 Arthur，如果叫别的请自行修改)
        # 这里把 Arthur 破格提拔为 admin
        cursor.execute("UPDATE players SET role = 'admin' WHERE user_name = 'Arthur'")
        
        conn.commit()
        print("✅ 角色系统升级成功！已为所有玩家发放身份牌。")
    except sqlite3.OperationalError as e:
        print(f"⚠️ 升级跳过：列可能已经存在。({e})")
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_db_for_rbac()