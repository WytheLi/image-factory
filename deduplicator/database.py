import sqlite3
from contextlib import contextmanager

from deduplicator.hashing import ImageHasher


class DatabaseManager:
    """数据库管理类"""

    def __init__(self, db_path='image_fingerprint.db'):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """上下文管理器处理数据库连接"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """初始化数据库结构"""
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS images
                         (id INTEGER PRIMARY KEY,
                         storage_path TEXT UNIQUE,
                         phash TEXT,
                         ahash TEXT,
                         dhash TEXT)''')
            conn.commit()

    def add_image(self, storage_path, hashes):
        """添加图像记录"""
        with self._get_connection() as conn:
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO images 
                             (storage_path, phash, ahash, dhash) 
                             VALUES (?, ?, ?, ?)''',
                          (storage_path,
                           hashes.get('phash'),
                           hashes.get('ahash'),
                           hashes.get('dhash')))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # 路径已存在

    def get_all_images(self):
        """获取所有图像记录"""
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, storage_path, phash, ahash, dhash FROM images")
            return c.fetchall()

    def find_similar(self, target_hash, hash_type='phash', threshold=5):
        """查找相似图像"""
        if hash_type not in ['phash', 'ahash', 'dhash']:
            raise ValueError("Invalid hash type")

        query = f"SELECT storage_path, {hash_type} FROM images WHERE {hash_type} IS NOT NULL"
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(query)
            results = []
            for path, hash_val in c.fetchall():
                dist = ImageHasher.hamming_distance(target_hash, hash_val)
                if dist <= threshold:
                    results.append((path, dist))
            return sorted(results, key=lambda x: x[1])  # 按相似度排序
