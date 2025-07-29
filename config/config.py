import os

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "local.env"), case_sensitive=False)

    BASE_PATH: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # OSS 配置
    OSS_ACCESS_KEY: str = 'your_access_key'
    OSS_SECRET_KEY: str = 'your_secret_key'
    OSS_ENDPOINT: str = 'https://oss-cn-hangzhou.aliyuncs.com'
    OSS_BUCKET_NAME: str = 'your-bucket-name'

    # 哈希配置
    HASH_METHOD: str = 'phash'
    HASH_SIZE: int = 8
    HIGHFREQ_FACTOR: int = 4

    # 去重阈值
    SIMILARITY_THRESHOLD: int = 5

    # 存储路径
    DB_PATH: str = 'image_fingerprints.db'
    LOCAL_STORAGE_PATH: str = 'resources/storage'  # 测试用

    # 阿里云DashScope API密钥
    DASHSCOPE_API_KEY: str = 'your_dashscope_api_key'


config = Config()
