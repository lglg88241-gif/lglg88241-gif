import sqlite3

conn = sqlite3.connect(':memory:') # 这次我们在内存里建个临时库测试
cursor = conn.cursor()

print("🛡️ 数据库终极防线：SQL注入攻防实战 🛡️\n")

# ================= 1. 初始化包含密码的管理员表 =================
cursor.execute("CREATE TABLE admin_users (id INTEGER PRIMARY KEY, username VARCHAR(50), password VARCHAR(50))")
cursor.execute("INSERT INTO admin_users (username, password) VALUES ('admin', 'super_secret_p@ss')")
conn.commit()
print("✅ 系统初始化完成，管理员 admin 的密码极其复杂！\n")

# ================= 2. 致命错误：黑客发起的 SQL 注入攻击 =================
print("💀 [模拟黑客攻击] 菜鸟程序员使用了危险的【字符串拼接】...")

# 黑客在密码框里输入了这段奇怪的文字
hacker_input = "' OR '1'='1" 

# 菜鸟程序员的代码逻辑：
bad_sql = f"SELECT * FROM admin_users WHERE username = 'admin' AND password = '{hacker_input}'"
print(f"   拼接出的灾难 SQL: {bad_sql}")

cursor.execute(bad_sql)
if cursor.fetchone():
    print("   😱 警报！系统沦陷！黑客用 [' OR '1'='1] 导致密码验证逻辑变成永远为真 (True)！黑客无密码登录成功！\n")

# ================= 3. 最佳实践：参数化查询 (Parameterized Queries) =================
print("👮 [绝密防御] 高级工程师使用了【参数化查询(占位符)】...")

# 高级工程师的代码逻辑：用 ? 占位，把输入当做纯文本传递！
good_sql = "SELECT * FROM admin_users WHERE username = ? AND password = ?"
print("   安全的 SQL 模板: SELECT * FROM admin_users WHERE username = ? AND password = ?")

# execute 的第二个参数传入元组，SQLite 底层会自动转义危险字符
cursor.execute(good_sql, ('admin', hacker_input))
if cursor.fetchone():
    print("   😱 (这行永远不会触发)")
else:
    print("   ✅ 防御成功！黑客输入的 [' OR '1'='1] 被数据库死死地当成了一长串普通密码字符串去比对，登录失败！")

conn.close()
