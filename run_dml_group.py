
import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🌟 DML 高阶演练：排序与分组 🌟\n")

# ================= 1. 准备数据环境 =================
# 为了演示，我们先删掉旧表，建一个带“职业”的新表
cursor.execute("DROP TABLE IF EXISTS heroes")
cursor.execute("""
CREATE TABLE heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50),
    role VARCHAR(20),
    level INTEGER
)
""")

# 插入一批测试数据
heroes_data = [
    ('lglg88241-gif', 'Warrior', 99),
    ('Git_Monster', 'Mage', 20),
    ('Python_Novice', 'Mage', 5),
    ('SQL_Master', 'Warrior', 80),
    ('Bug_Maker', 'Archer', 15),
    ('Code_Ninja', 'Archer', 60),
    ('FastAPI_God', 'Mage', 95)
]
cursor.executemany("INSERT INTO heroes (name, role, level) VALUES (?, ?, ?)", heroes_data)
conn.commit()
print("✅ 英雄数据已重新初始化！\n")

# ================= 2. ORDER BY (排序：全服战力榜) =================
print("🏆 全服战力排行榜 (前 3 名) 🏆")
# DESC 表示降序 (从大到小)，ASC 是升序 (从小到大)
# LIMIT 3 表示只取前 3 条
cursor.execute("""
    SELECT name, role, level 
    FROM heroes 
    ORDER BY level DESC 
    LIMIT 3
""")
for rank, row in enumerate(cursor.fetchall(), 1):
    print(f"第 {rank} 名: [{row[1]}] {row[0]} - 等级 {row[2]}")
print("-" * 30 + "\n")

# ================= 3. GROUP BY (分组：各职业数据统计) =================
print("📊 职业战力统计局 📊")
# 我们把英雄按 role 分组，计算每个职业的：总人数(COUNT) 和 平均等级(AVG)
cursor.execute("""
    SELECT role, COUNT(id) as total_heroes, AVG(level) as avg_level 
    FROM heroes 
    GROUP BY role
    ORDER BY avg_level DESC
""")
for row in cursor.fetchall():
    # round() 用来保留两位小数
    print(f"职业: {row[0]:<8} | 总人数: {row[1]} | 平均等级: {round(row[2], 2)}")
print("-" * 30 + "\n")

conn.close()