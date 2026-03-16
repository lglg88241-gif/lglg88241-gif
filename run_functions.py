import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🛠️ DML 瑞士军刀：四大高级函数实战 🛠️\n")

# ================= 1. 制造一批“脏”数据 =================
cursor.execute("DROP TABLE IF EXISTS accounts")
# 包含：名字乱写大小写、有负债、有没有称号的、有注册日期的
cursor.execute("""
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    balance REAL,         -- 存款 (带有小数)
    reg_date DATE,        -- 注册日期
    title VARCHAR(50)     -- 称号 (可能为空)
)
""")
data = [
    (1, 'aRthUr', 'pendragon', 100.567, '2023-01-15', 'Knight'),
    (2, 'MERLIN', 'wizard', -50.2, '2023-11-20', None),       # 名字全大写，欠钱，没称号
    (3, 'rookie', 'boy', 0.99, '2024-03-01', None)          # 名字全小写，没称号
]
cursor.executemany("INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)", data)
conn.commit()

# ================= 2. 字符串 & 数学函数联合技 =================
print("✂️ 1. 字符串与数学加工 (大小写规范化 + 金额四舍五入)")
# - UPPER(SUBSTR(...)): 把首字母大写
# - ROUND(balance, 1): 保留 1 位小数
# - ABS(balance): 提取绝对值
cursor.execute("""
    SELECT 
        UPPER(SUBSTR(first_name, 1, 1)) || LOWER(SUBSTR(first_name, 2)) AS clean_name,
        ROUND(balance, 1) AS rounded_bal,
        ABS(balance) AS absolute_bal
    FROM accounts
""")
for row in cursor.fetchall():
    print(f"规范名字: {row[0]:<10} | 账户余额: {row[1]:<6} | 绝对值(欠款变正): {row[2]}")
print("-" * 40 + "\n")

# ================= 3. 时间魔法 =================
print("⏳ 2. 时间魔法 (计算会员到期日)")
# SQLite 的时间加法：DATE(字段, '+1 year') -> 相当于标准 SQL 的 DATEADD
cursor.execute("""
    SELECT 
        clean_name, 
        reg_date, 
        DATE(reg_date, '+1 year') AS expire_date
    FROM (
        SELECT UPPER(first_name) AS clean_name, reg_date FROM accounts
    )
""")
for row in cursor.fetchall():
    print(f"[{row[0]}] 注册日: {row[1]} -> VIP 到期日: {row[2]}")
print("-" * 40 + "\n")

# ================= 4. 条件逻辑 (CASE 与 COALESCE) =================
print("🧠 3. 逻辑大脑 (状态自动判断 + 空值填补)")
# - CASE WHEN: 动态打标签 (根据余额判断穷富)
# - COALESCE: 填补 NULL (没称号的统一发个'萌新')
cursor.execute("""
    SELECT 
        first_name,
        COALESCE(title, '【无名萌新】') AS display_title,
        CASE 
            WHEN balance < 0 THEN '🔴 欠债老赖'
            WHEN balance < 10 THEN '🟡 穷困潦倒'
            ELSE '🟢 财务自由'
        END AS financial_status
    FROM accounts
""")
for row in cursor.fetchall():
    print(f"英雄: {row[0]:<8} | 称号: {row[1]:<12} | 状态: {row[2]}")

conn.close()
