import sqlite3
from auth import get_password_hash

def fix_all_passwords():
    print("⏳ 正在修复老玩家的密码哈希...")
    
    # 1. 调用你自己的 auth.py，生成一个绝对正确的 "123456" 乱码
    correct_hash = get_password_hash("123456")
    
    conn = sqlite3.connect('epic_game.sqlite')
    cursor = conn.cursor()
    
    try:
        # 2. 暴力覆盖：把所有人的密码都统一刷成这个正确的乱码
        cursor.execute("UPDATE players SET password_hash = ?", (correct_hash,))
        conn.commit()
        print("✅ 修复成功！所有老玩家的密码现已真正可用，密码均为：123456")
    except Exception as e:
        print(f"❌ 修复失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_all_passwords()