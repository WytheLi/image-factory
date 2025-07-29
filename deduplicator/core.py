import os
from .hashing import ImageHasher
from .database import DatabaseManager
from .storage import StorageProvider


class ImageDeduplicator:
    """图像去重核心类"""

    def __init__(self,
                 storage_provider: StorageProvider,
                 db_manager: DatabaseManager,
                 hasher: ImageHasher = None):
        self.storage = storage_provider
        self.db = db_manager
        self.hasher = hasher or ImageHasher()

    def is_original(self, image_path, threshold=5):
        """检查图像是否原创"""
        new_hash = self.hasher.compute(image_path)
        if not new_hash:
            return False

        # 检查数据库中是否有相似图像
        all_images = self.db.get_all_images()
        for _, _, phash, ahash, dhash in all_images:
            # 使用多种哈希方法检查
            for hash_val in [phash, ahash, dhash]:
                if hash_val and ImageHasher.hamming_distance(new_hash, hash_val) <= threshold:
                    return False
        return True

    def upload_image(self, image_path, remote_folder="images/"):
        """上传并记录图像"""
        if not self.is_original(image_path):
            return None, "Duplicate image"

        # 生成存储路径
        filename = os.path.basename(image_path)
        remote_path = f"{remote_folder}{filename}"

        # 上传到存储
        if not self.storage.upload(image_path, remote_path):
            return None, "Upload failed"

        # 计算多种哈希值
        hashes = {
            'phash': self.hasher.compute(image_path),
            'ahash': ImageHasher(method='ahash').compute(image_path),
            'dhash': ImageHasher(method='dhash').compute(image_path)
        }

        # 保存到数据库
        if self.db.add_image(remote_path, hashes):
            return remote_path, "Success"
        else:
            # 回滚上传
            self.storage.delete(remote_path)
            return None, "Database error"

    def find_duplicates(self, threshold=5):
        """查找所有重复图像"""
        all_images = self.db.get_all_images()
        duplicates = []
        n = len(all_images)

        for i in range(n):
            id1, path1, phash1, ahash1, dhash1 = all_images[i]
            for j in range(i + 1, n):
                id2, path2, phash2, ahash2, dhash2 = all_images[j]

                # 使用多种哈希方法比较
                for hash1, hash2 in [(phash1, phash2), (ahash1, ahash2), (dhash1, dhash2)]:
                    if hash1 and hash2:
                        dist = ImageHasher.hamming_distance(hash1, hash2)
                        if dist <= threshold:
                            duplicates.append((path1, path2, dist))
                            break  # 找到一种匹配即可
        return duplicates

    def check_oss_duplicate(self, image_path, threshold=5):
        """检查OSS中是否有重复图像"""
        new_hash = self.hasher.compute(image_path)
        if not new_hash:
            return []

        # 在数据库中查找相似图像
        return self.db.find_similar(new_hash, threshold=threshold)
