import os
import uuid
import json
import firebase_admin
from firebase_admin import credentials, storage
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Firebase Admin инициализация
# Приоритет: 1) FIREBASE_SERVICE_ACCOUNT_JSON env var (продакшн)
#            2) service_account.json файл (локальная разработка)
# ─────────────────────────────────────────────────────────────
STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "sjk-smartview.firebasestorage.app")

def _init_firebase():
    if firebase_admin._apps:
        return  # Already initialized

    # Вариант 0: путь к файлу через env var (Docker-friendly)
    cred_from_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
    if cred_from_path and os.path.exists(cred_from_path):
        try:
            cred = credentials.Certificate(cred_from_path)
            firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})
            print(f"Firebase Admin: initialized via FIREBASE_CREDENTIAL_PATH ({cred_from_path})")
            return
        except Exception as e:
            print(f"Firebase Admin: FIREBASE_CREDENTIAL_PATH error: {e}")

    # Вариант 1: JSON через переменную окружения (Railway, Vercel, etc.)
    sa_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            sa_dict = json.loads(sa_json)
            cred = credentials.Certificate(sa_dict)
            firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})
            print("Firebase Admin: initialized via FIREBASE_SERVICE_ACCOUNT_JSON env var.")
            return
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Firebase Admin: FIREBASE_SERVICE_ACCOUNT_JSON parse error: {e}")

    # Вариант 2: файл рядом с модулем (fallback для локальной разработки)
    cred_path = os.path.join(os.path.dirname(__file__), "service_account.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {"storageBucket": STORAGE_BUCKET})
        print("Firebase Admin: initialized via service_account.json file (local dev).")
        return

    # Вариант 3: Application Default Credentials (GCP managed environments)
    try:
        firebase_admin.initialize_app(options={"storageBucket": STORAGE_BUCKET})
        print("Firebase Admin: initialized via Application Default Credentials.")
    except Exception as e:
        print(f"Firebase Admin: initialization failed: {e}")


_init_firebase()

# ─────────────────────────────────────────────────────────────
# Локальная папка для fallback хранения
# ─────────────────────────────────────────────────────────────
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class StorageService:
    def __init__(self):
        try:
            self.bucket = storage.bucket()
            self.use_cloud = True
            print(f"StorageService: Firebase Storage ready (bucket: {STORAGE_BUCKET})")
        except Exception as e:
            print(f"StorageService: Firebase Storage unavailable → local fallback. Error: {e}")
            self.use_cloud = False
            self.bucket = None

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = "image/jpeg",
        folder: str = "uploads"
    ) -> str:
        """
        Загружает файл в Firebase Storage (или локально как fallback).
        Возвращает публичный URL.
        """
        ext = os.path.splitext(filename)[1] or ".jpg"
        unique_filename = f"{folder}/{uuid.uuid4()}{ext}"

        if self.use_cloud and self.bucket:
            try:
                blob = self.bucket.blob(unique_filename)
                blob.upload_from_string(file_content, content_type=content_type)
                blob.make_public()
                return blob.public_url
            except Exception as e:
                print(f"StorageService: Cloud upload failed → local fallback. Error: {e}")

        # Локальное хранение (Fallback)
        local_filename = f"{uuid.uuid4()}{ext}"
        local_path = UPLOAD_DIR / local_filename
        with open(local_path, "wb") as f:
            f.write(file_content)

        return f"/uploads/{local_filename}"


storage_service = StorageService()
