import sqlite3
import time

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🏎️ 终极对决：烂代码 VS 调优代码实战 🏎️\n")

# ================= 1. 准备靶场数据 =================
cursor.execute("DROP TABLE IF EXISTS players")
cursor.execute("DROP TABLE IF EXISTS scores")
cursor.execute("CREATE TABLE players (id INTEGER PRIMARY KEY, name VARCHAR(50), biography TEXT)") # biography 模拟极大的无用文本
cursor.execute("CREATE TABLE scores (player_id INTEGER, score INTEGER)")

cursor.executemany("INSERT INTO players VALUES (?, ?, ?)", [
    (1, 'Arthur', '一长串不要看的背景故事...'), 
    (2, 'Merlin', '另一长串不要看的废话...'),
    (3, 'Rookie', '毫无用处的描述...')
])
cursor.executemany("INSERT INTO scores VALUES (?, ?)", [(1, 99), (2, 85)])
conn.commit()

# ================= 2. 菜鸟写法 (全盘投影 + 关联子查询) =================
print("❌ [反面教材] 菜鸟写出的灾难级查询...")
# 缺点 1：SELECT * 把没用的 biography 全拉出来了
# 缺点 2：WHERE 里面嵌套了查成绩的子查询 (极其耗时)
bad_sql = """
    SELECT * FROM players p
    WHERE (SELECT score FROM scores s WHERE s.player_id = p.id) > 90
"""
# 看看数据库底层的抱怨
cursor.execute("EXPLAIN QUERY PLAN " + bad_sql)
plan = cursor.fetchall()
print(f"   执行计划: {plan}")
print("   ⚠️ 致命伤：数据库提示 'CORRELATED SCALAR SUBQUERY' (相关标量子查询)。这意味着玩家表有100万人，它就要查100万次成绩表！\n")

# ================= 3. 高手写法 (按需索取 + 高效连表) =================
print("✅ [神级代码] 架构师优化后的查询...")
# 优点 1：只拿 name (Selective Projection)
# 优点 2：用 INNER JOIN 完美替代子查询 (Reducing Subqueries)
good_sql = """
    SELECT p.name 
    FROM players p
    INNER JOIN scores s ON p.id = s.player_id
    WHERE s.score > 90
"""
# 看看数据库底层有多开心
cursor.execute("EXPLAIN QUERY PLAN " + good_sql)
plan = cursor.fetchall()
print(f"   执行计划: {plan}")
print("   🎉 完美优化：完全变成了高效的合并查询，且没有提取任何没用的庞大文本字段！\n")

conn.close()
