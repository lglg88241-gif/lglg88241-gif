PRAGMA foreign_keys = ON;
-- =========================================
-- 🧱 阶段一：基建狂魔 (清理旧数据 + 建表)
-- =========================================
-- 销毁顺序很有讲究：先删从表（有外键的），再删主表，否则会报错

DROP VIEW IF EXISTS v_player_details;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS classes;

-- 1. 职业表 (字典表)
CREATE TABLE classes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  class_name VARCHAR(50) UNIQUE NOT NULL -- 职业名称
);

-- 2. 玩家表 (核心表)
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(50) UNIQUE NOT NULL,
    level INTEGER DEFAULT 1 CHECK (level > 0),
    class_id INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- 3. 装备表 (附属表)
CREATE TABLE inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER,
    item_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES players(player_id) ON DELETE CASCADE
);

-- =========================================
-- ✍️ 阶段二：造物主降临 (插入测试数据)
-- =========================================
INSERT INTO classes (class_name) VALUES ('Warrior'), ('Mage'), ('Archer');

INSERT INTO players (user_name, level, class_id) VALUES
('Arthur', 99, 1),   -- 1 是 Warrior
('Lancelot', 50, 1), -- 1 是 Warrior
('Merlin', 80, 2),   -- 2 是 Mage
('Gandalf', 85, 2),  -- 2 是 Mage
('Rookie', 1, 3);    -- 3 是 Archer (穷光蛋新手，等下不给他发装备)

-- 给部分大佬发装备 (owner_id 对应 players 表的 player_id)
INSERT INTO inventory (item_name, owner_id) VALUES 
('Excalibur', 1),     -- 亚瑟的咖喱棒
('Heavy Shield', 1),  -- 亚瑟有两件装备
('Magic Wand', 3),    -- 梅林的法杖
('Elf Bow', 4);       -- 甘道夫拿了弓？(乱发的)
-- 注意：5 号玩家 Rookie 没有任何装备数据

-- =========================================
-- 👁️ 阶段三：情报中心 (极其干练的查询与视图)
-- =========================================
CREATE VIEW v_player_details AS
SELECT 
    p.user_name, 
    p.level, 
    c.class_name, 
    COALESCE(i.item_name, '【包裹空空如也】') AS equipment -- 空值处理神器
FROM players p
INNER JOIN classes c ON p.class_id = c.id    -- 玩家肯定有职业，用 INNER
LEFT JOIN inventory i ON p.player_id = i.owner_id; -- 玩家不一定有装备，必须用 LEFT
