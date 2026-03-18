import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🪟 DML 捷径魔法：Views 视图实战 🪟\n")

# ================= 1. 准备复杂的双表底层数据 =================
cursor.execute("DROP TABLE IF EXISTS heroes")
cursor.execute("DROP TABLE IF EXISTS weapons")
cursor.execute("CREATE TABLE heroes (id INTEGER PRIMARY KEY, name VARCHAR(50), level INTEGER)")
cursor.execute("CREATE TABLE weapons (id INTEGER PRIMARY KEY, w_name VARCHAR(50), hero_id INTEGER)")

cursor.executemany("INSERT INTO heroes VALUES (?, ?, ?)", [(1, 'Arthur', 99), (2, 'Merlin', 80), (3, 'Rookie', 5)])
cursor.executemany("INSERT INTO weapons VALUES (?, ?, ?)", [(1, 'Excalibur', 1), (2, 'Magic Wand', 2)])
conn.commit()

# ================= 2. CREATE VIEW (创建视图) =================
print("🔨 正在将复杂的 JOIN 查询封装为视图 [v_elite_arsenal]...")
cursor.execute("DROP VIEW IF EXISTS v_elite_arsenal")

# 我们把一个包含了 INNER JOIN 和 WHERE 过滤的复杂查询，打包成一个视图
cursor.execute("""
    CREATE VIEW v_elite_arsenal AS
    SELECT h.name AS hero_name, h.level, w.w_name AS weapon_name
    FROM heroes h
    INNER JOIN weapons w ON h.id = w.hero_id
    WHERE h.level >= 50
""")
print("✅ 视图创建成功！\n")

# ================= 3. 使用视图 (爽点来了！) =================
print("🖥️ 像查询普通表一样，极其清爽地查询视图：")
# 看！哪怕底层逻辑再复杂，你在业务代码里只需要写这么短一句！
cursor.execute("SELECT * FROM v_elite_arsenal")

for row in cursor.fetchall():
    print(f"精英英雄: {row[0]:<8} | 等级: {row[1]} | 专属武器: {row[2]}")
print("-" * 40 + "\n")

# ================= 4. DROPPING VIEWS (删除视图) =================
print("🗑️ 正在删除视图 [v_elite_arsenal]...")
cursor.execute("DROP VIEW v_elite_arsenal")
print("✅ 视图已销毁 (底层的英雄和武器数据依然完好无损)！")

conn.close()
