import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🪢 DML 终极魔法：六大 JOIN 战阵大比拼 🪢\n")

# ================= 1. 准备极度容易区分的数据 =================
cursor.execute("DROP TABLE IF EXISTS heroes")
cursor.execute("DROP TABLE IF EXISTS weapons")
cursor.execute("DROP TABLE IF EXISTS employees")

# 英雄表：有 3 个人（其中 Rookie 没有武器）
cursor.execute("CREATE TABLE heroes (id INTEGER PRIMARY KEY, name VARCHAR(50))")
cursor.executemany("INSERT INTO heroes VALUES (?, ?)", [(1, 'Arthur'), (2, 'Merlin'), (3, 'Rookie')])

# 武器表：有 3 把武器（其中 Lost Shield 找不到主人）
cursor.execute("CREATE TABLE weapons (id INTEGER PRIMARY KEY, w_name VARCHAR(50), hero_id INTEGER)")
cursor.executemany("INSERT INTO weapons VALUES (?, ?, ?)", [(1, 'Excalibur', 1), (2, 'Magic Wand', 2), (3, 'Lost Shield', 99)])

# 员工表（专门为了测试 Self Join：自己连自己）
cursor.execute("CREATE TABLE employees (emp_id INTEGER PRIMARY KEY, emp_name VARCHAR(50), manager_id INTEGER)")
cursor.executemany("INSERT INTO employees VALUES (?, ?, ?)", [(1, '大老板', None), (2, 'Arthur', 1), (3, 'Merlin', 1)])
conn.commit()

# 辅助打印函数
def print_result(cursor, title):
    print(f"--- {title} ---")
    try:
        rows = cursor.fetchall()
        for row in rows:
            print(f"  {row[0]:<8} | {row[1]}")
    except Exception as e:
        print(f"  ⚠️ 你的 SQLite 版本暂不支持此语法，未来在 PostgreSQL 中可正常运行。\n  报错信息: {e}")
    print("\n")

# ================= 2. 六大 JOIN 轮番轰炸 =================

# 1. INNER JOIN (内连接：只有门当户对的才显示)
cursor.execute("""
    SELECT h.name, w.w_name FROM heroes h
    INNER JOIN weapons w ON h.id = w.hero_id
""")
print_result(cursor, "1. INNER JOIN (交集：无武器的人和无主人的武器都被抛弃)")

# 2. LEFT JOIN (左连接：左表绝对不能少，右表没有就填 None)
cursor.execute("""
    SELECT h.name, w.w_name FROM heroes h
    LEFT JOIN weapons w ON h.id = w.hero_id
""")
print_result(cursor, "2. LEFT JOIN (保左表：Rookie 没有武器，显示 None)")

# 3. RIGHT JOIN (右连接：保右表，武器全列出)
try:
    cursor.execute("""
        SELECT h.name, w.w_name FROM heroes h
        RIGHT JOIN weapons w ON h.id = w.hero_id
    """)
    print_result(cursor, "3. RIGHT JOIN (保右表：Lost Shield 没有主人，左侧显示 None)")
except sqlite3.OperationalError as e:
    print(f"--- 3. RIGHT JOIN ---\n  ⚠️ SQLite 限制: {e} (需在 PostgreSQL 中使用)\n")

# 4. FULL OUTER JOIN (全外连接：大锅炖，谁也别丢下)
try:
    cursor.execute("""
        SELECT h.name, w.w_name FROM heroes h
        FULL OUTER JOIN weapons w ON h.id = w.hero_id
    """)
    print_result(cursor, "4. FULL OUTER JOIN (并集：Rookie 和 Lost Shield 全都上榜)")
except sqlite3.OperationalError as e:
    print(f"--- 4. FULL OUTER JOIN ---\n  ⚠️ SQLite 限制: {e} (需在 PostgreSQL 中使用)\n")

# 5. CROSS JOIN (交叉连接：核武器，全排列组合)
cursor.execute("""
    SELECT h.name, w.w_name FROM heroes h
    CROSS JOIN weapons w
""")
print_result(cursor, "5. CROSS JOIN (笛卡尔积：3个英雄 x 3把武器 = 9种硬凑的组合)")

# 6. SELF JOIN (自连接：自己查自己)
cursor.execute("""
    SELECT e1.emp_name AS '员工', e2.emp_name AS '主管'
    FROM employees e1
    LEFT JOIN employees e2 ON e1.manager_id = e2.emp_id
""")
print_result(cursor, "6. SELF JOIN (同一张员工表，找出每个人的主管)")

conn.close()
