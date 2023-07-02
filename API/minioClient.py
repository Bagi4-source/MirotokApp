from minio import Minio
import os


class MinioClient:
    def __init__(self):
        buckets = ["avatars", "results"]
        self.client = Minio(f'{os.getenv("MINIO_ROOT_HOST", "80.78.240.191")}:9000',
                            access_key=os.getenv("MINIO_ROOT_USER", "GermanAdmin"),
                            secret_key=os.getenv("MINIO_ROOT_PASSWORD", "German123Minio"),
                            secure=False)
        for bucket in buckets:
            try:
                self.client.make_bucket(bucket)
            except:
                pass
        try:
            self.save_image("avatars", "user.png", "./media/avatars/user.png")
        except:
            pass

    def get_url(self, bucket, file_name):
        try:
            self.client.get_object(
                bucket,
                file_name
            )
        except:
            return None

        try:
            return self.client.get_presigned_url(
                "GET",
                bucket,
                file_name
            )
        except:
            return None

    def save_image(self, bucket, file_name, file_path):
        try:
            self.client.fput_object(bucket, file_name, file_path, content_type='image/png')
        except:
            pass

    def save_image_bytes(self, bucket, file_name, data, length):
        self.client.put_object(bucket, file_name, data, length, content_type='image/png')
