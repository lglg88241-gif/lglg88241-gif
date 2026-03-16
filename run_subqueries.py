import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🪆 DML 高级魔法：Subqueries 子查询套娃 🪆\n")

# ================= 1. 准备数据 =================
cursor.execute("DROP TABLE IF EXISTS heroes")
cursor.execute("CREATE TABLE heroes (id INTEGER PRIMARY KEY, name VARCHAR(50), role VARCHAR(20), level INTEGER)")
heroes_data = [
    (1, 'Arthur', 'Warrior', 80),
    (2, 'Merlin', 'Mage', 90),
    (3, 'Lancelot', 'Warrior', 50),
    (4, 'Gandalf', 'Mage', 95),
    (5, 'Rookie_W', 'Warrior', 10),
    (6, 'Rookie_M', 'Mage', 5)
]
cursor.executemany("INSERT INTO heroes VALUES (?, ?, ?, ?)", heroes_data)
conn.commit()

# ================= 2. Scalar Nested Subquery (标量嵌套子查询) =================
print("🎯 场景 1：找出等级高于【全服平均水平】的精英英雄")
# 逻辑：先算全服平均等级 (内部只运行 1 次)，然后外部把高于这个值的查出来。
cursor.execute("""
    SELECT name, role, level 
    FROM heroes 
    WHERE level > (
        SELECT AVG(level) FROM heroes
    )
""")
print("--- 全服精英 ---")
for row in cursor.fetchall():
    print(f"[{row[1]}] {row[0]} - 等级 {row[2]}")
print("\n")

# ================= 3. Correlated Subquery (相关子查询) =================
print("🔁 场景 2：找出等级高于【自己所在职业平均水平】的内卷王")
# 逻辑：外部 (h1) 每次看一个英雄，内部就要去算一次【这个英雄所属职业】的平均等级。
cursor.execute("""
    SELECT h1.name, h1.role, h1.level 
    FROM heroes h1
    WHERE h1.level > (
        SELECT AVG(h2.level) 
        FROM heroes h2 
        WHERE h2.role = h1.role  -- 核心：内部条件依赖外部的值！
    )
""")
print("--- 职业内卷王 ---")
for row in cursor.fetchall():
    print(f"[{row[1]}] {row[0]} - 等级 {row[2]}")

conn.close()
