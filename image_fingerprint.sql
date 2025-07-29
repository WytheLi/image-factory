-- 创建主表：存储图像元数据和哈希值
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_path TEXT NOT NULL UNIQUE,  -- 存储路径（OSS路径）
    phash TEXT,                        -- 感知哈希值
    ahash TEXT,                        -- 平均哈希值
    dhash TEXT,                        -- 差异哈希值
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 更新时间
);

-- 创建哈希值索引（加速相似性搜索）
CREATE INDEX IF NOT EXISTS idx_phash ON images(phash);
CREATE INDEX IF NOT EXISTS idx_ahash ON images(ahash);
CREATE INDEX IF NOT EXISTS idx_dhash ON images(dhash);

-- 创建存储路径索引（加速路径查找）
CREATE INDEX IF NOT EXISTS idx_storage_path ON images(storage_path);

-- 创建时间索引（用于数据清理）
CREATE INDEX IF NOT EXISTS idx_created_at ON images(created_at);
