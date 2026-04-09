import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "epic_game" / "epic_game.sqlite"

def run_migration():
    print("⏳ 正在执行数据库平滑升级...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 这串火星文，正是 "123456" 经过 bcrypt 算法加密后的散列值！
    default_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQ68YlsS"
    
    try:
        # 核心 SQL: ALTER TABLE (修改表结构)
        # 我们给 players 表强行塞入一列 password_hash，并且给老数据填上默认值
        cursor.execute(f"""
            ALTER TABLE players 
            ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '{default_hash}'
        """)
        conn.commit()
        print("✅ 升级成功！已新增密码字段，老玩家的初始密码已统一设置为：123456")
    except sqlite3.OperationalError as e:
        # 如果你重复运行这个脚本，SQLite 会报错说这列已经存在了，我们优雅地拦截它
        print(f"⚠️ 升级跳过：列可能已经存在。({e})")
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
