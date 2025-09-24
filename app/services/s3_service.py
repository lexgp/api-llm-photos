import os

# import boto3
from boto3 import client as S3Client
from fastapi import HTTPException
from dotenv import load_dotenv
load_dotenv()

class S3Service:

    YANDEX_ACCESS_KEY_ID = os.getenv("YANDEX_ACCESS_KEY_ID")
    YANDEX_SECRET_ACCESS_KEY = os.getenv("YANDEX_SECRET_ACCESS_KEY")
    YANDEX_ENDPOINT = os.getenv("YANDEX_ENDPOINT")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    def __init__(self) -> None:
        self.s3_client = S3Client(
            's3',
            endpoint_url=S3Service.YANDEX_ENDPOINT,
            aws_access_key_id=S3Service.YANDEX_ACCESS_KEY_ID,
            aws_secret_access_key=S3Service.YANDEX_SECRET_ACCESS_KEY,
            region_name='ru-central1'
        )

    async def upload_file(self, file, object_name):
        try:
            # Загружаем файл в бакет
            self.s3_client.upload_fileobj(file, S3Service.BUCKET_NAME, object_name)
            presigned_url = self.get_presigned_url(object_name)
            return presigned_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")

    def get_presigned_url(self, object_name):
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3Service.BUCKET_NAME, 'Key': object_name},
            ExpiresIn=3600
        )
