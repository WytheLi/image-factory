from PIL import Image
import imagehash
import numpy as np


class ImageHasher:
    def __init__(self, method='phash', hash_size=8, highfreq_factor=4):
        """
        图像哈希计算器
        :param method: 哈希方法 (phash/ahash/dhash)
        :param hash_size: 哈希尺寸
        :param highfreq_factor: pHash高频因子
        """
        self.method = method
        self.hash_size = hash_size
        self.highfreq_factor = highfreq_factor

    def compute(self, image_path):
        """计算图像哈希值"""
        try:
            with Image.open(image_path) as img:
                return self._compute_hash(img)
        except Exception as e:
            print(f"Error computing hash for {image_path}: {str(e)}")
            return None

    def _compute_hash(self, image):
        """根据配置的算法计算哈希"""
        if self.method == 'phash':      # 感知哈希
            return str(imagehash.phash(image, self.hash_size, self.highfreq_factor))
        elif self.method == 'ahash':    # 平均哈希
            return str(imagehash.average_hash(image, self.hash_size))
        elif self.method == 'dhash':    # 差异哈希
            return str(imagehash.dhash(image, self.hash_size))
        else:
            raise ValueError(f"Unsupported hash method: {self.method}")

    @staticmethod
    def hamming_distance(hash1, hash2):
        """计算汉明距离"""
        if len(hash1) != len(hash2):
            raise ValueError("Hashes must be of same length")

        # 十六进制转二进制
        bin1 = bin(int(hash1, 16))[2:].zfill(64)
        bin2 = bin(int(hash2, 16))[2:].zfill(64)

        return sum(c1 != c2 for c1, c2 in zip(bin1, bin2))

    @staticmethod
    def multi_hash(image_path, methods=('phash', 'ahash')):
        """计算多种哈希组合"""
        with Image.open(image_path) as img:
            return {
                method: str(getattr(imagehash, method)(img))
                for method in methods
            }
