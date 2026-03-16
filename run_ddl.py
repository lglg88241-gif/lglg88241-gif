import sqlite3


conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("ddl架构升级")
#1 建一个临时表
cursor.execute("""
CREATE TABLE IF NOT EXISTS temp_weapons (
    id INTEGER PRIMARY KEY ,
    name VARCHAR(50)
)
""")
print("✅ CREATE: 成功创建临时表 temp_weapons")
# 2. ALTER TABLE：老板说英雄们需要武器，我们给之前的 heroes 表加一列！
try:
    cursor.execute("ALTER TABLE heroes ADD COLUMN weapon VARCHAR(50)")
    print("✅ ALTER: 成功给 heroes 表增加了 weapon 列！")
except sqlite3.OperationalError:
    print("⚠️ ALTER: weapon 列已经存在啦，无需重复添加。")

# 给我们的主号发一把神器 (这是DML，顺手做的)
cursor.execute("UPDATE heroes SET weapon = '屠龙宝刀' WHERE name = 'lglg88241-gif'")

# 3. TRUNCATE 概念体现 (清空临时表)
# 注：标准SQL是 TRUNCATE TABLE temp_weapons; SQLite用下面的写法：
cursor.execute("DELETE FROM temp_weapons")
print("✅ TRUNCATE: 成功清空了 temp_weapons 表里的所有数据")

# 4. DROP TABLE：测试完毕，把临时表彻底炸毁
cursor.execute("DROP TABLE temp_weapons")
print("✅ DROP: 成功把 temp_weapons 表从数据库中彻底抹除")

conn.commit()
print("🎉 DDL 升级全部完成！")

# 验证一下：看看英雄表的新结构和数据
cursor.execute("SELECT name, level, weapon FROM heroes WHERE name = 'lglg88241-gif'")
print("---------------------------------")
row = cursor.fetchone()
if row:
    print(f"🦸‍♂️ 英雄状态: 名字={row[0]}, 等级={row[1]}, 武器={row[2]}")
print("---------------------------------")

conn.close()