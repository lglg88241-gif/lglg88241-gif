import sqlite3

# 1. 创建并连接到一个本地数据库文件
conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

# 2. 建表 (Keywords & Data Types)
cursor.execute("""
CREATE TABLE IF NOT EXISTS heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50),
    level INTEGER,
    is_active BOOLEAN
)
""")

# 3. 清空旧数据（为了方便你反复运行测试）
cursor.execute("DELETE FROM heroes")

# 4. 增 (INSERT) - 插入三条数据
cursor.execute("INSERT INTO heroes (name, level, is_active) VALUES ('lglg88241-gif', 99, 1)")
cursor.execute("INSERT INTO heroes (name, level, is_active) VALUES ('Git_Monster', 15, 0)")
cursor.execute("INSERT INTO heroes (name, level, is_active) VALUES ('Python_Novice', 5, 1)")
conn.commit()

# 5. 查 (SELECT & Operators) - 找出等级大于 10 且活跃的英雄
print("🔍 正在执行 SQL 查询...")
print("---------------------------------")
cursor.execute("SELECT name, level FROM heroes WHERE level > 10 AND is_active = 1")

# 获取并打印结果
rows = cursor.fetchall()
for row in rows:
    print(f"✅ 找到符合条件的英雄: 名字={row[0]}, 等级={row[1]}")
print("---------------------------------")

conn.close()