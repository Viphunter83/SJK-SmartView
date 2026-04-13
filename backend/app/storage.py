import os
import boto3
import uuid
from botocore.exceptions import NoCredentialsError
from pathlib import Path

# Конфигурация из окружения
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL") # Для работы с R2 / Supabase / Selectel

# Локальная папка для временного хранения / Fallback
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class StorageService:
    def __init__(self):
        self.use_s3 = all([S3_BUCKET, AWS_ACCESS_KEY, AWS_SECRET_KEY])
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                endpoint_url=S3_ENDPOINT
            )
            print(f"StorageService: Initialized with S3 (Bucket: {S3_BUCKET})")
        else:
            print("StorageService: S3 credentials not found. Falling back to Local Storage.")

    async def upload_file(self, file_content: bytes, filename: str, content_type: str = "image/jpeg") -> str:
        """
        Загружает файл и возвращает публичный URL.
        """
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"
        
        if self.use_s3:
            try:
                self.s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=unique_filename,
                    Body=file_content,
                    ContentType=content_type,
                    ACL='public-read' # Или 'private' в зависимости от настроек бакета
                )
                
                # Генерация URL
                if S3_ENDPOINT:
                    return f"{S3_ENDPOINT}/{S3_BUCKET}/{unique_filename}"
                return f"https://{S3_BUCKET}.s3.amazonaws.com/{unique_filename}"
            except Exception as e:
                print(f"S3 Upload failed: {e}. Falling back to local.")
                # Продолжаем как локальное хранилище в случае ошибки
        
        # Локальное хранение (Fallback)
        local_path = UPLOAD_DIR / unique_filename
        with open(local_path, "wb") as f:
            f.write(file_content)
        
        # Для локального запуска возвращаем путь (в проде здесь должен быть URL медиа-сервера)
        return f"/uploads/{unique_filename}"

storage_service = StorageService()
