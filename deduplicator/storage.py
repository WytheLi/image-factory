import os
from abc import ABC, abstractmethod

import oss2


class StorageProvider(ABC):
    """存储提供者抽象类"""

    @abstractmethod
    def upload(self, local_path, remote_path):
        pass

    @abstractmethod
    def download(self, remote_path, local_path):
        pass

    @abstractmethod
    def exists(self, remote_path):
        pass

    @abstractmethod
    def delete(self, remote_path):
        pass


class OSSProvider(StorageProvider):
    """阿里云OSS存储实现"""

    def __init__(self, access_key, secret_key, endpoint, bucket_name):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.bucket_name = bucket_name

        auth = oss2.Auth(access_key, secret_key)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    def get_file_url(self, remote_path, expires=3600):
        """获取文件访问URL（自动判断Bucket类型）"""
        # 检查Bucket ACL
        acl = self.bucket.get_bucket_acl().acl

        if acl == oss2.BUCKET_ACL_PUBLIC_READ:
            # 公共读Bucket，直接返回公开URL
            return self._get_public_url(remote_path)
        else:
            # 私有Bucket，返回签名URL
            return self._get_signed_url(remote_path, expires)

    def _get_public_url(self, object_name):
        """生成公开访问URL"""
        # 处理endpoint格式
        endpoint = self.endpoint.replace('https://', '').replace('http://', '')
        return f"https://{self.bucket_name}.{endpoint}/{object_name}"

    def _get_signed_url(self, object_name, expires=3600):
        """生成带签名的临时访问URL"""
        return self.bucket.sign_url('GET', object_name, expires)

    def upload(self, local_path, remote_path):
        try:
            res = self.bucket.put_object_from_file(remote_path, local_path)
            if res.status == 200:
                # 获取访问URL
                return self.get_file_url(remote_path)
        except Exception as e:
            print(f"OSS upload failed: {str(e)}")

    def download(self, remote_path, local_path):
        try:
            res = self.bucket.get_object_to_file(remote_path, local_path)
            if res.status == 200:
                return True
        except Exception as e:
            print(f"OSS download failed: {str(e)}")

    def exists(self, remote_path):
        return self.bucket.object_exists(remote_path)

    def delete(self, remote_path):
        try:
            res = self.bucket.delete_object(remote_path)
            if res.status == 204:
                return True
        except Exception as e:
            print(f"OSS delete failed: {str(e)}")


class LocalStorageProvider(StorageProvider):

    """本地存储实现"""

    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def upload(self, local_path, remote_path):
        import shutil
        try:
            shutil.copy(local_path, f"{self.base_path}/{remote_path}")
            return True
        except Exception as e:
            print(f"Local storage upload failed: {str(e)}")
            return False



if  __name__ == '__main__':
    from config import config

    storage = OSSProvider(config.OSS_ACCESS_KEY, config.OSS_SECRET_KEY, config.OSS_ENDPOINT, config.OSS_BUCKET_NAME)
    # res = storage.upload(os.path.join(config.BASE_PATH, "resources/img/bg2.png"), "images/bg2.png")
    res = storage.delete("images/bg2.png")
    print(res)
    # storage.download("images/bg0.png", "test_download.txt")