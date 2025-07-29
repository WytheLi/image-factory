from deduplicator.core import ImageDeduplicator
from deduplicator.storage import OSSProvider, LocalStorageProvider
from deduplicator.database import DatabaseManager
from deduplicator.hashing import ImageHasher
from config import config


def main():
    # 初始化组件（oss存储有图片去重机制，这里只是演示）
    storage = OSSProvider(
        config.OSS_ACCESS_KEY,
        config.OSS_SECRET_KEY,
        config.OSS_ENDPOINT,
        config.OSS_BUCKET_NAME
    )

    # 测试时可以使用本地存储
    # storage = LocalStorageProvider(config.LOCAL_STORAGE_PATH)

    db = DatabaseManager(config.DB_PATH)
    hasher = ImageHasher(
        method=config.HASH_METHOD,
        hash_size=config.HASH_SIZE,
        highfreq_factor=config.HIGHFREQ_FACTOR
    )

    deduplicator = ImageDeduplicator(storage, db, hasher)

    # 上传新图片
    image_path = "resources/img/bg1.png"
    result, message = deduplicator.upload_image(image_path)

    if result:
        print(f"Image uploaded successfully: {result}")
    else:
        print(f"Upload failed: {message}")

    # 检查OSS重复
    duplicates = deduplicator.find_duplicates()
    if duplicates:
        print("\nDuplicate images found:")
        for img1, img2, distance in duplicates:
            print(f"- {img1} and {img2} (distance: {distance})")
    else:
        print("\nNo duplicate images found")


if __name__ == "__main__":
    main()
