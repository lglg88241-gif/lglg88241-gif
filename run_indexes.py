import sqlite3
import time

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("⚡ DML 终极加速：Indexes 索引与查询优化实战 ⚡\n")

# ================= 1. 制造 10 万条庞大数据 =================
print("⏳ 正在疯狂插入 10 万条用户数据，请稍等几秒钟...")
cursor.execute("DROP TABLE IF EXISTS massive_users")
cursor.execute("CREATE TABLE massive_users (id INTEGER PRIMARY KEY, username VARCHAR(50))")

# 批量生成 10 万个普通用户
users = [(f"NPC_User_{i}",) for i in range(100000)]
# 在最后悄悄塞入我们的目标用户
users.append(("FastAPI_Ninja_999",)) 

cursor.executemany("INSERT INTO massive_users (username) VALUES (?)", users)
conn.commit()
print("✅ 10 万条数据插入完毕！\n")

# ================= 2. 裸奔查询 (不加索引 = 全表扫描) =================
print("🐢 [测试 1] 不加索引，去 10 万人里捞目标...")

start_time = time.time()
cursor.execute("SELECT * FROM massive_users WHERE username = 'FastAPI_Ninja_999'")
result = cursor.fetchone()
end_time = time.time()

time_without_index = end_time - start_time
print(f"   找到目标: {result}")
print(f"   耗时: {time_without_index:.5f} 秒")

# 揭秘数据库底层是怎么找的 (EXPLAIN QUERY PLAN)
cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM massive_users WHERE username = 'FastAPI_Ninja_999'")
print(f"   底层计划: {cursor.fetchone()[3]} (这意味着它像个傻子一样一行行全查了一遍)\n")


# ================= 3. Managing Indexes (建索引) =================
print("🔨 正在给 username 列加上【索引目录】...")
# 语法：CREATE INDEX 索引名 ON 表名(列名)
cursor.execute("CREATE INDEX idx_username ON massive_users(username)")
conn.commit()
print("✅ 索引建立完成！\n")


# ================= 4. Query Optimization (索引加速查询) =================
print("🚀 [测试 2] 戴上索引光环，再次去 10 万人里捞目标...")

start_time = time.time()
cursor.execute("SELECT * FROM massive_users WHERE username = 'FastAPI_Ninja_999'")
result = cursor.fetchone()
end_time = time.time()

time_with_index = end_time - start_time
print(f"   找到目标: {result}")
print(f"   耗时: {time_with_index:.5f} 秒")

# 再次揭秘底层计划
cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM massive_users WHERE username = 'FastAPI_Ninja_999'")
print(f"   底层计划: {cursor.fetchone()[3]} (完美！它直接翻开目录，锁定了目标！)\n")

# 计算加速比
if time_with_index > 0:
    speedup = time_without_index / time_with_index
    print("-" * 40)
    print(f"🎉 查询优化结论：加了索引后，速度提升了约 {speedup:.1f} 倍！")
    print("-" * 40)

# 收尾：Drop Index (演示如何删除索引)
cursor.execute("DROP INDEX idx_username")

conn.close()
