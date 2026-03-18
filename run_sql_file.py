import sqlite3

# 连接数据库
conn = sqlite3.connect('epic_game.sqlite')
cursor = conn.cursor()

print("🚀 正在将 epic_game.sql 注入数据库引擎...\n")

# 1. 读取纯 SQL 文件并一次性执行 (executescript 是专门执行大段 SQL 文本的神器)
with open('epic_game.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()
cursor.executescript(sql_script)

# 2. 验证阶段三的视图 (直接查我们刚才在 SQL 里建好的虚拟表)
print("📊 [视图查询结果] 全服玩家装备面板：")
for row in cursor.execute("SELECT * FROM v_player_details"):
    print(f"玩家: {row[0]:<10} | 等级: {row[1]:<3} | 职业: {row[2]:<8} | 装备: {row[3]}")

print("\n📈 [统计查询结果] 正在内卷的职业 (人数 > 1)：")
# 验证聚合查询 (分组 + 二次过滤)
stats_sql = """
    SELECT c.class_name, COUNT(p.player_id) as total_ppl, AVG(p.level)
    FROM classes c
    INNER JOIN players p ON c.id = p.class_id
    GROUP BY c.class_name
    HAVING total_ppl > 1
"""
for row in cursor.execute(stats_sql):
    print(f"职业: {row[0]:<8} | 总人数: {row[1]} | 平均等级: {row[2]:.1f}")

conn.close()
