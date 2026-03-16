import sqlite3

conn = sqlite3.connect('my_first_db.sqlite')
cursor = conn.cursor()

print("🔥 DML 终极演练：HAVING 与 JOINs 🔥\n")

# ================= 1. 准备双表环境 =================
# 表 A：英雄表 (复用之前的数据)
cursor.execute("DROP TABLE IF EXISTS heroes")
cursor.execute("""
CREATE TABLE heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50),
    role VARCHAR(20),
    level INTEGER
)
""")
heroes_data = [
    ('lglg88241-gif', 'Warrior', 99),
    ('Git_Monster', 'Mage', 20),
    ('Python_Novice', 'Mage', 5),
    ('SQL_Master', 'Warrior', 80),
    ('Bug_Maker', 'Archer', 15)
]
cursor.executemany("INSERT INTO heroes (name, role, level) VALUES (?, ?, ?)", heroes_data)

# 表 B：装备库 (新增！)
# 注意：owner_id 就是用来关联英雄表 id 的关键钥匙（外键概念）
cursor.execute("DROP TABLE IF EXISTS equipment")
cursor.execute("""
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name VARCHAR(50),
    attack_power INTEGER,
    owner_id INTEGER 
)
""")
equip_data = [
    ('屠龙宝刀', 999, 1),      # 对应 id=1 的 lglg88241-gif
    ('生锈的铁剑', 5, 3),      # 对应 id=3 的 Python_Novice
    ('破损的法杖', 10, 2),     # 对应 id=2 的 Git_Monster
    ('无尽之刃', 500, 1),      # 大佬 lglg88241-gif 一个人拿两把武器
    ('无人认领的破鞋', 0, 99)  # 找不到主人的垃圾装备
]
cursor.executemany("INSERT INTO equipment (item_name, attack_power, owner_id) VALUES (?, ?, ?)", equip_data)

conn.commit()
print("✅ 双表环境 (英雄 + 装备) 已就绪！\n")

# ================= 2. HAVING (分组后的二次过滤) =================
print("⚖️ 精英职业筛选局 ⚖️")
# 需求：找出平均等级“大于 30 级”的职业 (过滤掉了平均分太低的菜鸡职业)
cursor.execute("""
    SELECT role, AVG(level) as avg_level 
    FROM heroes 
    GROUP BY role
    HAVING avg_level > 30 
""")
for row in cursor.fetchall():
    print(f"达标职业: {row[0]:<8} | 平均战力: {row[1]}")
print("-" * 30 + "\n")

# ================= 3. INNER JOIN (内连接：神装认主) =================
print("⚔️ 英雄装备盘点 (JOINs 连表查询) ⚔️")
# 需求：把英雄的名字和他们手里的武器名字拼在一起
# 核心逻辑：ON heroes.id = equipment.owner_id (用 ID 把两张表死死锁住)
cursor.execute("""
    SELECT h.name, e.item_name, e.attack_power
    FROM heroes h
    INNER JOIN equipment e ON h.id = e.owner_id
    ORDER BY e.attack_power DESC
""")
for row in cursor.fetchall():
    print(f"[{row[0]}] 装备了: {row[1]} (攻击力 +{row[2]})")
print("-" * 30 + "\n")

conn.close()