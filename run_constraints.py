import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

# 🔴 核心操作：强制开启 SQLite 的外键约束防御
cursor.execute("PRAGMA foreign_keys = ON;")

print("🛡️ DDL 终极防御测试：数据约束 (Constraints) 🛡️\n")

# ================= 1. 建立铜墙铁壁 =================
cursor.execute("DROP TABLE IF EXISTS weapons")
cursor.execute("DROP TABLE IF EXISTS players")

# 表 A：玩家表 (集成了 PK, UNIQUE, NOT NULL, CHECK)
cursor.execute("""
CREATE TABLE players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,  -- 必须填名字，且全服唯一
    level INTEGER CHECK(level >= 1)        -- 等级绝不能是 0 或负数
)
""")

# 表 B：武器表 (集成了 FK)
cursor.execute("""
CREATE TABLE weapons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    player_id INTEGER,
    FOREIGN KEY(player_id) REFERENCES players(id) -- 核心：主人ID必须在玩家表里存在！
)
""")
conn.commit()
print("✅ 坚不可摧的双表防线已建立！\n")

# ================= 2. 正常数据录入 =================
cursor.execute("INSERT INTO players (username, level) VALUES ('lglg88241-gif', 99)")
valid_player_id = cursor.lastrowid # 获取刚插入的ID
cursor.execute("INSERT INTO weapons (name, player_id) VALUES ('合法的新手铁剑', ?)", (valid_player_id,))
conn.commit()
print("✅ 合法玩家与装备录入成功！\n")

# ================= 3. 垃圾数据火力全开 (使用 try-except 捕获数据库的怒吼) =================
print("🚨 警报：开始承受垃圾数据的猛烈攻击！🚨")

# 攻击 1: NOT NULL (不写名字)
try:
    cursor.execute("INSERT INTO players (level) VALUES (10)") # 故意漏掉 username
except sqlite3.IntegrityError as e:
    print(f"❌ [NOT NULL 防御成功] 拒绝无名氏: {e}")

# 攻击 2: UNIQUE (名字重复)
try:
    cursor.execute("INSERT INTO players (username, level) VALUES ('lglg88241-gif', 50)")
except sqlite3.IntegrityError as e:
    print(f"❌ [UNIQUE 防御成功] 拒绝盗号狗 (名字已存在): {e}")

# 攻击 3: CHECK (等级开挂)
try:
    cursor.execute("INSERT INTO players (username, level) VALUES ('Hacker', -5)")
except sqlite3.IntegrityError as e:
    print(f"❌ [CHECK 防御成功] 拒绝非法修改 (等级不能小于1): {e}")

# 攻击 4: FOREIGN KEY (发给不存在的人)
try:
    cursor.execute("INSERT INTO weapons (name, player_id) VALUES ('虚空之刃', 9999)")
except sqlite3.IntegrityError as e:
    print(f"❌ [FOREIGN KEY 防御成功] 拒绝幽灵装备 (找不到ID为9999的主人): {e}")

print("\n🎉 所有垃圾数据均被数据库铁门死死挡在门外，你的数据依然纯洁！")
conn.close()
