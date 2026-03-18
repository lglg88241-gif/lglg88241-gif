import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🏦 DML 安全防线：Transactions 事务实战 🏦\n")

# ================= 1. 建立极其严格的银行系统 =================
cursor.execute("DROP TABLE IF EXISTS bank_accounts")
# 注意这里的 CHECK 约束：余额绝对不能小于 0！这是触发报警的底线。
cursor.execute("""
CREATE TABLE bank_accounts (
    name VARCHAR(50) PRIMARY KEY,
    balance INTEGER CHECK(balance >= 0) 
)
""")
cursor.executemany("INSERT INTO bank_accounts VALUES (?, ?)", [('Arthur', 100), ('Merlin', 100)])
conn.commit()

print("📊 初始账户状态：")
for row in cursor.execute("SELECT * FROM bank_accounts"): print(f"   [{row[0]}] 余额: {row[1]}")
print("-" * 40 + "\n")

# ================= 2. 成功的事务 (买一瓶 30 块的药水) =================
print("✅ [交易 1] Arthur 花 30 块钱找 Merlin 买药水...")
try:
    # BEGIN：在 Python sqlite3 中，只要你执行 DML，它底层会自动悄悄 BEGIN
    
    # 第一步：扣款
    cursor.execute("UPDATE bank_accounts SET balance = balance - 30 WHERE name = 'Arthur'")
    # 第二步：打款
    cursor.execute("UPDATE bank_accounts SET balance = balance + 30 WHERE name = 'Merlin'")
    
    # 完美执行，永久保存
    conn.commit()
    print("   交易成功！已 Commit。")
except Exception as e:
    conn.rollback()
    print(f"   交易失败：{e}")

# ================= 3. 失败并回滚的事务 (想透支买 999 块的神器) =================
print("\n❌ [交易 2] Arthur 想强行透支 999 块钱买神器...")
try:
    # 第一步：尝试扣款 (这里因为扣完变负数，会立刻触发 CHECK 约束报警)
    cursor.execute("UPDATE bank_accounts SET balance = balance - 999 WHERE name = 'Arthur'")
    
    # 这步根本不会执行到，但为了演示事务结构，我们写在这里
    cursor.execute("UPDATE bank_accounts SET balance = balance + 999 WHERE name = 'Merlin'")
    
    conn.commit()
except sqlite3.IntegrityError as e:
    # 核心魔法来了：捕捉到报错，立刻下达 ROLLBACK 指令！
    conn.rollback()
    print(f"   🚨 警报！触发数据库底线 ({e})")
    print("   ⏪ 正在执行 ROLLBACK (时光倒流)，撤销刚才在这个事务里所做的一切修改...")

print("\n" + "-" * 40)
print("📊 最终账户状态 (看看 Arthur 的钱有没有被错误地扣掉)：")
for row in cursor.execute("SELECT * FROM bank_accounts"): print(f"   [{row[0]}] 余额: {row[1]}")

conn.close()
